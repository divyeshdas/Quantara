import requests
import pandas as pd
import numpy as np
from typing import Optional


FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"


def fetch_fred_series(
    series_id: str,
    api_key: str,
    start_date: str = "2011-01-01",
) -> Optional[pd.DataFrame]:
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
        "frequency": "m",
    }
    try:
        r = requests.get(FRED_BASE, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        obs = data.get("observations", [])
        df = pd.DataFrame(obs)[["date", "value"]]
        df["date"] = pd.to_datetime(df["date"])
        df["rate"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["rate"])[["date", "rate"]]
        return df.sort_values("date").reset_index(drop=True)
    except Exception:
        return None


def get_india_gsec_10y(api_key: str) -> Optional[np.ndarray]:
    """Fetch India 10Y G-Sec yields from FRED (IRLTLT01INM156N)."""
    df = fetch_fred_series("IRLTLT01INM156N", api_key)
    if df is not None:
        return df["rate"].values
    return None
