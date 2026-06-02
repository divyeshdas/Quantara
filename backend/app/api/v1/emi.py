import numpy as np
from fastapi import APIRouter, HTTPException

from app.schemas.emi import EMIRequest, EMIResponse, EMIScenario, EMIDistribution
from app.core.redis import make_cache_key, get_cached, set_cached
from quant_engine.cir import CIRParams, simulate as cir_sim
from quant_engine.calibration import FALLBACK_CIR
from quant_engine.emi_calculator import compute_emi, emi_from_simulated_paths
from app.api.v1.simulate import get_calibrated_params

router = APIRouter()

LOAN_SPREADS = {"home": 2.75, "personal": 5.5, "business": 4.0}


@router.post("/impact", response_model=EMIResponse)
async def emi_impact(req: EMIRequest):
    cache_key = "emi:" + make_cache_key("cir", req.current_rate, req.horizon_months, req.n_paths)
    cache_key += f":{req.loan_amount}:{req.tenure_months}:{req.loan_type}"

    _, c_params, _, _ = get_calibrated_params()
    params = c_params or FALLBACK_CIR

    n_steps = req.horizon_months * 21
    paths = cir_sim(req.current_rate, params, req.n_paths, n_steps, 1 / 252)
    terminal_rates = paths[:, -1]

    spread = req.bank_spread or LOAN_SPREADS.get(req.loan_type, 2.75)
    emi_dist = emi_from_simulated_paths(terminal_rates, spread, req.loan_amount, req.tenure_months)

    current_lending = req.current_rate + spread
    current_emi_result = compute_emi(req.loan_amount, current_lending, req.tenure_months)

    p5_rate = float(np.percentile(terminal_rates, 5)) + spread
    p50_rate = float(np.percentile(terminal_rates, 50)) + spread
    p95_rate = float(np.percentile(terminal_rates, 95)) + spread

    scenarios = [
        EMIScenario(
            rate=round(p5_rate, 2),
            emi=compute_emi(req.loan_amount, p5_rate, req.tenure_months).monthly_emi,
            total_payment=compute_emi(req.loan_amount, p5_rate, req.tenure_months).total_payment,
            total_interest=compute_emi(req.loan_amount, p5_rate, req.tenure_months).total_interest,
            label="Best case (5th pct.)",
        ),
        EMIScenario(
            rate=round(p50_rate, 2),
            emi=compute_emi(req.loan_amount, p50_rate, req.tenure_months).monthly_emi,
            total_payment=compute_emi(req.loan_amount, p50_rate, req.tenure_months).total_payment,
            total_interest=compute_emi(req.loan_amount, p50_rate, req.tenure_months).total_interest,
            label="Median scenario",
        ),
        EMIScenario(
            rate=round(p95_rate, 2),
            emi=compute_emi(req.loan_amount, p95_rate, req.tenure_months).monthly_emi,
            total_payment=compute_emi(req.loan_amount, p95_rate, req.tenure_months).total_payment,
            total_interest=compute_emi(req.loan_amount, p95_rate, req.tenure_months).total_interest,
            label="Worst case (95th pct.)",
        ),
    ]

    worst_emi = scenarios[2].emi
    max_additional_monthly = round(worst_emi - current_emi_result.monthly_emi, 2)
    max_additional_tenure = round(max_additional_monthly * req.tenure_months, 2)

    return EMIResponse(
        scenarios=scenarios,
        emi_distribution=EMIDistribution(**emi_dist),
        current_emi=current_emi_result.monthly_emi,
        max_additional_monthly=max_additional_monthly,
        max_additional_tenure=max_additional_tenure,
    )
