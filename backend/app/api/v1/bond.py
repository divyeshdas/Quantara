import numpy as np
from fastapi import APIRouter

from app.schemas.bond import BondRequest, BondResponse, BondPriceDistribution
from quant_engine.cir import CIRParams, simulate as cir_sim
from quant_engine.vasicek import VasicekParams, simulate as vasicek_sim
from quant_engine.calibration import FALLBACK_CIR, FALLBACK_VASICEK
from quant_engine.bond_pricing import coupon_bond_price, duration, price_from_paths
from app.api.v1.simulate import get_calibrated_params

router = APIRouter()


@router.post("/price", response_model=BondResponse)
async def bond_price_endpoint(req: BondRequest):
    v_params, c_params, _, _ = get_calibrated_params()

    if req.model == "vasicek":
        params = v_params or FALLBACK_VASICEK
        paths = vasicek_sim(req.current_rate, params, req.n_paths, req.horizon_months * 21, 1 / 252)
    else:
        params = c_params or FALLBACK_CIR
        paths = cir_sim(req.current_rate, params, req.n_paths, req.horizon_months * 21, 1 / 252)

    terminal_rates = paths[:, -1]

    current_price = coupon_bond_price(
        req.face_value, req.coupon_rate, req.maturity_years,
        req.current_rate, params, req.frequency
    )
    mod_dur, convexity = duration(
        req.face_value, req.coupon_rate, req.maturity_years,
        req.current_rate, params, req.frequency
    )

    prices = price_from_paths(
        terminal_rates, req.face_value, req.coupon_rate,
        req.maturity_years, params, req.frequency
    )

    median_rate = float(np.percentile(terminal_rates, 50))
    ytm_at_median = median_rate + (req.coupon_rate - req.current_rate) * 0.3

    sample_idx = np.random.choice(len(terminal_rates), size=min(500, len(terminal_rates)), replace=False)

    return BondResponse(
        current_price=round(current_price, 4),
        price_distribution=BondPriceDistribution(
            p5=float(np.percentile(prices, 5)),
            p25=float(np.percentile(prices, 25)),
            p50=float(np.percentile(prices, 50)),
            p75=float(np.percentile(prices, 75)),
            p95=float(np.percentile(prices, 95)),
            mean=float(np.mean(prices)),
            std=float(np.std(prices)),
        ),
        modified_duration=round(mod_dur, 4),
        convexity=round(convexity, 4),
        terminal_rates_sample=terminal_rates[sample_idx].tolist(),
        price_sample=prices[sample_idx].tolist(),
        ytm_at_median_rate=round(ytm_at_median, 4),
    )
