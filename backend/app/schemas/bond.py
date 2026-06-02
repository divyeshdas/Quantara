from pydantic import BaseModel, Field
from typing import Literal


class BondRequest(BaseModel):
    face_value: float = Field(1000, ge=100)
    coupon_rate: float = Field(..., ge=0.0, le=30.0, description="Annual coupon in %")
    maturity_years: float = Field(..., ge=0.5, le=30.0)
    current_rate: float = Field(..., ge=0.0, le=25.0)
    model: Literal["vasicek", "cir"] = "cir"
    horizon_months: int = Field(12, ge=1, le=24)
    n_paths: int = Field(10000, ge=1000, le=50000)
    frequency: int = Field(2, ge=1, le=4)


class BondPriceDistribution(BaseModel):
    p5: float
    p25: float
    p50: float
    p75: float
    p95: float
    mean: float
    std: float


class BondResponse(BaseModel):
    current_price: float
    price_distribution: BondPriceDistribution
    modified_duration: float
    convexity: float
    terminal_rates_sample: list[float]
    price_sample: list[float]
    ytm_at_median_rate: float
