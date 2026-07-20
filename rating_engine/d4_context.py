"""D4 — Contesto Partita (peso 20%).

Clutch index: peso di ogni contributo in base al momento della partita
e allo stato del punteggio.
"""

import pandas as pd
import numpy as np

POSITIVE_TYPES = {
    "Shot", "Pass", "Dribble", "Carry", "Interception",
    "Ball Recovery", "Clearance", "Block", "Goal Keeper",
}
NEGATIVE_TYPES = {"Foul Committed", "Bad Behaviour", "Error"}


def _minute_weight(minute: float, period: int) -> float:
    if period >= 3:
        return 2.0
    if minute >= 75:
        return 1.6
    if minute >= 60:
        return 1.3
    if minute >= 45:
        return 1.1
    return 1.0


def _game_state_weight(score_diff: int) -> float:
    diff = abs(score_diff)
    if diff == 0:
        return 1.5
    if diff == 1:
        return 1.2
    if diff == 2:
        return 0.8
    return 0.5


def _build_running_score(events: pd.DataFrame) -> dict:
    """Ritorna {event_index: {team_id: goals_so_far}} al momento di ogni evento."""
    running: dict = {}
    cumulative: dict = {}
    if "type" not in events.columns:
        return {}
    goals = events[(events["type"] == "Shot") & (events.get("shot_outcome", pd.Series()) == "Goal")]
    goal_set = set(goals.index)

    for idx in events.index:
        if idx in goal_set:
            row = events.loc[idx]
            tid = row.get("team_id")
            cumulative[tid] = cumulative.get(tid, 0) + 1
        running[idx] = dict(cumulative)
    return running


def compute(events: pd.DataFrame, positions: dict[int, str]) -> pd.Series:
    if "type" not in events.columns:
        return pd.Series(dtype=float, name="d4_raw")

    ev = events.copy()
    ev["player_id"] = pd.to_numeric(ev.get("player_id", pd.Series(dtype=float)), errors="coerce")

    running_score = _build_running_score(ev)
    all_teams = list(ev["team_id"].dropna().unique()) if "team_id" in ev.columns else []

    player_team: dict = {}
    for _, row in ev.dropna(subset=["player_id", "team_id"]).iterrows():
        player_team[int(row["player_id"])] = row["team_id"]

    def opp(my_team):
        others = [t for t in all_teams if t != my_team]
        return others[0] if others else None

    scores: dict[int, float] = {}

    for pid in ev["player_id"].dropna().unique():
        pid = int(pid)
        p = ev[ev["player_id"] == pid]
        my_team = player_team.get(pid)
        opp_team = opp(my_team)
        clutch = 0.0

        for idx, row in p.iterrows():
            ev_type = row.get("type", "")
            minute = float(row.get("minute", 45))
            period = int(row.get("period", 1))
            mw = _minute_weight(minute, period)

            state = running_score.get(idx, {})
            my_g = state.get(my_team, 0)
            opp_g = state.get(opp_team, 0) if opp_team else 0
            gw = _game_state_weight(my_g - opp_g)

            weight = mw * gw

            if ev_type in POSITIVE_TYPES:
                bonus = 0.1
                if ev_type == "Shot":
                    xg = float(row.get("shot_statsbomb_xg") or 0)
                    bonus += xg * 2.0
                    if row.get("shot_outcome") == "Goal":
                        bonus += 3.0
                elif ev_type == "Pass":
                    if row.get("pass_goal_assist"):
                        bonus += 2.5
                    elif row.get("pass_shot_assist"):
                        bonus += 1.0
                clutch += bonus * weight
            elif ev_type in NEGATIVE_TYPES:
                clutch -= 0.3 * weight

        scores[pid] = clutch

    return pd.Series(scores, name="d4_raw")
