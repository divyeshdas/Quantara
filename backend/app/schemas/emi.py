from pydantic import BaseModel, Field
from typing import Literal


class EMIRequest(BaseModel):
    loan_amount: float = Field(..., ge=100000, le=500000000, description="Loan principal in INR")
    current_rate: float = Field(..., ge=1.0, le=25.0, description="Current repo rate in %")
    tenure_months: int = Field(..., ge=12, le=360)
    loan_type: Literal["home", "personal", "business"] = "home"
    bank_spread: float = Field(2.5, ge=0.0, le=10.0, description="Bank spread over repo in %")
    horizon_months: int = Field(12, ge=1, le=24)
    n_paths: int = Field(10000, ge=1000, le=50000)


class EMIScenario(BaseModel):
    rate: float
    emi: float
    total_payment: float
    total_interest: float
    label: str


class EMIDistribution(BaseModel):
    p5: float
    p25: float
    p50: float
    p75: float
    p95: float
    mean: float
    std: float


class EMIResponse(BaseModel):
    scenarios: list[EMIScenario]
    emi_distribution: EMIDistribution
    current_emi: float
    max_additional_monthly: float
    max_additional_tenure: float
