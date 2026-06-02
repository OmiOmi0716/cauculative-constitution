from __future__ import annotations

from math import fabs

from .models import GeomBlock, MoveRecord, OmegaState, ROLE_KEYS
from .spectral import ScalarizerConfig, hadamard4, scalarize


def copy_blocks(blocks: dict[str, GeomBlock]) -> dict[str, GeomBlock]:
    return {role: GeomBlock(block.L, block.a, block.b) for role, block in blocks.items()}


def _apply_scalar_delta(
    block: GeomBlock,
    scalar_delta: float,
    scalarizer: ScalarizerConfig,
) -> GeomBlock:
    if abs(scalarizer.a) > 1e-12:
        return GeomBlock(
            L=block.L,
            a=block.a + scalar_delta * scalarizer.A / scalarizer.a,
            b=block.b,
        )
    if abs(scalarizer.L) > 1e-12:
        return GeomBlock(
            L=block.L + scalar_delta * 100.0 / scalarizer.L,
            a=block.a,
            b=block.b,
        )
    if abs(scalarizer.b) > 1e-12:
        return GeomBlock(
            L=block.L,
            a=block.a,
            b=block.b + scalar_delta * scalarizer.B / scalarizer.b,
        )
    raise ValueError("Scalarizer has no editable axis.")


def apply_g_reframe_justice(
    blocks: dict[str, GeomBlock],
    eta: float = 0.5,
    scalarizer: ScalarizerConfig | None = None,
) -> dict[str, GeomBlock]:
    cfg = scalarizer or ScalarizerConfig(a=1.0, L=0.0, b=0.0)
    current_scalars = tuple(scalarize(blocks[role], cfg) for role in ROLE_KEYS)
    c0, c_gh, c_ud, c_cross = hadamard4(current_scalars)
    target_scalars = hadamard4((c0, (1.0 - eta) * c_gh, c_ud, (1.0 - eta) * c_cross))

    new_blocks = copy_blocks(blocks)
    for role, target_scalar in zip(ROLE_KEYS, target_scalars):
        current_scalar = scalarize(new_blocks[role], cfg)
        new_blocks[role] = _apply_scalar_delta(new_blocks[role], target_scalar - current_scalar, cfg)
    return new_blocks


def _scalar_delta_to_axis_step(delta: float, scalarizer: ScalarizerConfig) -> tuple[str, float]:
    if abs(scalarizer.L) > 1e-12:
        return "L", delta * 100.0 / scalarizer.L
    if abs(scalarizer.a) > 1e-12:
        return "a", delta * scalarizer.A / scalarizer.a
    if abs(scalarizer.b) > 1e-12:
        return "b", delta * scalarizer.B / scalarizer.b
    raise ValueError("Scalarizer has no editable axis for H_BOUNDARY_SET.")


def apply_h_boundary_set(
    blocks: dict[str, GeomBlock],
    delta: float = 0.3,
    scalarizer: ScalarizerConfig | None = None,
) -> dict[str, GeomBlock]:
    cfg = scalarizer or ScalarizerConfig()
    axis, step = _scalar_delta_to_axis_step(delta, cfg)
    new_blocks = copy_blocks(blocks)

    for role, sign in (("G_up", 1.0), ("G_down", -1.0), ("H_up", 1.0), ("H_down", -1.0)):
        block = new_blocks[role]
        if axis == "L":
            new_blocks[role] = GeomBlock(L=block.L + sign * step, a=block.a, b=block.b)
        elif axis == "a":
            new_blocks[role] = GeomBlock(L=block.L, a=block.a + sign * step, b=block.b)
        else:
            new_blocks[role] = GeomBlock(L=block.L, a=block.a, b=block.b + sign * step)
    return new_blocks


def _lerp(left: float, right: float, weight: float) -> float:
    return left + weight * (right - left)


