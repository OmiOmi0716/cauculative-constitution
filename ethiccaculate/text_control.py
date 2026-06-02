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

NLI-like claim analysis:
  Identifies assertions, their evidence support, and logical structure.
  Provides claim_support_ratio used by the Honesty axis correction.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from math import log

from .models import ControlState


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
    "as a result", "due to", "owing to", "given that", "so", "hence",
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
    """Split text into sentences using punctuation boundaries."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _tokenize(text: str) -> list[str]:
    return re.sub(r"[^\w\s]", " ", text.lower()).split()


def _contains_any(tokens: list[str], word_set: frozenset[str], window: int = 0) -> int:
    """Count how many tokens (or bigrams for window=1) appear in word_set."""
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
# Per-axis estimators
# ---------------------------------------------------------------------------

def _clamp(v: float, lo: float = 0.05, hi: float = 0.95) -> float:
    return max(lo, min(hi, v))


def _estimate_C(tokens: list[str], claims: ClaimAnalysis) -> float:
    """
    C = Causal consistency axis  [want low, pass threshold <= 0.35]

    High C: many contradictions, logical gaps
    Low C:  consistent reasoning, explicit causals
    """
    n_sent = claims.sentence_count
    contra_density = claims.contradiction_count / n_sent
    causal_density = claims.logical_count / n_sent
    return _clamp(0.25 + 0.45 * contra_density - 0.15 * causal_density)


def _estimate_S(tokens: list[str], claims: ClaimAnalysis) -> float:
    """
    S = Stability axis  [want low, pass threshold <= 0.35]

    High S: hedged, topic-diverse, uncertain text
    Low S:  focused, direct statements
    """
    n = max(len(tokens), 1)
    n_sent = claims.sentence_count
    hedge_density = _contains_any(tokens, _HEDGE) / n_sent
    question_density = claims.question_count / n_sent
    return _clamp(0.18 + 0.45 * hedge_density + 0.20 * question_density)


def _estimate_X(tokens: list[str], claims: ClaimAnalysis) -> float:
    """
    X = External event rate  [want low, pass threshold <= 0.50]

    High X: many external references, URLs, citations
    Low X:  self-contained text
    """
    n_sent = claims.sentence_count
    ext_density = _contains_any(tokens, _EXTERNAL_REF, window=1) / n_sent
    return _clamp(0.10 + 0.50 * ext_density)


def _estimate_P(tokens: list[str], claims: ClaimAnalysis) -> float:
    """
    P = Pressure / urgency axis  [want low, pass threshold <= 0.50]

    High P: urgency words, time pressure
    Low P:  measured, considered tone
    """
    n_sent = claims.sentence_count
    urgency_density = _contains_any(tokens, _URGENCY) / n_sent
    exclamation_density = sum(1 for t in tokens if t == "!") / n_sent
    return _clamp(0.12 + 0.60 * urgency_density + 0.20 * exclamation_density)


def _estimate_tau(tokens: list[str], claims: ClaimAnalysis) -> float:
    """
    tau = Task progress  [want high, pass threshold >= 0.60]

    High tau: text completes stated purpose, has closure
    Low tau:  many open questions, incomplete
    """
    n_sent = claims.sentence_count
    closure_density = _contains_any(tokens, _CLOSURE, window=1) / n_sent
    question_density = claims.question_count / n_sent
    logical_density = claims.logical_count / n_sent
    return _clamp(0.60 + 0.25 * closure_density + 0.10 * logical_density - 0.25 * question_density)


def _estimate_M(tokens: list[str], claims: ClaimAnalysis) -> float:
    """
    M = Memory coherence  [want high, pass threshold >= 0.55]

    High M: good internal references, coherent pronouns, no topic fragmentation
    Low M:  disconnected, repetitive without reference
    """
    n_sent = claims.sentence_count
    cohesive_density = _contains_any(tokens, _PRONOUNS_COHESIVE) / n_sent
    causal_density = claims.logical_count / n_sent
    return _clamp(0.65 + 0.15 * cohesive_density + 0.10 * causal_density)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@dataclass
class TextControlResult:
    """Full diagnostic output of text control estimation."""
    control: ControlState
    claims: ClaimAnalysis
    write_gate_feasible: bool   # True if all axes can satisfy write_gate thresholds

    def format_axes(self) -> str:
        c = self.control
        lines = [
            f"  C (consistency) : {c.C:.4f}  {'<= 0.35 OK' if c.C <= 0.35 else '> 0.35 FAIL'}",
            f"  S (stability)   : {c.S:.4f}  {'<= 0.35 OK' if c.S <= 0.35 else '> 0.35 FAIL'}",
            f"  X (external)    : {c.X:.4f}  {'<= 0.50 OK' if c.X <= 0.50 else '> 0.50 FAIL'}",
            f"  P (pressure)    : {c.P:.4f}  {'<= 0.50 OK' if c.P <= 0.50 else '> 0.50 FAIL'}",
            f"  tau (progress)  : {c.tau:.4f}  {'>= 0.60 OK' if c.tau >= 0.60 else '< 0.60 FAIL'}",
            f"  M (coherence)   : {c.M:.4f}  {'>= 0.55 OK' if c.M >= 0.55 else '< 0.55 FAIL'}",
        ]
        return "\n".join(lines)


def estimate_control_from_text(text: str) -> TextControlResult:
    """
    Estimate all 6 ControlState axes from text linguistic features.

    This replaces fallback_control_from_spectral() for text-based evaluation,
    making write_gate meaningful without vLLM telemetry.

    Args:
        text: Raw text to analyze

    Returns:
        TextControlResult with ControlState and full ClaimAnalysis
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

    # Check against write_gate thresholds (GateThresholds defaults)
    feasible = (
        control.C <= 0.35
        and control.S <= 0.35
        and control.X <= 0.50
        and control.P <= 0.50
        and control.tau >= 0.60
        and control.M >= 0.55
    )

    return TextControlResult(control=control, claims=claims, write_gate_feasible=feasible)
