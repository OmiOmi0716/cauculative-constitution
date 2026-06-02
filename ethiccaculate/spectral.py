from __future__ import annotations

from dataclasses import dataclass

from .models import GeomBlock, ROLE_KEYS, SpectralState, clamp


@dataclass(frozen=True)
class ScalarizerConfig:
    bias: float = 0.0
    L: float = 1.0
    a: float = 1.0
    b: float = 1.0
    A: float = 100.0
    B: float = 100.0
    eps: float = 1e-9


def scalarize(block: GeomBlock, theta: ScalarizerConfig | None = None) -> float:
    cfg = theta or ScalarizerConfig()
    l = block.L / 100.0
    a = block.a / cfg.A
    b = block.b / cfg.B
    return cfg.bias + cfg.L * l + cfg.a * a + cfg.b * b


def hadamard4(values: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    f0, f1, f2, f3 = values
    return (
        0.5 * (f0 + f1 + f2 + f3),
        0.5 * (f0 + f1 - f2 - f3),
        0.5 * (f0 - f1 + f2 - f3),
        0.5 * (f0 - f1 - f2 + f3),
    )


def spectral_from_blocks(
    blocks: dict[str, GeomBlock],
    theta: ScalarizerConfig | None = None,
    noise: float = 0.0,
) -> SpectralState:
    cfg = theta or ScalarizerConfig()
    missing = [role for role in ROLE_KEYS if role not in blocks]
    if missing:
        raise ValueError(f"Missing geometry roles: {', '.join(missing)}")

    scalars = {role: scalarize(blocks[role], cfg) for role in ROLE_KEYS}
    values = tuple(scalars[role] for role in ROLE_KEYS)
    c0, c_gh, c_ud, c_cross = hadamard4(values)

    ebase = c0**2
    esyn = c_ud**2
    ecosyn = c_gh**2 + c_cross**2
    enoise = max(0.0, noise)
    denom = ebase + esyn + ecosyn + enoise + cfg.eps
    raw_u = (ebase + esyn - ecosyn - enoise) / denom
    return SpectralState(
        Ebase=ebase,
        Esyn=esyn,
        Ecosyn=ecosyn,
        Enoise=enoise,
        U=clamp(raw_u, -1.0, 1.0),
        c0=c0,
        c_gh=c_gh,
        c_ud=c_ud,
        c_cross=c_cross,
        scalars=scalars,
    )


def total_scalar_energy(blocks: dict[str, GeomBlock], theta: ScalarizerConfig | None = None) -> float:
    cfg = theta or ScalarizerConfig()
    return sum(scalarize(blocks[role], cfg) ** 2 for role in ROLE_KEYS)


def total_spectral_energy(spectral: SpectralState) -> float:
    return spectral.Ebase + spectral.Esyn + spectral.Ecosyn + spectral.Enoise
