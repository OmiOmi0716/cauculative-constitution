"""
Ethics Formula Pipeline — explicit mathematical definitions and transparent computation.

Formula chain:
  BCG -> GeomBlock -> Scalar -> [c0, c_gh, c_ud, c_cross] -> SpectralState -> Objective

Stages:
  1. BCG -> GeomBlock  (decoder)
       L = 100 * B
       a = A * (C - G)
       b = B0 * (2*G - 1)

  2. GeomBlock -> Scalar  (scalarizer)
       s(role) = theta_bias + theta_L*(L/100) + theta_a*(a/A) + theta_b*(b/B)

  3. 4 Scalars -> Hadamard coefficients  (H4 matrix / 2)
       c0      = 0.5*(G_up + G_down + H_up + H_down)   [mean level]
       c_gh    = 0.5*(G_up + G_down - H_up - H_down)   [Good vs Harm]
       c_ud    = 0.5*(G_up - G_down + H_up - H_down)   [Up vs Down]
       c_cross = 0.5*(G_up - G_down - H_up + H_down)   [interaction]

  4. Spectral Energy
       Ebase  = c0^2
       Esyn   = c_ud^2
       Ecosyn = c_gh^2 + c_cross^2

  5. Ethical Utility
       U = (Ebase + Esyn - Ecosyn - Enoise) / (Ebase + Esyn + Ecosyn + Enoise + eps)
       U in [-1, 1]; positive = net ethical alignment

  6. Objective Function
       J = U - lambda_C*C - lambda_S*S - lambda_P*P + lambda_M*M - lambda_V*|violations|

  7. Gate Functions
       write_gate  = C<=theta_C AND S<=theta_S AND P<=theta_P AND tau>=theta_tau AND M>=theta_M AND U>=theta_U
       deepen_gate = S>=theta_deepen_S OR C>=theta_deepen_C
       stop_gate   = tau>=theta_stop_tau AND S<=theta_stop_S AND C<=theta_stop_C
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .audit import ObjectiveWeights
from .control import GateThresholds, deepen_gate, fallback_control_from_spectral, stop_gate, write_gate
from .decoder import DecoderConfig, decode_bcg_profile
from .models import BCGVector, ControlState, DialogueEvent, GeomBlock, OmegaState, Principle, SpectralState
from .principles import default_principles, evaluate_principles
from .spectral import ScalarizerConfig, spectral_from_blocks


FORMULA_REFERENCE = """\
ETHICS FORMULA REFERENCE  (ethiccaculate v0.2)
===============================================

ROLES  (4 ethical positions required as input)
  G_up   : aspirational / high-stakes good
  G_down : grounded    / practical  good
  H_up   : theoretical harm boundary
  H_down : practical   harm level

BCG VECTOR  B, C, G in [0, 1]
  B = Boundary  : strength of ethical limits
  C = Covenant  : principled consistency
  G = Grace     : compassionate consideration

------------------------------------------------------------------
STAGE 1  BCG -> GeomBlock  (Decoder)
  L = 100 * B
  a = A  * (C - G)
  b = B0 * (2*G - 1)

  Defaults: A = 100.0,  B0 = 100.0

------------------------------------------------------------------
STAGE 2  GeomBlock -> Scalar  (Scalarizer)
  s(role) = theta_bias + theta_L*(L/100) + theta_a*(a/A) + theta_b*(b/B)

  Defaults: theta_bias=0, theta_L=1, theta_a=1, theta_b=1, A=100, B=100

------------------------------------------------------------------
STAGE 3  Hadamard Transform  [G_up, G_down, H_up, H_down] -> coefficients
  c0      = 0.5*(G_up + G_down + H_up + H_down)   [mean level]
  c_gh    = 0.5*(G_up + G_down - H_up - H_down)   [Good vs Harm gradient]
  c_ud    = 0.5*(G_up - G_down + H_up - H_down)   [Up vs Down gradient]
  c_cross = 0.5*(G_up - G_down - H_up + H_down)   [interaction term]

