from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal


class ModelParamsInput(BaseModel):
    kappa: Optional[float] = None
    theta: Optional[float] = None
    sigma: Optional[float] = None


class SimulationRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    current_rate: float = Field(..., ge=0.0, le=25.0, description="Current repo rate in %")
    horizon_months: int = Field(12, ge=1, le=24)
    n_paths: int = Field(10000, ge=1000, le=50000)
    model_params: ModelParamsInput = ModelParamsInput()
    use_calibrated: bool = True


class PathsSummary(BaseModel):
    p5: list[float]
    p25: list[float]
    p50: list[float]
    p75: list[float]
    p95: list[float]
    mean: list[float]


class TerminalDistribution(BaseModel):
    mean: float
    std: float
    p5: float
    p25: float
    p50: float
    p75: float
    p95: float


class CalibratedParams(BaseModel):
    kappa: float
    theta: float
    sigma: float


class SimulationResponse(BaseModel):
    model: str
    paths_summary: PathsSummary
    terminal_distribution: TerminalDistribution
    calibrated_params: CalibratedParams
    time_axis: list[float]
    feller_condition_met: Optional[bool] = None
    feller_margin: Optional[float] = None
    negative_rate_probability: Optional[float] = None
    prob_increase: float
    prob_decrease: float
    computation_time_ms: float
    cache_hit: bool
    calibration_converged: bool
    used_fallback_params: bool


class CompareResponse(BaseModel):
    vasicek: SimulationResponse
    cir: SimulationResponse
    vasicek_rmse: float
    cir_rmse: float
    recommended_model: str
