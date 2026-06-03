import numpy as np
from scipy.optimize import minimize
from dataclasses import dataclass
from typing import Literal

from .vasicek import VasicekParams
from .cir import CIRParams


FALLBACK_VASICEK = VasicekParams(kappa=0.3, theta=6.5, sigma=0.8)
FALLBACK_CIR = CIRParams(kappa=0.3, theta=6.5, sigma=0.8)


@dataclass
class CalibrationResult:
    params: VasicekParams | CIRParams
    rmse: float
    converged: bool
    log_likelihood: float
    used_fallback: bool


def calibrate_vasicek(rates: np.ndarray, dt: float = 1 / 252) -> CalibrationResult:
    """
    MLE calibration for Vasicek using the exact conditional distribution.
    rates: annualised rate series as percentages (e.g. 6.5 for 6.5%)
    """
    r = rates / 100.0  # work in decimal space

    def neg_log_likelihood(params):
        k, th, s = params
        if k <= 0 or s <= 0:
            return 1e10

        exp_kdt = np.exp(-k * dt)
        mu = r[:-1] * exp_kdt + th * (1 - exp_kdt)
        var = s**2 * (1 - np.exp(-2 * k * dt)) / (2 * k)

        if var <= 0:
            return 1e10

        residuals = r[1:] - mu
        ll = -0.5 * np.sum(np.log(2 * np.pi * var) + residuals**2 / var)
        return -ll

    r0_current = float(r[-1])
    x0 = [0.5, float(np.mean(r)), float(np.std(np.diff(r)) * np.sqrt(252))]
    bounds = [(1e-4, 10), (0.001, 0.20), (1e-4, 0.5)]

    try:
        result = minimize(neg_log_likelihood, x0, bounds=bounds, method="L-BFGS-B")
        k, th, s = result.x
        params = VasicekParams(kappa=k, theta=th * 100, sigma=s * 100)
        converged = result.success
        ll = -result.fun
    except Exception:
        params = FALLBACK_VASICEK
        converged = False
        ll = 0.0

    rmse = _compute_rmse(rates, params, dt)

    return CalibrationResult(
        params=params,
        rmse=rmse,
        converged=converged,
        log_likelihood=ll,
        used_fallback=not converged,
    )


def calibrate_cir(rates: np.ndarray, dt: float = 1 / 252) -> CalibrationResult:
    """
    MLE calibration for CIR using the conditional distribution (approximate Gaussian).
    For the full non-central chi-squared MLE, we use a penalised objective.
    """
    r = rates / 100.0

    def neg_log_likelihood(params):
        k, th, s = params
        if k <= 0 or s <= 0 or th <= 0:
            return 1e10

        # Conditional mean and variance via Euler approximation
        mu = r[:-1] + k * (th - r[:-1]) * dt
        var = s**2 * np.maximum(r[:-1], 1e-6) * dt

        residuals = r[1:] - mu
        ll = -0.5 * np.sum(np.log(2 * np.pi * var) + residuals**2 / var)
        return -ll

    x0 = [0.5, float(np.mean(r)), float(np.std(np.diff(r)) * np.sqrt(252) / np.sqrt(float(np.mean(r))))]
    bounds = [(1e-4, 10), (0.001, 0.20), (1e-4, 0.5)]

    try:
        result = minimize(neg_log_likelihood, x0, bounds=bounds, method="L-BFGS-B")
        k, th, s = result.x
        # CIR in % space: dr_pct = κ(θ_pct−r_pct)dt + σ_pct√r_pct dW
        # σ_pct = σ_dec * √100 = σ_dec * 10  (not × 100 like Vasicek)
        params = CIRParams(kappa=k, theta=th * 100, sigma=s * 10)
        converged = result.success
        ll = -result.fun
    except Exception:
        params = FALLBACK_CIR
        converged = False
        ll = 0.0

    rmse = _compute_rmse(rates, params, dt)

    return CalibrationResult(
        params=params,
        rmse=rmse,
        converged=converged,
        log_likelihood=ll,
        used_fallback=not converged,
    )


def _compute_rmse(rates: np.ndarray, params: VasicekParams | CIRParams, dt: float) -> float:
    r = rates / 100.0
    k = params.kappa / 100 if isinstance(params, (VasicekParams, CIRParams)) else params.kappa

    # Use params directly (already converted in calibrate functions for RMSE)
    k = params.kappa
    th = params.theta
    s = params.sigma

    # Work in same scale as input (percentage)
    predicted = rates[:-1] + k * (th - rates[:-1]) * dt
    actual = rates[1:]
    return float(np.sqrt(np.mean((predicted - actual) ** 2)))