def apply_bridge_theory_to_psy(
    blocks: dict[str, GeomBlock],
    gamma: float = 0.4,
) -> dict[str, GeomBlock]:
    new_blocks = copy_blocks(blocks)
    for g_role, h_role in (("G_up", "H_up"), ("G_down", "H_down")):
        g_block = new_blocks[g_role]
        h_block = new_blocks[h_role]
        new_blocks[h_role] = GeomBlock(
            L=_lerp(h_block.L, g_block.L, gamma),
            a=_lerp(h_block.a, g_block.a, gamma),
            b=_lerp(h_block.b, g_block.b, gamma),
        )
    return new_blocks


def apply_bridge_data_to_theory(
    blocks: dict[str, GeomBlock],
    gamma: float = 0.4,
) -> dict[str, GeomBlock]:
    new_blocks = copy_blocks(blocks)
    for g_role, h_role in (("G_up", "H_up"), ("G_down", "H_down")):
        g_block = new_blocks[g_role]
        h_block = new_blocks[h_role]
        new_blocks[g_role] = GeomBlock(
            L=_lerp(g_block.L, h_block.L, gamma),
            a=_lerp(g_block.a, h_block.a, gamma),
            b=_lerp(g_block.b, h_block.b, gamma),
        )
    return new_blocks


def apply_operation(
    blocks: dict[str, GeomBlock],
    op: str,
    strength: float,
    scalarizer: ScalarizerConfig | None = None,
) -> dict[str, GeomBlock]:
    if op == "G_REFRAME_JUSTICE":
        return apply_g_reframe_justice(blocks, strength, scalarizer)
    if op == "H_BOUNDARY_SET":
        return apply_h_boundary_set(blocks, strength, scalarizer)
    if op == "BRIDGE_THEO_TO_PSY":
        return apply_bridge_theory_to_psy(blocks, strength)
    if op == "BRIDGE_DATA_TO_THEORY":
        return apply_bridge_data_to_theory(blocks, strength)
    raise ValueError(f"Unknown operation: {op}")


def _mean_g_h_gap(state: OmegaState) -> float:
    gap = 0.0
    for g_role, h_role in (("G_up", "H_up"), ("G_down", "H_down")):
        g_block = state.blocks[g_role]
        h_block = state.blocks[h_role]
        gap += fabs(g_block.L - h_block.L) + fabs(g_block.a - h_block.a) + fabs(g_block.b - h_block.b)
    return gap / 2.0


def infer_move(previous: OmegaState | None, current: OmegaState) -> MoveRecord | None:
    if previous is None:
        return None

    prev_spec = previous.spectral
    cur_spec = current.spectral
    delta_u = cur_spec.U - prev_spec.U
    delta_ecosyn = cur_spec.Ecosyn - prev_spec.Ecosyn

    op: str | None = None
    strength = 0.0

    if cur_spec.c_ud - prev_spec.c_ud > 0.15:
        op = "H_BOUNDARY_SET"
        strength = max(0.0, (cur_spec.c_ud - prev_spec.c_ud) / 2.0)
    elif abs(cur_spec.c_gh) < abs(prev_spec.c_gh) and abs(cur_spec.c_cross) <= abs(prev_spec.c_cross) + 1e-9:
        op = "G_REFRAME_JUSTICE"
        denom = abs(prev_spec.c_gh) + 1e-9
        strength = max(0.0, min(1.0, 1.0 - abs(cur_spec.c_gh) / denom))
    elif _mean_g_h_gap(current) < _mean_g_h_gap(previous):
        op = "BRIDGE_THEO_TO_PSY"
        before = _mean_g_h_gap(previous)
        after = _mean_g_h_gap(current)
        strength = max(0.0, min(1.0, 1.0 - after / (before + 1e-9)))

    if op is None:
        return None

    return MoveRecord(
        move_id="",
        op=op,
        strength=strength,
        pre_state=previous.state_id,
        post_state=current.state_id,
        audit={"delta_U": delta_u, "delta_Ecosyn": delta_ecosyn},
    )
