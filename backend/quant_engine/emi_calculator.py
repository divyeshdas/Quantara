import numpy as np
from dataclasses import dataclass


@dataclass
class EMIResult:
    monthly_emi: float
    total_payment: float
    total_interest: float
    rate_used: float  # annual %


def compute_emi(principal: float, annual_rate: float, tenure_months: int) -> EMIResult:
    """
    Standard reducing-balance EMI formula.
    EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    annual_rate: percentage (e.g. 8.5 for 8.5%)
    """
    r = annual_rate / 100 / 12
    n = tenure_months

    if r == 0:
        emi = principal / n
    else:
        emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)

    total = emi * n
    return EMIResult(
        monthly_emi=round(emi, 2),
        total_payment=round(total, 2),
        total_interest=round(total - principal, 2),
        rate_used=annual_rate,
    )


def emi_from_simulated_paths(
    terminal_rates: np.ndarray,
    spread: float,
    principal: float,
    tenure_months: int,
) -> dict:
    """
    Given simulated terminal rates (e.g. 12-month forecasts), compute EMI distribution.
    spread: bank spread over repo rate in percentage points (e.g. 2.5)
    """
    lending_rates = terminal_rates + spread
    emis = np.array([
        compute_emi(principal, float(r), tenure_months).monthly_emi
        for r in lending_rates
    ])

    return {
        "p5": float(np.percentile(emis, 5)),
        "p25": float(np.percentile(emis, 25)),
        "p50": float(np.percentile(emis, 50)),
        "p75": float(np.percentile(emis, 75)),
        "p95": float(np.percentile(emis, 95)),
        "mean": float(np.mean(emis)),
        "std": float(np.std(emis)),
    }
