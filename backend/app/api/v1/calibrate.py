from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

from data.rbi_provider import get_rate_series, expand_to_daily
import pandas as pd
from data.rbi_provider import load_rbi_rates
from quant_engine.calibration import calibrate_vasicek, calibrate_cir

router = APIRouter()


class CalibrationResponse(BaseModel):
    model: str
    kappa: float
    theta: float
    sigma: float
    rmse: float
    converged: bool
    log_likelihood: float
    used_fallback: bool
    feller_condition_met: bool | None
    feller_margin: float | None
    data_points: int


@router.get("/{model}", response_model=CalibrationResponse)
async def get_calibration(model: Literal["vasicek", "cir"]):
    df = load_rbi_rates()
    daily_df = expand_to_daily(df)
    rates = daily_df["rate"].values

    if model == "vasicek":
        result = calibrate_vasicek(rates)
        params = result.params
        feller_met = None
        feller_margin = None
    else:
        result = calibrate_cir(rates)
        params = result.params
        from quant_engine.cir import feller_condition
        feller_met, feller_margin = feller_condition(params)

    return CalibrationResponse(
        model=model,
        kappa=round(params.kappa, 4),
        theta=round(params.theta, 4),
        sigma=round(params.sigma, 4),
        rmse=round(result.rmse, 6),
        converged=result.converged,
        log_likelihood=round(result.log_likelihood, 2),
        used_fallback=result.used_fallback,
        feller_condition_met=feller_met,
        feller_margin=round(feller_margin, 6) if feller_margin is not None else None,
        data_points=len(rates),
    )
