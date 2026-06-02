import pandas as pd
import numpy as np
from pathlib import Path


DATA_FILE = Path(__file__).parent / "rbi_repo_rates.csv"


def load_rbi_rates() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def get_rate_series() -> np.ndarray:
    """Returns the full rate series as a numpy array (percentage values)."""
    df = load_rbi_rates()
    return df["rate"].values


def get_current_rate() -> float:
    df = load_rbi_rates()
    return float(df["rate"].iloc[-1])


def get_historical_for_api() -> list[dict]:
    df = load_rbi_rates()
    return [
        {"date": row["date"].strftime("%Y-%m-%d"), "rate": float(row["rate"])}
        for _, row in df.iterrows()
    ]


def expand_to_daily(df: pd.DataFrame) -> pd.DataFrame:
    """
    Forward-fill RBI decision dates to daily frequency.
    Useful for calibration which expects a dense time series.
    """
    df = df.set_index("date")
    daily_idx = pd.date_range(df.index.min(), df.index.max(), freq="B")
    df = df.reindex(daily_idx, method="ffill")
    df.index.name = "date"
    return df.reset_index()
