from __future__ import annotations

from .models import ControlState, DialogueEvent, GeomBlock
from .operations import apply_g_reframe_justice, apply_h_boundary_set
from .spectral import ScalarizerConfig


def blocks_from_scalar_fields(
    values: tuple[float, float, float, float],
    axis: str = "a",
) -> dict[str, GeomBlock]:
    g_up, g_down, h_up, h_down = values

    def make_block(value: float) -> GeomBlock:
        if axis == "L":
            return GeomBlock(L=100.0 * value, a=0.0, b=0.0)
        if axis == "a":
            return GeomBlock(L=0.0, a=value, b=0.0)
        if axis == "b":
            return GeomBlock(L=0.0, a=0.0, b=value)
        raise ValueError(f"Unsupported axis: {axis}")

    return {
        "G_up": make_block(g_up),
        "G_down": make_block(g_down),
        "H_up": make_block(h_up),
        "H_down": make_block(h_down),
    }


def whitepaper_truth_vs_harm_events() -> tuple[list[DialogueEvent], ScalarizerConfig]:
    theta = ScalarizerConfig(L=0.0, a=1.0, b=0.0, A=1.0, B=1.0)
    control = ControlState(C=0.20, S=0.20, X=0.10, P=0.10, tau=0.80, M=0.70)

    initial_blocks = blocks_from_scalar_fields((0.9, 0.7, -0.5, -0.3), axis="a")
    after_reframe = apply_g_reframe_justice(initial_blocks, eta=0.5, scalarizer=theta)
    after_boundary = apply_h_boundary_set(after_reframe, delta=0.3, scalarizer=theta)

    events = [
        DialogueEvent(
            event_id="evt_0",
            text="Initial tension state.",
            speaker="system",
            blocks=initial_blocks,
            control=control,
            sensitive_context=False,
            evidence_coverage=1.0,
        ),
        DialogueEvent(
            event_id="evt_1",
            text="Apply G_REFRAME_JUSTICE.",
            speaker="system",
            blocks=after_reframe,
            control=control,
            declared_move="G_REFRAME_JUSTICE",
            move_strength=0.5,
            sensitive_context=False,
            evidence_coverage=1.0,
        ),
        DialogueEvent(
            event_id="evt_2",
            text="Apply H_BOUNDARY_SET.",
            speaker="system",
            blocks=after_boundary,
            control=control,
            declared_move="H_BOUNDARY_SET",
            move_strength=0.3,
            sensitive_context=False,
            evidence_coverage=1.0,
        ),
    ]
    return events, theta


def multi_system_sensitive_case_events() -> list[DialogueEvent]:
    blocks = blocks_from_scalar_fields((90.0, 70.0, -50.0, -30.0), axis="a")
    control = ControlState(C=0.58, S=0.42, X=0.25, P=0.18, tau=0.34, M=0.41)
    return [
        DialogueEvent(
            event_id="sensitive_0",
            text="The model gives a confident answer in a sensitive context with weak evidence.",
            speaker="ai",
            blocks=blocks,
            control=control,
            sensitive_context=True,
            claimed_confidence=0.94,
            evidence_coverage=0.18,
            truth_distortion=0.12,
            meta={"case": "sensitive_demo"},
        )
    ]