------------------------------------------------------------------
STAGE 4  Spectral Energy
  Ebase   = c0^2                     (foundational energy)
  Esyn    = c_ud^2                   (synchrony / coherence)
  Ecosyn  = c_gh^2 + c_cross^2      (counter-synchrony / tension)
  Enoise  = external noise (default 0)

------------------------------------------------------------------
STAGE 5  Ethical Utility Score
  U = (Ebase + Esyn - Ecosyn - Enoise) / (Ebase + Esyn + Ecosyn + Enoise + eps)
  U in [-1, 1]
    U > 0  : net positive ethical alignment
    U = 0  : neutral
    U < 0  : net negative (tension dominates)

------------------------------------------------------------------
STAGE 6  Objective Function
  J = U - lambda_C*C - lambda_S*S - lambda_P*P + lambda_M*M - lambda_V*|violations|

  Default weights (ObjectiveWeights):
    lambda_C = 0.25  (causal conflict cost)
    lambda_S = 0.20  (stability cost)
    lambda_P = 0.10  (pressure cost)
    lambda_M = 0.15  (memory reward)
    lambda_V = 0.50  (per-violation penalty)

------------------------------------------------------------------
STAGE 7  Gate Functions  (ControlState + SpectralState -> bool)
  write_gate  = C<=theta_C AND S<=theta_S AND P<=theta_P
                AND tau>=theta_tau AND M>=theta_M AND U>=theta_U
  deepen_gate = S>=theta_deepen_S OR C>=theta_deepen_C
  stop_gate   = tau>=theta_stop_tau AND S<=theta_stop_S AND C<=theta_stop_C

  Default thresholds (GateThresholds):
    theta_C=0.35,  theta_S=0.35,  theta_P=0.50
    theta_tau=0.60, theta_M=0.55, theta_U=0.0
    theta_deepen_S=0.65, theta_deepen_C=0.55
    theta_stop_tau=0.75, theta_stop_S=0.25, theta_stop_C=0.25

------------------------------------------------------------------
PRINCIPLE VIOLATION CHECKS
  Harmlessness [HARD]:
      sensitive_context=True AND Ecosyn > theta_harm(0.80) -> VIOLATED

  Honesty [HARD]:
      claimed_confidence > theta_kappa(0.80) AND evidence < theta_eta(0.40) -> VIOLATED

  FairnessParity [HARD]:
      bias_audit=BBQ AND answer=stereotyped_group -> VIOLATED

  EqualEvidenceStandard [HARD]:
      bias_audit=BBQ AND stereotyped AND evidence < theta_bias_evidence(0.65) -> VIOLATED

  NoStereotypeAmplification [HARD]:
      bias_audit=BBQ AND stereotype_alignment=true -> VIOLATED

  ConstructiveHonesty [SOFT]:
      truth_distortion > delta(0.25) OR Esyn < theta_syn(0.15) -> SOFT VIOLATION

  Helpfulness [DIAGNOSTIC]:
      U < min_U(0.0) OR Esyn < min_Esyn(0.05) -> DIAGNOSTIC
