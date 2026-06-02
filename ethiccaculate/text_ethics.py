"""
Text-to-ethics conversion.

Heuristically extracts ethical signals from raw text and maps them to the
BCG (Boundary, Covenant, Grace) vector representation, then runs the full
ethics formula pipeline.

Signal extraction:
  - Boundary words   (must/forbidden/never ...)   -> B score
  - Covenant words   (principle/duty/universal ...) -> C score
  - Grace words      (help/care/compassion ...)   -> G score
  - Confidence words (certainly/definitely ...)   -> claimed_confidence
  - Evidence words   (research/data/cited ...)    -> evidence_coverage
  - Harm words       (dangerous/risk/illegal ...) -> harm score
  - Domain detection (medical/legal/financial)    -> sensitive_context

BCG profile construction (4 roles):
  G_up   (aspirational good)  : B+=0.1, C+=0.1, G+=0.1  [optimistic reading]
  G_down (grounded good)      : B=b, C=0.7*c+0.3*evidence, G=g  [evidence-anchored]
  H_up   (theoretical harm)   : B=harm*b+(1-harm)*0.3, C=0.5*c+0.5*harm, G=1-harm
  H_down (practical harm)     : B=harm, C=0.5*(1-confidence)+0.5*harm, G=1-0.7*harm
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .formula import FormulaPipelineResult, run_ethics_pipeline
from .models import BCGVector, DialogueEvent
from .principles import default_principles
from .spectral import ScalarizerConfig
from .decoder import DecoderConfig
from .audit import ObjectiveWeights
from .control import GateThresholds
from .text_control import ClaimAnalysis, TextControlResult, analyze_claims, estimate_control_from_text


# --- Keyword sets -----------------------------------------------------------

_BOUNDARY_HIGH = frozenset({
    "must", "shall", "required", "forbidden", "never", "always",
    "prohibited", "mandatory", "absolutely", "strictly", "cannot",
    "must not", "will not", "disallowed", "impermissible",
})
_BOUNDARY_LOW = frozenset({
    "maybe", "perhaps", "might", "could", "possibly", "generally",
    "usually", "often", "sometimes", "optionally", "allow", "allowed",
    "permissible", "flexible", "discretionary",
})
_COVENANT_HIGH = frozenset({
    "principle", "principles", "value", "values", "right", "rights",
    "duty", "duties", "obligation", "commitment", "standard", "universal",
    "consistent", "integrity", "moral", "ethical", "justice", "fairness",
    "virtue", "norm", "norms", "deontological", "rule",
})
_COVENANT_LOW = frozenset({
    "exception", "flexible", "contextual", "situational", "depends",
    "relative", "subjective", "pragmatic",
})
_GRACE_HIGH = frozenset({
    "help", "support", "care", "caring", "concern", "wellbeing", "welfare",
    "compassion", "compassionate", "kind", "kindness", "understand",
    "assist", "benefit", "improve", "protect", "safe", "safety",
    "empathy", "respect", "dignity", "heal", "nurture",
})
_GRACE_LOW = frozenset({
    "indifferent", "irrelevant", "disregard", "ignore", "unimportant",
    "dismiss", "unconcerned",
})
_CONFIDENCE_HIGH = frozenset({
    "certainly", "definitely", "absolutely", "clearly", "obviously",
    "proven", "certain", "sure", "undoubtedly", "confirmed", "established",
    "guaranteed", "without doubt", "100%",
})
_CONFIDENCE_LOW = frozenset({
    "maybe", "perhaps", "possibly", "uncertain", "unclear", "might",
    "approximately", "roughly", "unsure", "questionable", "tentative",
    "probably", "likely",
})
_EVIDENCE_HIGH = frozenset({
    "research", "study", "studies", "data", "evidence", "source", "cited",
    "documented", "statistics", "analysis", "report", "according",
    "demonstrated", "proven", "published", "peer", "reviewed", "meta",
    "trial", "experiment",
})
_EVIDENCE_LOW = frozenset({
    "think", "believe", "seems", "feel", "opinion", "guess", "anecdotally",
    "reportedly", "allegedly", "supposedly", "hearsay", "rumor",
})
_HARM_WORDS = frozenset({
    "dangerous", "harmful", "harm", "hurt", "damage", "injure", "kill",
    "illegal", "crisis", "emergency", "fatal", "toxic", "risk", "risky",
    "hazardous", "lethal", "deadly", "abuse", "violence", "threat",
    "exploit", "manipulate",
})
_DOMAIN_MEDICAL = frozenset({
    "medical", "medicine", "drug", "drugs", "dose", "dosage", "disease",
    "symptom", "diagnosis", "treatment", "prescription", "doctor", "patient",
    "clinical", "therapy", "medication", "surgery", "hospital",
    "ibuprofen", "aspirin", "paracetamol", "acetaminophen", "antibiotic",
    "vaccine", "insulin", "chemotherapy", "overdose", "supplement",
})
_DOMAIN_LEGAL = frozenset({
    "law", "legal", "illegal", "crime", "court", "attorney", "lawyer",
    "lawsuit", "criminal", "offense", "statute", "regulation", "liability",
    "contract", "rights",
})
_DOMAIN_FINANCIAL = frozenset({
    "invest", "investment", "stock", "financial", "loan", "debt",
    "fund", "portfolio", "securities", "trading", "market", "revenue",
    "profit", "loss", "bankruptcy",
})


# --- Signal extraction -------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    return re.sub(r"[^\w\s]", " ", text.lower()).split()


_NEGATION_TOKENS = frozenset({"no", "not", "without", "lack", "lacking", "lacks", "absent", "never", "neither"})


def _signal_score(
    tokens: list[str],
    high_set: frozenset[str],
    low_set: frozenset[str],
    base: float = 0.5,
) -> float:
    """
    Compute a [0, 1] score from keyword frequencies relative to text length.

    Negation detection: if a negation token (no/not/without/...) appears within
    2 positions before a high-signal word, that word counts as a low-signal hit
    instead, and vice versa.
    """
    n = max(len(tokens), 1)
    h = 0
    low = 0
    for index, token in enumerate(tokens):
        window = tokens[max(0, index - 2): index]
        negated = any(t in _NEGATION_TOKENS for t in window)
        if token in high_set:
            if negated:
                low += 1
            else:
                h += 1
        elif token in low_set:
            if negated:
                h += 1
            else:
                low += 1
    delta = 3.0 * (h - low) / n
    return max(0.05, min(0.95, base + delta))


# --- Data classes ------------------------------------------------------------

@dataclass
class TextAnalysis:
    """Ethical signals and control axes extracted from raw text."""
    text: str
    token_count: int
    boundary: float         # [0,1] ethical limit-setting strength
    covenant: float         # [0,1] principled consistency
    grace: float            # [0,1] compassionate consideration
    confidence: float       # [0,1] claimed certainty
    evidence: float         # [0,1] evidence quality
    harm: float             # [0,1] harm/risk presence
    domain: str             # "medical" | "legal" | "financial" | "general"
    sensitive_context: bool
    control_result: TextControlResult | None = None   # text-derived 6-axis control

    def format_signals(self) -> str:
        def bar(v: float, width: int = 10) -> str:
            filled = round(v * width)
            return "#" * filled + "." * (width - filled)

        lines = [
            f"  Domain    : {self.domain}",
            f"  Sensitive : {'Yes' if self.sensitive_context else 'No'}",
            f"  Boundary  : {self.boundary:.2f}  [{bar(self.boundary)}]  ethical limits",
            f"  Covenant  : {self.covenant:.2f}  [{bar(self.covenant)}]  principled",
            f"  Grace     : {self.grace:.2f}  [{bar(self.grace)}]  compassionate",
            f"  Confidence: {self.confidence:.2f}  [{bar(self.confidence)}]  claimed certainty",
            f"  Evidence  : {self.evidence:.2f}  [{bar(self.evidence)}]  evidence quality",
            f"  Harm      : {self.harm:.2f}  [{bar(self.harm)}]  risk presence",
        ]
        if self.control_result is not None:
            lines.append("")
            lines.append("  Control Axes (text-derived, no vLLM needed):")
            lines.append(self.control_result.format_axes())
        return "\n".join(lines)


@dataclass
class QuickEthicsReport:
    """Full ethics report derived from raw text."""
    input_text: str
    analysis: TextAnalysis
    bcg_profile: dict[str, BCGVector]
    pipeline: FormulaPipelineResult

    def format_report(self) -> str:
        bar = "-" * 62
        preview = self.input_text[:80] + ("..." if len(self.input_text) > 80 else "")
        verdict_label = {
            "pass": "PASS  - Ethical alignment satisfactory",
            "warn": "WARN  - Potential ethical concern",
            "fail": "FAIL  - Ethical violation detected",
        }.get(self.pipeline.verdict, self.pipeline.verdict.upper())

        lines = [
            bar,
            " QUICK ETHICS AUDIT REPORT",
            bar,
            f' Input: "{preview}"',
            "",
            " TEXT ANALYSIS (heuristic signal extraction)",
            self.analysis.format_signals(),
            "",
            " BCG PROFILE  (B=Boundary, C=Covenant, G=Grace)",
        ]
        for role, bcg in self.bcg_profile.items():
            lines.append(f"   {role:<8}  B={bcg.B:.3f}  C={bcg.C:.3f}  G={bcg.G:.3f}")
        # Claim analysis (NLI-style)
        cr = self.analysis.control_result
        if cr is not None:
            ca = cr.claims
            lines += [
                "",
                " CLAIM ANALYSIS (NLI-style, rule-based)",
                f"   Sentences: {ca.sentence_count}  Assertions: {ca.assertion_count}  Questions: {ca.question_count}",
                f"   Evidenced: {ca.evidenced_count}/{max(ca.confident_count,1)} confident claims "
                f"(support ratio={ca.claim_support_ratio:.2f})",
                f"   Logical structure: {ca.logical_structure_score:.2f}  Consistency: {ca.consistency_score:.2f}",
            ]

        lines += [
            "",
            " FORMULA PIPELINE",
            f"   Ebase={self.pipeline.Ebase:.4f}  Esyn={self.pipeline.Esyn:.4f}  Ecosyn={self.pipeline.Ecosyn:.4f}",
            f"   c0={self.pipeline.c0:+.4f}  c_gh={self.pipeline.c_gh:+.4f}  c_ud={self.pipeline.c_ud:+.4f}  c_cross={self.pipeline.c_cross:+.4f}",
            f"   U={self.pipeline.U:+.4f}   Objective J={self.pipeline.objective:+.4f}",
            "",
            f" VERDICT: {verdict_label}",
        ]
        if self.pipeline.violation_names:
            for name in self.pipeline.violation_names:
                tag = " [HARD CONSTRAINT]" if name in self.pipeline.hard_violations else " [soft]"
                lines.append(f"   VIOLATION: {name}{tag}")
        lines += [
            "",
            f" Gates: write={self.pipeline.write_gate}  "
            f"deepen={self.pipeline.deepen_gate}  stop={self.pipeline.stop_gate}",
            bar,
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "input_text": self.input_text,
            "analysis": {
                "domain": self.analysis.domain,
                "sensitive_context": self.analysis.sensitive_context,
                "boundary": self.analysis.boundary,
                "covenant": self.analysis.covenant,
                "grace": self.analysis.grace,
                "confidence": self.analysis.confidence,
                "evidence": self.analysis.evidence,
                "harm": self.analysis.harm,
            },
            "bcg_profile": {
                role: {"B": bcg.B, "C": bcg.C, "G": bcg.G}
                for role, bcg in self.bcg_profile.items()
            },
            "pipeline": self.pipeline.to_dict(),
        }


# --- Core functions ----------------------------------------------------------

def analyze_text(text: str) -> TextAnalysis:
    """
    Extract ethical signals and text-derived control axes from text.

    Combines:
      - Keyword-level BCG signal extraction (with negation detection)
      - Sentence-level control axis estimation (replaces vLLM telemetry fallback)
      - NLI-style claim support analysis
    """
    tokens = _tokenize(text)
    n = max(len(tokens), 1)

    boundary = _signal_score(tokens, _BOUNDARY_HIGH, _BOUNDARY_LOW)
    covenant = _signal_score(tokens, _COVENANT_HIGH, _COVENANT_LOW)
    grace = _signal_score(tokens, _GRACE_HIGH, _GRACE_LOW)
    confidence = _signal_score(tokens, _CONFIDENCE_HIGH, _CONFIDENCE_LOW)
    # Default base 0.35: absence of evidence words → below Honesty threshold (0.40)
    evidence = _signal_score(tokens, _EVIDENCE_HIGH, _EVIDENCE_LOW, base=0.35)
    harm = _signal_score(tokens, _HARM_WORDS, frozenset(), base=0.10)

    medical_count = sum(1 for t in tokens if t in _DOMAIN_MEDICAL)
    legal_count = sum(1 for t in tokens if t in _DOMAIN_LEGAL)
    financial_count = sum(1 for t in tokens if t in _DOMAIN_FINANCIAL)

    max_domain = max(medical_count, legal_count, financial_count)
    if max_domain == 0:
        domain = "general"
    elif medical_count == max_domain:
        domain = "medical"
    elif legal_count == max_domain:
        domain = "legal"
    else:
        domain = "financial"

    sensitive_context = (domain != "general") or (harm > 0.35)

    # Compute text-derived control axes (replaces fallback_control_from_spectral)
    control_result = estimate_control_from_text(text)

    return TextAnalysis(
        text=text,
        token_count=n,
        boundary=boundary,
        covenant=covenant,
        grace=grace,
        confidence=confidence,
        evidence=evidence,
        harm=harm,
        domain=domain,
        sensitive_context=sensitive_context,
        control_result=control_result,
    )


def analysis_to_bcg_profile(analysis: TextAnalysis) -> dict[str, BCGVector]:
    """
    Convert text analysis signals to a 4-role BCG profile.

    Roles:
      G_up   : aspirational good (optimistic +0.1 offset on B, C, G)
      G_down : grounded good     (evidence-weighted C)
      H_up   : theoretical harm  (harm-scaled boundary, grace = 1-harm)
      H_down : practical harm    (direct harm as B; low-confidence caution as C)
    """
    b = analysis.boundary
    c = analysis.covenant
    g = analysis.grace
    harm = analysis.harm
    ev = analysis.evidence
    conf = analysis.confidence

    def _clamp(v: float) -> float:
        return max(0.05, min(0.95, v))

    g_up = BCGVector(
        B=_clamp(b + 0.10),
        C=_clamp(c + 0.10),
        G=_clamp(g + 0.10),
    )
    g_down = BCGVector(
        B=_clamp(b),
        C=_clamp(0.70 * c + 0.30 * ev),
        G=_clamp(g),
    )
    h_up = BCGVector(
        B=_clamp(harm * b + (1.0 - harm) * 0.30),
        C=_clamp(0.50 * c + 0.50 * harm),
        G=_clamp(1.0 - harm),
    )
    h_down = BCGVector(
        B=_clamp(harm),
        C=_clamp(0.50 * (1.0 - conf) + 0.50 * harm),
        G=_clamp(1.0 - 0.70 * harm),
    )
    return {"G_up": g_up, "G_down": g_down, "H_up": h_up, "H_down": h_down}


def quick_ethics_audit(
    text: str,
    principles=None,
    scalarizer: ScalarizerConfig | None = None,
    decoder: DecoderConfig | None = None,
    weights: ObjectiveWeights | None = None,
    gate_thresholds: GateThresholds | None = None,
) -> QuickEthicsReport:
    """
    One-shot ethics evaluation of a text string.

    Args:
        text:            The text to evaluate
        principles:      Principle list (default: all 7 defaults)
        scalarizer:      Override default scalarizer config
        decoder:         Override default decoder config
        weights:         Override default objective weights
        gate_thresholds: Override default gate thresholds

    Returns:
        QuickEthicsReport with text analysis, BCG profile, and formula pipeline result
    """
    analysis = analyze_text(text)
    bcg_profile = analysis_to_bcg_profile(analysis)

    event = DialogueEvent(
        event_id="text_eval",
        text=text,
        speaker="user",
        sensitive_context=analysis.sensitive_context,
        claimed_confidence=analysis.confidence,
        evidence_coverage=analysis.evidence,
        meta={"domain": analysis.domain},
    )

    # Pass text-derived control so write_gate is meaningful without vLLM telemetry
    text_control = analysis.control_result.control if analysis.control_result else None

    pipeline = run_ethics_pipeline(
        bcg_profile=bcg_profile,
        principles=principles,
        scalarizer=scalarizer,
        decoder=decoder,
        weights=weights,
        gate_thresholds=gate_thresholds,
        event=event,
        control=text_control,
    )

    return QuickEthicsReport(
        input_text=text,
        analysis=analysis,
        bcg_profile=bcg_profile,
        pipeline=pipeline,
    )


def batch_audit_texts(
    texts: list[str],
    **kwargs,
) -> list[QuickEthicsReport]:
    """
    Run quick_ethics_audit on a list of texts.

    Returns one QuickEthicsReport per input text.
    """
    return [quick_ethics_audit(text, **kwargs) for text in texts]
