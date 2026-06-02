import numpy as np
from dataclasses import dataclass


@dataclass
class VasicekParams:
    kappa: float  # mean reversion speed
    theta: float  # long-run mean
    sigma: float  # volatility


def simulate(
    r0: float,
    params: VasicekParams,
    n_paths: int,
    n_steps: int,
    dt: float,
    seed: int | None = None,
) -> np.ndarray:
    """
    Vectorised Euler-Maruyama simulation.
    Returns shape (n_paths, n_steps + 1).
    """
    rng = np.random.default_rng(seed)

    paths = np.empty((n_paths, n_steps + 1))
    paths[:, 0] = r0

    sqrt_dt = np.sqrt(dt)
    Z = rng.standard_normal((n_paths, n_steps))

    for t in range(n_steps):
        r = paths[:, t]
        drift = params.kappa * (params.theta - r) * dt
        diffusion = params.sigma * sqrt_dt * Z[:, t]
        paths[:, t + 1] = r + drift + diffusion

    return paths


def bond_price(r: float, tau: float, params: VasicekParams) -> float:
    """Closed-form zero-coupon bond price P(0, tau) under Vasicek."""
    k, th, s = params.kappa, params.theta, params.sigma
    if k == 0:
        B = tau
    else:
        B = (1 - np.exp(-k * tau)) / k

    A = np.exp(
        (th - s**2 / (2 * k**2)) * (B - tau)
        - s**2 * B**2 / (4 * k)
    )
    return A * np.exp(-B * r)


def negative_rate_probability(paths: np.ndarray) -> float:
    """Fraction of all path-steps with r < 0."""
    return float(np.mean(paths < 0))


def terminal_negative_rate_probability(paths: np.ndarray) -> float:
    """Fraction of paths where the terminal rate is negative."""
    return float(np.mean(paths[:, -1] < 0))