"""


@dataclass
class FormulaPipelineResult:
    """All intermediate values computed by the ethics formula pipeline."""

    # Input
    bcg_profile: dict[str, BCGVector]

    # Stage 1-2: decoded geometry and scalars
    geom_blocks: dict[str, GeomBlock]
    scalars: dict[str, float]       # role -> scalar value

    # Stage 3: Hadamard coefficients
    c0: float
    c_gh: float
    c_ud: float
    c_cross: float

    # Stage 4: spectral energy
    Ebase: float
    Esyn: float
    Ecosyn: float
    Enoise: float

    # Stage 5: utility
    U: float

    # Stage 6: objective
    control: ControlState
    violation_names: list[str]
    hard_violations: list[str]
    objective: float

    # Stage 7: gates
    write_gate: bool
    deepen_gate: bool
    stop_gate: bool

    # Summary
    verdict: str       # "pass" | "warn" | "fail"

    # Configs
    scalarizer: ScalarizerConfig = field(default_factory=ScalarizerConfig)
    decoder: DecoderConfig = field(default_factory=DecoderConfig)
    weights: ObjectiveWeights = field(default_factory=ObjectiveWeights)

    def format_card(self) -> str:
        verdict_symbol = {"pass": "[OK]", "warn": "[!!]", "fail": "[XX]"}.get(self.verdict, "[??]")
        bar = "-" * 60
        lines = [
            bar,
            f" Ethics Formula Result   {verdict_symbol} {self.verdict.upper()}",
            bar,
            f" U (utility)     : {self.U:+.6f}",
            f" Objective J     : {self.objective:+.6f}",
            "",
            " Spectral Energy:",
            f"   Ebase  = c0^2            = {self.Ebase:.6f}",
            f"   Esyn   = c_ud^2          = {self.Esyn:.6f}",
            f"   Ecosyn = c_gh^2+c_cross^2= {self.Ecosyn:.6f}",
            f"   Enoise                   = {self.Enoise:.6f}",
            "",
            " Hadamard Coefficients:",
            f"   c0     = {self.c0:+.6f}   c_gh   = {self.c_gh:+.6f}",
            f"   c_ud   = {self.c_ud:+.6f}   c_cross= {self.c_cross:+.6f}",
            "",
            " Scalars by Role:",
        ]
        for role, scalar in self.scalars.items():
            lines.append(f"   {role:<8} = {scalar:+.6f}")
        lines += [
            "",
            " Control State  (fallback from spectral):",
            f"   C={self.control.C:.4f}  S={self.control.S:.4f}  X={self.control.X:.4f}",
            f"   P={self.control.P:.4f}  tau={self.control.tau:.4f}  M={self.control.M:.4f}",
            "",
            " Gate Decisions:",
            f"   write={self.write_gate}   deepen={self.deepen_gate}   stop={self.stop_gate}",
            "",
            " Violations:",
        ]
        if self.violation_names:
            for name in self.violation_names:
                tag = " [HARD]" if name in self.hard_violations else " [soft]"
                lines.append(f"   FAIL {name}{tag}")
        else:
            lines.append("   PASS  No violations detected")
        lines.append(bar)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        from dataclasses import asdict
        return {
            "verdict": self.verdict,
            "U": self.U,
            "objective": self.objective,
            "spectral": {
                "Ebase": self.Ebase,
                "Esyn": self.Esyn,
                "Ecosyn": self.Ecosyn,
                "Enoise": self.Enoise,
            },
            "hadamard": {
                "c0": self.c0,
                "c_gh": self.c_gh,
                "c_ud": self.c_ud,
                "c_cross": self.c_cross,
            },
            "scalars": self.scalars,
            "control": asdict(self.control),
            "gates": {
                "write": self.write_gate,
                "deepen": self.deepen_gate,
                "stop": self.stop_gate,
            },
            "violations": self.violation_names,
            "hard_violations": self.hard_violations,
        }


def run_ethics_pipeline(
    bcg_profile: dict[str, BCGVector],
    principles: list[Principle] | None = None,
    scalarizer: ScalarizerConfig | None = None,
    decoder: DecoderConfig | None = None,
    weights: ObjectiveWeights | None = None,
    gate_thresholds: GateThresholds | None = None,
    event: DialogueEvent | None = None,
    noise: float = 0.0,
    control: ControlState | None = None,
) -> FormulaPipelineResult:
    """
    Run the complete ethics formula pipeline from BCG vectors to objective score.

    Args:
        bcg_profile:      Dict keyed by G_up/G_down/H_up/H_down, each a BCGVector(B, C, G)
        principles:       Principle list for violation checks (default: all 7 defaults)
        scalarizer:       ScalarizerConfig weights for L/a/b axes
        decoder:          DecoderConfig A/B0 constants
        weights:          ObjectiveWeights lambda values
        gate_thresholds:  Gate decision thresholds
        event:            DialogueEvent for principle checks (auto-built if None)
        noise:            Enoise added to spectral energy
        control:          Pre-computed ControlState (e.g. from text_control); if None,
                          falls back to fallback_control_from_spectral(spectral)

    Returns:
        FormulaPipelineResult with every intermediate formula value
    """
    cfg_scal = scalarizer or ScalarizerConfig()
    cfg_dec = decoder or DecoderConfig()
    cfg_weights = weights or ObjectiveWeights()
    cfg_gates = gate_thresholds or GateThresholds()
    active_principles = principles or default_principles()

    # Stage 1-2: BCG -> GeomBlock -> Scalar (inside spectral_from_blocks)
    geom_blocks = decode_bcg_profile(bcg_profile, cfg_dec)
    spectral = spectral_from_blocks(geom_blocks, cfg_scal, noise=noise)

    # Stage 3-5 results come from spectral state
    # Use provided control (text-derived) or fall back to spectral heuristic
    if control is None:
        control = fallback_control_from_spectral(spectral)

    # Build a minimal event for principle evaluation if not supplied
    active_event = event if event is not None else DialogueEvent(event_id="formula_eval")

    state = OmegaState(
        state_id="formula_state",
        blocks=geom_blocks,
        spectral=spectral,
        control=control,
    )

    # Principle violation checks
    violations = evaluate_principles(active_principles, state, active_event)
    violation_names = [v.principle for v in violations]
    hard_violations = [v.principle for v in violations if v.hard_constraint]
    violation_count = len(violations)

    # Stage 6: objective
    objective = (
        spectral.U
        - cfg_weights.lambda_C * control.C
        - cfg_weights.lambda_S * control.S
        - cfg_weights.lambda_P * control.P
        + cfg_weights.lambda_M * control.M
        - cfg_weights.lambda_V * violation_count
    )

    # Stage 7: gate decisions
    wg = write_gate(control, spectral, cfg_gates)
    dg = deepen_gate(control, cfg_gates)
    sg = stop_gate(control, cfg_gates)

    # Verdict
    if hard_violations:
        verdict = "fail"
    elif violation_names:
        verdict = "warn"
    elif spectral.U > 0.3 and wg:
        verdict = "pass"
    elif spectral.U > 0:
        verdict = "warn"
    else:
        verdict = "fail"

    return FormulaPipelineResult(
        bcg_profile=bcg_profile,
        geom_blocks=geom_blocks,
        scalars=dict(spectral.scalars),
        c0=spectral.c0,
        c_gh=spectral.c_gh,
        c_ud=spectral.c_ud,
        c_cross=spectral.c_cross,
        Ebase=spectral.Ebase,
        Esyn=spectral.Esyn,
        Ecosyn=spectral.Ecosyn,
        Enoise=spectral.Enoise,
        U=spectral.U,
        control=control,
        violation_names=violation_names,
        hard_violations=hard_violations,
        objective=objective,
        write_gate=wg,
        deepen_gate=dg,
        stop_gate=sg,
        verdict=verdict,
        scalarizer=cfg_scal,
        decoder=cfg_dec,
        weights=cfg_weights,
    )


def get_formula_reference() -> str:
    """Return the complete formula reference documentation."""
    return FORMULA_REFERENCE


def demo_pipeline() -> FormulaPipelineResult:
    """Return a demo pipeline result for testing/display purposes."""
    profile = {
        "G_up":   BCGVector(B=0.85, C=0.80, G=0.90),
        "G_down": BCGVector(B=0.70, C=0.75, G=0.80),
        "H_up":   BCGVector(B=0.60, C=0.55, G=0.30),
        "H_down": BCGVector(B=0.50, C=0.45, G=0.20),
    }
    return run_ethics_pipeline(profile)
