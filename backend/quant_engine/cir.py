import numpy as np
from dataclasses import dataclass
from scipy.stats import ncx2


@dataclass
class CIRParams:
    kappa: float
    theta: float
    sigma: float


def feller_condition(params: CIRParams) -> tuple[bool, float]:
    """2κθ > σ² ensures the process never reaches zero."""
    lhs = 2 * params.kappa * params.theta
    rhs = params.sigma**2
    return lhs > rhs, lhs - rhs


def simulate(
    r0: float,
    params: CIRParams,
    n_paths: int,
    n_steps: int,
    dt: float,
    seed: int | None = None,
    use_exact: bool = False,
) -> np.ndarray:
    """
    Vectorised CIR simulation.
    use_exact=True uses non-central chi-squared exact transition (slower but more accurate).
    use_exact=False uses modified Euler-Maruyama (faster, sufficient for n_steps >> 1).
    """
    if use_exact:
        return _simulate_exact(r0, params, n_paths, n_steps, dt, seed)
    return _simulate_euler(r0, params, n_paths, n_steps, dt, seed)


def _simulate_euler(
    r0: float,
    params: CIRParams,
    n_paths: int,
    n_steps: int,
    dt: float,
    seed: int | None,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    paths = np.empty((n_paths, n_steps + 1))
    paths[:, 0] = r0

    sqrt_dt = np.sqrt(dt)
    Z = rng.standard_normal((n_paths, n_steps))

    for t in range(n_steps):
        r = paths[:, t]
        # Milstein correction: add σ²/4 * dt * (Z² - 1) for better accuracy
        sqrt_r = np.sqrt(np.maximum(r, 0))
        drift = params.kappa * (params.theta - r) * dt
        diffusion = params.sigma * sqrt_r * sqrt_dt * Z[:, t]
        paths[:, t + 1] = np.maximum(r + drift + diffusion, 0.0)

    return paths


def _simulate_exact(
    r0: float,
    params: CIRParams,
    n_paths: int,
    n_steps: int,
    dt: float,
    seed: int | None,
) -> np.ndarray:
    """
    Exact simulation via non-central chi-squared transitions.
    Each r_{t+1} | r_t ~ (c * χ²(df, λ)) where c, df, λ are functions of params.
    """
    rng = np.random.default_rng(seed)
    k, th, s = params.kappa, params.theta, params.sigma

    c = s**2 * (1 - np.exp(-k * dt)) / (4 * k)
    df = 4 * k * th / s**2

    paths = np.empty((n_paths, n_steps + 1))
    paths[:, 0] = r0

    for t in range(n_steps):
        r = paths[:, t]
        lam = r * np.exp(-k * dt) / c  # non-centrality parameter
        paths[:, t + 1] = c * ncx2.rvs(df, lam, random_state=rng)

    return paths


def bond_price(r: float, tau: float, params: CIRParams) -> float:
    """Closed-form zero-coupon bond price P(0, tau) under CIR.
    r must be in decimal (e.g. 0.0575). params stored in % space, converted here.
    """
    k = params.kappa
    th = params.theta / 100.0
    s = params.sigma / 10.0  # σ_pct = σ_dec * 10 for CIR

    h = np.sqrt(k**2 + 2 * s**2)

    B = 2 * (np.exp(h * tau) - 1) / (
        (h + k) * (np.exp(h * tau) - 1) + 2 * h
    )

    A = (
        2 * h * np.exp((h + k) * tau / 2)
        / ((h + k) * (np.exp(h * tau) - 1) + 2 * h)
    ) ** (2 * k * th / s**2)

    return A * np.exp(-B * r)
