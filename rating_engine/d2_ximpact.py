"""D2 — xImpact (peso 25%)."""

import pandas as pd
import numpy as np


def _xg_of_next_shot(events: pd.DataFrame, pass_id) -> float:
    """xG del tiro che segue un dato key_pass_id."""
    shots = events[events["type"] == "Shot"] if "type" in events.columns else events.iloc[0:0]
    if "shot_key_pass_id" not in shots.columns:
        return 0.0
    match = shots[shots["shot_key_pass_id"] == pass_id]
    return float(match["shot_statsbomb_xg"].fillna(0).iloc[0]) if not match.empty else 0.0


def compute(events: pd.DataFrame, positions: dict[int, str]) -> pd.Series:
    if "type" not in events.columns:
        return pd.Series(dtype=float, name="d2_raw")

    ev = events.copy()
    ev["player_id"] = pd.to_numeric(ev.get("player_id", pd.Series(dtype=float)), errors="coerce")

    # pre-calcola xG per possesso e giocatori presenti in ogni possesso
    shots = ev[ev["type"] == "Shot"].copy()
    shots["xg"] = pd.to_numeric(shots.get("shot_statsbomb_xg", 0), errors="coerce").fillna(0)

    poss_xg: dict = {}
    poss_players: dict = {}
    if "possession" in ev.columns:
        for poss, grp in ev.groupby("possession"):
            poss_players[poss] = set(grp["player_id"].dropna().astype(int))
        for _, sh in shots.iterrows():
            poss = sh.get("possession")
            if poss is not None:
                poss_xg.setdefault(poss, []).append((sh.get("player_id"), float(sh["xg"])))

    scores: dict[int, float] = {}

    for pid in ev["player_id"].dropna().unique():
        pid = int(pid)
        p = ev[ev["player_id"] == pid]

        # xG own
        my_shots = p[p["type"] == "Shot"]
        xg_own = pd.to_numeric(my_shots.get("shot_statsbomb_xg", 0), errors="coerce").fillna(0).sum()

        # xG assist (key pass → cerca il tiro collegato)
        xg_assist = 0.0
        if "pass_shot_assist" in p.columns and "id" in p.columns:
            kp = p[p["pass_shot_assist"].fillna(False).astype(bool)]
            for _, row in kp.iterrows():
                xg_assist += _xg_of_next_shot(ev, row["id"])

        # xG chain: ogni possesso in cui il giocatore è presente e finisce con tiro altrui
        xg_chain = 0.0
        if "possession" in ev.columns:
            my_poss = set(p["possession"].dropna().unique())
            for poss in my_poss:
                n_players = len(poss_players.get(poss, {pid}))
                for shooter_pid, xg_val in poss_xg.get(poss, []):
                    if shooter_pid != pid:
                        xg_chain += xg_val / max(n_players, 1)

        # xG pressure proxy: pressioni che causano turnover immediato
        xg_pressure = 0.0
        pressures = p[p["type"] == "Pressure"]
        if not pressures.empty:
            ev_sorted = ev.sort_index()
            my_team = p.iloc[0].get("team_id") if "team_id" in p.columns else None
            for idx in pressures.index:
                next_ev = ev_sorted[ev_sorted.index > idx].head(3)
                if not next_ev.empty:
                    nt = next_ev["type"].iloc[0] if "type" in next_ev.columns else ""
                    nt_team = next_ev.iloc[0].get("team_id")
                    if nt in ("Ball Recovery", "Interception") and nt_team == my_team:
                        xg_pressure += 0.05

        score = (
            float(xg_own) * 2.5 +
            float(xg_assist) * 2.0 +
            float(xg_chain) * 0.8 +
            float(xg_pressure) * 1.0
        )
        scores[pid] = score

    return pd.Series(scores, name="d2_raw")
