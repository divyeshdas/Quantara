from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from ..core.database import Base


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True)
    model = Column(String(16), nullable=False)
    current_rate = Column(Float, nullable=False)
    horizon_months = Column(Integer, nullable=False)
    n_paths = Column(Integer, nullable=False)
    kappa = Column(Float)
    theta = Column(Float)
    sigma = Column(Float)
    terminal_mean = Column(Float)
    terminal_std = Column(Float)
    computation_time_ms = Column(Float)
    cache_hit = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CalibrationSnapshot(Base):
    __tablename__ = "calibration_snapshots"

    id = Column(Integer, primary_key=True)
    model = Column(String(16), nullable=False)
    kappa = Column(Float, nullable=False)
    theta = Column(Float, nullable=False)
    sigma = Column(Float, nullable=False)
    rmse = Column(Float)
    converged = Column(Boolean, default=True)
    log_likelihood = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
