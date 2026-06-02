import numpy as np
import time


PERCENTILES = [5, 25, 50, 75, 95]


def summarise_paths(paths: np.ndarray) -> dict:
    """
    Reduce (n_paths, n_steps+1) array to percentile bands + mean.
    Returns dict suitable for JSON serialisation.
    """
    pcts = np.percentile(paths, PERCENTILES, axis=0)
    return {
        "p5": pcts[0].tolist(),
        "p25": pcts[1].tolist(),
        "p50": pcts[2].tolist(),
        "p75": pcts[3].tolist(),
        "p95": pcts[4].tolist(),
        "mean": paths.mean(axis=0).tolist(),
    }


def terminal_stats(paths: np.ndarray) -> dict:
    terminal = paths[:, -1]
    return {
        "mean": float(np.mean(terminal)),
        "std": float(np.std(terminal)),
        "p5": float(np.percentile(terminal, 5)),
        "p25": float(np.percentile(terminal, 25)),
        "p50": float(np.percentile(terminal, 50)),
        "p75": float(np.percentile(terminal, 75)),
        "p95": float(np.percentile(terminal, 95)),
    }


def rate_change_probabilities(paths: np.ndarray, r0: float) -> dict:
    terminal = paths[:, -1]
    return {
        "prob_increase": float(np.mean(terminal > r0)),
        "prob_decrease": float(np.mean(terminal < r0)),
        "prob_unchanged": float(np.mean(terminal == r0)),
    }


def make_time_axis(horizon_months: int, n_steps: int) -> list[float]:
    """Return time axis in months, length n_steps+1."""
    total_years = horizon_months / 12
    return (np.linspace(0, total_years * 12, n_steps + 1)).tolist()
