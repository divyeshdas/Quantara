import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import get_settings
from app.core.redis import close_redis
from app.api.v1 import simulate, calibrate, emi, bond, rates
from app.api.v1.simulate import set_calibrated_params
from data.rbi_provider import load_rbi_rates, expand_to_daily
from quant_engine.calibration import calibrate_vasicek, calibrate_cir


def run_calibration():
    df = load_rbi_rates()
    daily_df = expand_to_daily(df)
    rate_series = daily_df["rate"].values

    v_result = calibrate_vasicek(rate_series)
    c_result = calibrate_cir(rate_series)

    set_calibrated_params(
        v_result.params,
        c_result.params,
        v_result.rmse,
        c_result.rmse,
    )
    print(f"Calibration done — Vasicek: κ={v_result.params.kappa:.4f} θ={v_result.params.theta:.4f} σ={v_result.params.sigma:.4f}")
    print(f"Calibration done — CIR:     κ={c_result.params.kappa:.4f} θ={c_result.params.theta:.4f} σ={c_result.params.sigma:.4f}")


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_calibration()
    scheduler.add_job(run_calibration, "interval", hours=24)
    scheduler.start()
    yield
    scheduler.shutdown()
    await close_redis()


settings = get_settings()

app = FastAPI(
    title="RateSimulator API",
    description="RBI interest rate path simulation using Vasicek and CIR stochastic models",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rates.router, prefix="/api/v1/rates", tags=["rates"])
app.include_router(simulate.router, prefix="/api/v1/simulate", tags=["simulate"])
app.include_router(calibrate.router, prefix="/api/v1/calibrate", tags=["calibrate"])
app.include_router(emi.router, prefix="/api/v1/emi", tags=["emi"])
app.include_router(bond.router, prefix="/api/v1/bond", tags=["bond"])


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
