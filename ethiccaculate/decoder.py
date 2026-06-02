from __future__ import annotations

from dataclasses import dataclass

from .models import BCGVector, GeomBlock, ROLE_KEYS, clamp


@dataclass(frozen=True)
class DecoderConfig:
    A: float = 100.0
    B0: float = 100.0


def decode_bcg_to_geom(bcg: BCGVector, config: DecoderConfig | None = None) -> GeomBlock:
    cfg = config or DecoderConfig()
    boundary = clamp(bcg.B, 0.0, 1.0)
    covenant = clamp(bcg.C, 0.0, 1.0)
    grace = clamp(bcg.G, 0.0, 1.0)
    return GeomBlock(
        L=100.0 * boundary,
        a=cfg.A * (covenant - grace),
        b=cfg.B0 * (2.0 * grace - 1.0),
    )


def decode_bcg_profile(
    profile: dict[str, BCGVector],
    config: DecoderConfig | None = None,
) -> dict[str, GeomBlock]:
    missing = [role for role in ROLE_KEYS if role not in profile]
    if missing:
        raise ValueError(f"Missing BCG roles: {', '.join(missing)}")
    return {role: decode_bcg_to_geom(profile[role], config) for role in ROLE_KEYS}
