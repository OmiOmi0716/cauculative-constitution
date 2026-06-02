"""
Text-derived control axis estimation.

Replaces fallback_control_from_spectral() for text-based ethics evaluation.
Estimates all 6 axes (C, S, X, P, tau, M) purely from linguistic features
so that write_gate is meaningful without external vLLM telemetry.

Axis semantics (want low for C/S/X/P, want high for tau/M):
  C   Causal consistency   [<= 0.35 to pass write_gate]
  S   Stability            [<= 0.35 to pass write_gate]
  X   External events      [<= 0.50 to pass write_gate]
  P   Pressure / urgency   [<= 0.50 to pass write_gate]
  tau Task progress        [>= 0.60 to pass write_gate]
  M   Memory / coherence   [>= 0.55 to pass write_gate]

Formal spec alignment (v2.5-formal-safety):
  D_C = alpha*leak + beta*(1-SC)               §9.1 Causal axis
  D_S = w1*entropy_risk + w2*answer_var + w3*instability   §9.2 S-lite
  d_tau = N_remain + lambda_tau*N_stall        §9.6 tau axis
  tau_mix = q_t * tau_score                    §9.6 quality gate
  score_a = max(0, 1 - d_a/(kappa_a+1))       §13  monitoring
  H_eps   = exp(sum w_a*log(score_a+eps))-eps  §13  health

NLI-like claim analysis:
  Identifies assertions, their evidence support, and logical structure.
  Provides claim_support_ratio used by the Causal axis correction.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from math import ceil, exp, log as _log

from .models import ControlState


# ---------------------------------------------------------------------------
# Formal spec: M state machine (v2.5 §9.5)
# ---------------------------------------------------------------------------

class MemoryState(Enum):
    """
    Memory axis state machine from v2.5 §9.5.

    Transitions:
      transient        -> commit_candidate
      commit_candidate -> committed | rejected | conflict
      conflict         -> rejected
                       -> commit_candidate  (only when conflict resolved by verified evidence)
      committed        -> recalled -> committed
      rejected is terminal
    """
    transient = "transient"
    commit_candidate = "commit_candidate"
    committed = "committed"
    recalled = "recalled"
    rejected = "rejected"
    conflict = "conflict"


# ---------------------------------------------------------------------------
# Formal spec: axis health scoring (v2.5 §13)
# ---------------------------------------------------------------------------

def score_a(d_a: float, kappa_a: int) -> float:
    """
    Axis health score from defect value.  (v2.5 §13)

      score_a = max(0, 1 - toNat(d_a) / (kappa_a + 1))

    Properties:
      d_a = 0          -> 1.0  (no defect)
      d_a = kappa_a    -> 1/(kappa_a+1)  (at threshold)
      d_a > kappa_a    -> 0    (outside acceptable domain)
    """
    return max(0.0, 1.0 - d_a / (kappa_a + 1))


def health_score_epsilon(
    scores: dict[str, float],
    weights: dict[str, float] | None = None,
    epsilon: float = 1e-6,
) -> float:
    """
    Epsilon-geometric-mean health monitoring indicator.  (v2.5 §13)

      H_eps = exp( sum_{a in A} w_a * log(score_a + eps) ) - eps

    Properties:
      all scores = 1  ->  H_eps ≈ 1
      any score  = 0  ->  H_eps = 0
      H_eps in [0, 1]

    Args:
        scores:  per-axis scores in [0, 1]
        weights: per-axis weights (uniform if None); must be non-negative
        epsilon: numerical stability floor (default 1e-6)
    """
    if not scores:
        return 0.0
    n = len(scores)
    total_w = sum(weights.values()) if weights else float(n)
    if total_w <= 0.0:
        return 0.0
    log_sum = sum(
        ((weights or {}).get(a, 1.0) / total_w) * _log(max(0.0, scores[a]) + epsilon)
        for a in scores
    )
    return max(0.0, min(1.0, exp(log_sum) - epsilon))


# ---------------------------------------------------------------------------
# Linguistic feature sets
# ---------------------------------------------------------------------------

_CONTRADICTION = frozenset({
    "but", "however", "although", "despite", "whereas", "yet",
    "nevertheless", "nonetheless", "contrary", "conversely",
    "on the other hand", "even though", "while",
})

_CAUSAL = frozenset({
    "because", "therefore", "thus", "hence", "since", "consequently",
    "as a result", "due to", "owing to", "given that", "so",
    "which means", "it follows", "accordingly", "for this reason",
})

_HEDGE = frozenset({
    "maybe", "perhaps", "might", "could", "possibly", "seems",
    "appears", "likely", "probably", "generally", "usually", "often",
    "sometimes", "somewhat", "relatively", "arguably", "presumably",
    "conceivably", "tentatively",
})

_URGENCY = frozenset({
    "immediately", "urgently", "urgent", "asap", "emergency",
    "right now", "at once", "without delay", "critical", "deadline",
    "by tomorrow", "time-sensitive", "pressing", "instantaneously",
})

_EXTERNAL_REF = frozenset({
    "see", "refer", "check", "citation", "cite", "reference",
    "url", "http", "www", "according to", "source", "as reported",
    "from the study", "per the report",
})

_PRONOUNS_COHESIVE = frozenset({
    "it", "they", "their", "this", "that", "these", "those",
    "its", "them", "which", "who", "whose",
})

_CLOSURE = frozenset({
    "therefore", "thus", "hence", "in conclusion", "finally",
    "as a result", "to summarize", "in summary", "overall",
    "ultimately", "to conclude", "in short", "in brief",
    "to sum up", "all in all",
})

_EVIDENCE_CONNECTORS = frozenset({
    "because", "since", "as", "given that", "due to", "owing to",
    "based on", "according to", "the data show", "studies indicate",
    "evidence suggests", "research shows", "proven by",
})

_CONFIDENCE_MARKERS = frozenset({
    "certainly", "definitely", "absolutely", "clearly", "obviously",
    "undoubtedly", "guaranteed", "certain", "sure", "without doubt",
    "100%", "always", "never",
})


# ---------------------------------------------------------------------------
# Sentence splitting and basic structure
# ---------------------------------------------------------------------------

def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _tokenize(text: str) -> list[str]:
    return re.sub(r"[^\w\s]", " ", text.lower()).split()


def _contains_any(tokens: list[str], word_set: frozenset[str], window: int = 0) -> int:
    """Count tokens (or bigrams for window=1) appearing in word_set."""
    count = 0
    for i, t in enumerate(tokens):
        if t in word_set:
            count += 1
            continue
        if window >= 1 and i + 1 < len(tokens):
            bigram = t + " " + tokens[i + 1]
            if bigram in word_set:
                count += 1
    return count


# ---------------------------------------------------------------------------
# NLI-style claim analysis
# ---------------------------------------------------------------------------

@dataclass
class ClaimAnalysis:
    """
    Lightweight NLI approximation from sentence structure.

    Approximates entailment/evidence relationships without an ML model by
    detecting explicit linguistic connectives.
    """
    sentence_count: int
    assertion_count: int          # declarative sentences (end with '.')
    question_count: int           # unresolved questions
    evidenced_count: int          # assertions containing evidence connectors
    confident_count: int          # assertions with confidence markers
    logical_count: int            # sentences with explicit causal connectors
    contradiction_count: int      # sentences with contrastive connectors

    # Derived ratios
    claim_support_ratio: float    # evidenced / max(confident, 1)  in [0,1]
    logical_structure_score: float  # logical / sentences  in [0,1]
    consistency_score: float      # 1 - contradiction_density  in [0,1]


def analyze_claims(text: str) -> ClaimAnalysis:
    """
    Estimate claim structure and logical support from text.

    Treats each sentence as a unit and checks for:
      - Explicit evidence connectors → evidenced_count
      - Confidence markers → confident_count
      - Causal connectors → logical_count
      - Contradiction markers → contradiction_count
    """
    sentences = _split_sentences(text)
    n = max(len(sentences), 1)

    assertions = sum(1 for s in sentences if s.endswith(".") and not s.endswith(".."))
    questions = sum(1 for s in sentences if s.endswith("?"))

    evidenced = 0
    confident = 0
    logical = 0
    contradictions = 0

    for sentence in sentences:
        tokens = _tokenize(sentence)
        has_evidence = _contains_any(tokens, _EVIDENCE_CONNECTORS, window=1) > 0
        has_confidence = _contains_any(tokens, _CONFIDENCE_MARKERS) > 0
        has_causal = _contains_any(tokens, _CAUSAL, window=1) > 0
        has_contra = _contains_any(tokens, _CONTRADICTION) > 0

        if has_evidence:
            evidenced += 1
        if has_confidence:
            confident += 1
        if has_causal:
            logical += 1
        if has_contra:
            contradictions += 1

    claim_support = evidenced / max(confident, 1) if confident > 0 else (1.0 if evidenced == 0 else 0.5)
    claim_support = min(1.0, claim_support)

    return ClaimAnalysis(
        sentence_count=n,
        assertion_count=assertions,
        question_count=questions,
        evidenced_count=evidenced,
        confident_count=confident,
        logical_count=logical,
        contradiction_count=contradictions,
        claim_support_ratio=claim_support,
        logical_structure_score=min(1.0, logical / n),
        consistency_score=max(0.0, 1.0 - contradictions / n),
    )


# ---------------------------------------------------------------------------
# Per-axis estimators — aligned with formal D_a risk functions (v2.5 §9)
# ---------------------------------------------------------------------------

def _clamp(v: float, lo: float = 0.05, hi: float = 0.95) -> float:
    return max(lo, min(hi, v))


def _estimate_C(tokens: list[str], claims: ClaimAnalysis) -> float:
    """
    D_C = alpha*leak + beta*(1-SC)       (v2.5 §9.1)

    Text proxies:
      leak(x)  ← contradiction density (causal inconsistency signal)
      SC(x)    ← claim_support_ratio (evidenced / confident assertions)

    SC = 0 when confident assertions exist but none are evidenced.
    No assertions at all → SC = 1 (trivially consistent, no claims to check).
    """
    n = claims.sentence_count
    contra_density = claims.contradiction_count / n   # leak proxy
    SC = claims.claim_support_ratio
    if claims.confident_count == 0 and claims.evidenced_count == 0:
        SC = 1.0  # no assertions → no inconsistency to detect
    alpha, beta = 0.35, 0.50
    D_C = alpha * contra_density + beta * (1.0 - SC)
    return _clamp(D_C)


def _estimate_S(tokens: list[str], claims: ClaimAnalysis) -> float:
    """
    S-lite: D_S = w1*entropy_risk + w2*answer_variance + w3*retry_instability
                                                         (v2.5 §9.2)

    Text proxies:
      entropy_risk     ← hedge token density (scaled per sentence)
      answer_variance  ← question density (unresolved = distributional spread)
      retry_instability ← contradiction density (topic/stance reversals)
    """
    n = claims.sentence_count
    hedge_count = _contains_any(tokens, _HEDGE)
    hedge_per_sent = hedge_count / n
    # Hedging is a soft stability signal: scale so ~2 hedges/sentence ≈ risk=1
    entropy_risk = min(1.0, hedge_per_sent * 0.5)
    answer_variance = claims.question_count / n
    retry_instability = min(1.0, (claims.contradiction_count / n) * 2.0)
    w1, w2, w3 = 0.40, 0.30, 0.30
    D_S = w1 * entropy_risk + w2 * answer_variance + w3 * retry_instability
    return _clamp(D_S)


def _estimate_X(tokens: list[str], claims: ClaimAnalysis) -> float:
    """
    X = External event rate  [want low, pass threshold <= 0.50]

    High X: many external references, URLs, citations
    """
    n_sent = claims.sentence_count
    ext_density = _contains_any(tokens, _EXTERNAL_REF, window=1) / n_sent
    return _clamp(0.10 + 0.50 * ext_density)


def _estimate_P(tokens: list[str], claims: ClaimAnalysis) -> float:
    """
    P = Pressure / urgency axis  [want low, pass threshold <= 0.50]

    High P: urgency words, time pressure
    """
    n_sent = claims.sentence_count
    urgency_density = _contains_any(tokens, _URGENCY) / n_sent
    exclamation_density = sum(1 for t in tokens if t == "!") / n_sent
    return _clamp(0.12 + 0.60 * urgency_density + 0.20 * exclamation_density)


def _estimate_tau(tokens: list[str], claims: ClaimAnalysis) -> float:
    """
    d_tau = N_remain + lambda_tau * N_stall       (v2.5 §9.6)
    tau_score = max(0, 1 - d_tau / (kappa_tau+1)) (score_a formula)
    tau_mix   = q_t * tau_score + closure_bonus   (quality gate)

    Text proxies:
      N_remain ← question_count (unresolved questions = remaining work)
      N_stall  ← max(0, question_count - logical_count) (questions
                 without causal resolution = stall windows)
      q_t      ← logical_structure_score * consistency_score
                 (quality gate: text is both structured and consistent)
    """
    n = claims.sentence_count
    lambda_tau = 2.0      # stall penalty multiplier (v2.5 requires > 0)
    kappa_tau = 4         # acceptable defect threshold
    N_remain = claims.question_count
    N_stall = max(0, claims.question_count - claims.logical_count)
    d_tau = N_remain + lambda_tau * N_stall
    tau_score = max(0.0, 1.0 - d_tau / (kappa_tau + 1))
    # Quality gate: well-structured + consistent text earns higher tau
    q_t = claims.logical_structure_score * claims.consistency_score
    # tau_mix = quality-gated score + closure bonus
    closure_count = _contains_any(tokens, _CLOSURE, window=1)
    closure_density = closure_count / n
    tau_mix = (0.70 + 0.30 * q_t) * tau_score + 0.15 * closure_density
    return _clamp(tau_mix)


def _estimate_M(tokens: list[str], claims: ClaimAnalysis) -> float:
    """
    M = Memory coherence  [want high, pass threshold >= 0.55]

    D_M proxy: contradiction_count drives memory conflict risk.
    High M: good internal references, coherent pronouns, no conflicts.

    Maps to MemoryState via:
      M >= 0.80  →  committed / recalled
      M >= 0.55  →  commit_candidate
      M < 0.55   →  transient / conflict
    """
    n = claims.sentence_count
    cohesive_density = _contains_any(tokens, _PRONOUNS_COHESIVE) / n
    causal_density = claims.logical_count / n
    # Conflict penalty from contradiction count (d_M = w3*N_memory_conflict proxy)
    conflict_penalty = min(0.30, (claims.contradiction_count / n) * 0.30)
    return _clamp(0.65 + 0.15 * cohesive_density + 0.10 * causal_density - conflict_penalty)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@dataclass
class TextControlResult:
    """Full diagnostic output of text control estimation."""
    control: ControlState
    claims: ClaimAnalysis
    write_gate_feasible: bool   # True if all axes satisfy write_gate thresholds
    health_score: float = 0.0  # H_epsilon monitoring metric (v2.5 §13)

    def format_axes(self) -> str:
        c = self.control
        lines = [
            f"  C (consistency) : {c.C:.4f}  {'<= 0.35 OK' if c.C <= 0.35 else '> 0.35 FAIL'}",
            f"  S (stability)   : {c.S:.4f}  {'<= 0.35 OK' if c.S <= 0.35 else '> 0.35 FAIL'}",
            f"  X (external)    : {c.X:.4f}  {'<= 0.50 OK' if c.X <= 0.50 else '> 0.50 FAIL'}",
            f"  P (pressure)    : {c.P:.4f}  {'<= 0.50 OK' if c.P <= 0.50 else '> 0.50 FAIL'}",
            f"  tau (progress)  : {c.tau:.4f}  {'>= 0.60 OK' if c.tau >= 0.60 else '< 0.60 FAIL'}",
            f"  M (coherence)   : {c.M:.4f}  {'>= 0.55 OK' if c.M >= 0.55 else '< 0.55 FAIL'}",
            f"  health (H_eps)  : {self.health_score:.4f}",
        ]
        return "\n".join(lines)


def estimate_control_from_text(text: str) -> TextControlResult:
    """
    Estimate all 6 ControlState axes from text linguistic features.

    This replaces fallback_control_from_spectral() for text-based evaluation,
    making write_gate meaningful without vLLM telemetry.

    The axis estimators map formal D_a risk functions (v2.5 §9) to
    linguistic proxies extracted without an ML model.

    Args:
        text: Raw text to analyze

    Returns:
        TextControlResult with ControlState, ClaimAnalysis, and H_epsilon
        health score.
    """
    tokens = _tokenize(text)
    claims = analyze_claims(text)

    control = ControlState(
        C=_estimate_C(tokens, claims),
        S=_estimate_S(tokens, claims),
        X=_estimate_X(tokens, claims),
        P=_estimate_P(tokens, claims),
        tau=_estimate_tau(tokens, claims),
        M=_estimate_M(tokens, claims),
    )

    feasible = (
        control.C <= 0.35
        and control.S <= 0.35
        and control.X <= 0.50
        and control.P <= 0.50
        and control.tau >= 0.60
        and control.M >= 0.55
    )

    # Compute per-axis health scores normalised to write_gate thresholds.
    # For risk axes (C,S,X,P): score = max(0, 1 - value/threshold)
    # For progress axes (tau,M): score = min(1, (value - floor) / (1 - floor))
    axis_scores = {
        "C":   max(0.0, 1.0 - control.C / 0.35),
        "S":   max(0.0, 1.0 - control.S / 0.35),
        "X":   max(0.0, 1.0 - control.X / 0.50),
        "P":   max(0.0, 1.0 - control.P / 0.50),
        "tau": max(0.0, min(1.0, (control.tau - 0.30) / 0.70)),
        "M":   max(0.0, min(1.0, (control.M  - 0.30) / 0.70)),
    }
    h_score = health_score_epsilon(axis_scores)

    return TextControlResult(
        control=control,
        claims=claims,
        write_gate_feasible=feasible,
        health_score=h_score,
    )
