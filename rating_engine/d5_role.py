"""D5 — Role Fulfillment (peso 15%).

Cosine similarity tra profilo azioni reale e profilo atteso per il ruolo.
"""

import pandas as pd
import numpy as np
from d1_direct import POSITION_GROUP_MAP

ROLE_PROFILES: dict[str, dict[str, float]] = {
    "GK":  {"Goal Keeper": 0.35, "Pass": 0.35, "Clearance": 0.10, "Ball Recovery": 0.08,
             "Duel": 0.05, "Shot": 0.02, "Pressure": 0.05},
    "CB":  {"Pass": 0.30, "Clearance": 0.15, "Duel": 0.15, "Interception": 0.10,
             "Block": 0.08, "Pressure": 0.10, "Ball Recovery": 0.07, "Carry": 0.05},
    "FB":  {"Pass": 0.28, "Carry": 0.12, "Duel": 0.12, "Pressure": 0.12,
             "Dribble": 0.08, "Interception": 0.08, "Ball Recovery": 0.08,
             "Clearance": 0.06, "Shot": 0.03, "Block": 0.03},
    "CM":  {"Pass": 0.40, "Carry": 0.15, "Pressure": 0.15, "Duel": 0.10,
             "Ball Recovery": 0.08, "Interception": 0.06, "Shot": 0.04, "Dribble": 0.02},
    "AM":  {"Pass": 0.30, "Carry": 0.15, "Dribble": 0.12, "Shot": 0.12,
             "Pressure": 0.10, "Ball Recovery": 0.06, "Duel": 0.08,
             "Interception": 0.04, "Block": 0.03},
    "FW":  {"Shot": 0.20, "Pass": 0.20, "Carry": 0.15, "Dribble": 0.15,
             "Pressure": 0.12, "Duel": 0.10, "Ball Recovery": 0.05, "Interception": 0.03},
}

ALL_TYPES = sorted({t for profile in ROLE_PROFILES.values() for t in profile})


def _vec(profile: dict[str, float]) -> np.ndarray:
    return np.array([profile.get(t, 0.0) for t in ALL_TYPES])


def compute(events: pd.DataFrame, positions: dict[int, str]) -> pd.Series:
    if "type" not in events.columns:
        return pd.Series(dtype=float, name="d5_raw")

    ev = events.copy()
    ev["player_id"] = pd.to_numeric(ev.get("player_id", pd.Series(dtype=float)), errors="coerce")
    scores: dict[int, float] = {}

    for pid in ev["player_id"].dropna().unique():
        pid = int(pid)
        p = ev[ev["player_id"] == pid]
        grp = POSITION_GROUP_MAP.get(positions.get(pid, "Unknown"), "CM")
        expected = _vec(ROLE_PROFILES.get(grp, ROLE_PROFILES["CM"]))

        counts = p["type"].value_counts()
        total = counts.sum()
        actual = np.array([counts.get(t, 0) / total for t in ALL_TYPES]) if total > 0 else np.zeros(len(ALL_TYPES))

        denom = np.linalg.norm(expected) * np.linalg.norm(actual)
        cos_sim = float(np.dot(expected, actual) / denom) if denom > 0 else 0.0
        scores[pid] = (cos_sim + 1) / 2  # scala 0-1

    return pd.Series(scores, name="d5_raw")
