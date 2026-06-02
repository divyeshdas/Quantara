import time
import numpy as np
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.simulation import (
    SimulationRequest,
    SimulationResponse,
    CompareResponse,
    PathsSummary,
    TerminalDistribution,
    CalibratedParams,
)
from app.core.redis import make_cache_key, get_cached, set_cached
from app.core.config import get_settings
from quant_engine.vasicek import VasicekParams, simulate as vasicek_sim, negative_rate_probability as neg_rate_prob
from quant_engine.cir import CIRParams, simulate as cir_sim, feller_condition
from quant_engine.simulation_utils import summarise_paths, terminal_stats, rate_change_probabilities, make_time_axis
from quant_engine.calibration import calibrate_vasicek, calibrate_cir, FALLBACK_VASICEK, FALLBACK_CIR

router = APIRouter()

# In-memory calibration cache — refreshed on startup via scheduler
_calibrated_vasicek: VasicekParams | None = None
_calibrated_cir: CIRParams | None = None
_vasicek_rmse: float = 0.0
_cir_rmse: float = 0.0


def get_calibrated_params():
    return _calibrated_vasicek, _calibrated_cir, _vasicek_rmse, _cir_rmse


def set_calibrated_params(v_params, c_params, v_rmse, c_rmse):
    global _calibrated_vasicek, _calibrated_cir, _vasicek_rmse, _cir_rmse
    _calibrated_vasicek = v_params
    _calibrated_cir = c_params
    _vasicek_rmse = v_rmse
    _cir_rmse = c_rmse


def _build_vasicek_response(
    req: SimulationRequest,
    paths: np.ndarray,
    params: VasicekParams,
    elapsed_ms: float,
    cache_hit: bool,
    converged: bool,
    used_fallback: bool,
) -> SimulationResponse:
    summary = summarise_paths(paths)
    stats = terminal_stats(paths)
    probs = rate_change_probabilities(paths, req.current_rate)
    time_ax = make_time_axis(req.horizon_months, paths.shape[1] - 1)

    return SimulationResponse(
        model="vasicek",
        paths_summary=PathsSummary(**summary),
        terminal_distribution=TerminalDistribution(**stats),
        calibrated_params=CalibratedParams(kappa=params.kappa, theta=params.theta, sigma=params.sigma),
        time_axis=time_ax,
        negative_rate_probability=neg_rate_prob(paths),
        prob_increase=probs["prob_increase"],
        prob_decrease=probs["prob_decrease"],
        computation_time_ms=elapsed_ms,
        cache_hit=cache_hit,
        calibration_converged=converged,
        used_fallback_params=used_fallback,
    )


def _build_cir_response(
    req: SimulationRequest,
    paths: np.ndarray,
    params: CIRParams,
    elapsed_ms: float,
    cache_hit: bool,
    converged: bool,
    used_fallback: bool,
) -> SimulationResponse:
    summary = summarise_paths(paths)
    stats = terminal_stats(paths)
    probs = rate_change_probabilities(paths, req.current_rate)
    time_ax = make_time_axis(req.horizon_months, paths.shape[1] - 1)
    feller_met, feller_margin = feller_condition(params)

    return SimulationResponse(
        model="cir",
        paths_summary=PathsSummary(**summary),
        terminal_distribution=TerminalDistribution(**stats),
        calibrated_params=CalibratedParams(kappa=params.kappa, theta=params.theta, sigma=params.sigma),
        time_axis=time_ax,
        feller_condition_met=feller_met,
        feller_margin=feller_margin,
        prob_increase=probs["prob_increase"],
        prob_decrease=probs["prob_decrease"],
        computation_time_ms=elapsed_ms,
        cache_hit=cache_hit,
        calibration_converged=converged,
        used_fallback_params=used_fallback,
    )


@router.post("/vasicek", response_model=SimulationResponse)
async def simulate_vasicek(req: SimulationRequest):
    settings = get_settings()
    cache_key = make_cache_key("vasicek", req.current_rate, req.horizon_months, req.n_paths)

    cached = await get_cached(cache_key)
    if cached:
        cached["cache_hit"] = True
        return SimulationResponse(**cached)

    t0 = time.perf_counter()

    v_params, _, v_rmse, _ = get_calibrated_params()
    if req.use_calibrated and v_params:
        params = v_params
        converged = True
        used_fallback = False
    elif req.model_params.kappa is not None:
        params = VasicekParams(
            kappa=req.model_params.kappa,
            theta=req.model_params.theta,
            sigma=req.model_params.sigma,
        )
        converged = True
        used_fallback = False
    else:
        params = FALLBACK_VASICEK
        converged = False
        used_fallback = True

    n_steps = req.horizon_months * 21
    dt = 1 / 252
    paths = vasicek_sim(req.current_rate, params, req.n_paths, n_steps, dt)

    elapsed_ms = (time.perf_counter() - t0) * 1000
    response = _build_vasicek_response(req, paths, params, elapsed_ms, False, converged, used_fallback)

    await set_cached(cache_key, response.model_dump())
    return response


@router.post("/cir", response_model=SimulationResponse)
async def simulate_cir(req: SimulationRequest):
    cache_key = make_cache_key("cir", req.current_rate, req.horizon_months, req.n_paths)

    cached = await get_cached(cache_key)
    if cached:
        cached["cache_hit"] = True
        return SimulationResponse(**cached)

    t0 = time.perf_counter()

    _, c_params, _, c_rmse = get_calibrated_params()
    if req.use_calibrated and c_params:
        params = c_params
        converged = True
        used_fallback = False
    elif req.model_params.kappa is not None:
        params = CIRParams(
            kappa=req.model_params.kappa,
            theta=req.model_params.theta,
            sigma=req.model_params.sigma,
        )
        converged = True
        used_fallback = False
    else:
        params = FALLBACK_CIR
        converged = False
        used_fallback = True

    n_steps = req.horizon_months * 21
    dt = 1 / 252
    paths = cir_sim(req.current_rate, params, req.n_paths, n_steps, dt)

    elapsed_ms = (time.perf_counter() - t0) * 1000
    response = _build_cir_response(req, paths, params, elapsed_ms, False, converged, used_fallback)

    await set_cached(cache_key, response.model_dump())
    return response


@router.post("/compare", response_model=CompareResponse)
async def simulate_compare(req: SimulationRequest):
    v_req = SimulationRequest(**req.model_dump())
    c_req = SimulationRequest(**req.model_dump())

    v_response = await simulate_vasicek(v_req)
    c_response = await simulate_cir(c_req)

    _, _, v_rmse, c_rmse = get_calibrated_params()
    recommended = "vasicek" if v_rmse <= c_rmse else "cir"

    return CompareResponse(
        vasicek=v_response,
        cir=c_response,
        vasicek_rmse=v_rmse,
        cir_rmse=c_rmse,
        recommended_model=recommended,
    )
