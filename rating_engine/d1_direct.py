"""D1 — Azioni Dirette (peso 20%).

Calcola un punteggio grezzo per ogni giocatore basato sulle azioni
statisticamente rilevabili, normalizzate per ruolo.

Nomi colonna StatsBomb (flatten_attrs=True):
  type, player, player_id, team, team_id, position
  shot_outcome, shot_statsbomb_xg
  pass_outcome, pass_goal_assist, pass_shot_assist, pass_end_location
  dribble_outcome, duel_outcome, duel_type
  interception_outcome, goalkeeper_outcome, goalkeeper_type
  foul_committed_card, carry_end_location
"""

import pandas as pd
import numpy as np

ACTION_WEIGHTS = {
    "goal":               10.0,
    "assist":              7.0,
    "shot_on_target":      1.5,
    "shot_off_target":    -0.3,
    "key_pass":            2.5,
    "pass_completed":      0.04,   # ridotto: volume passaggi semplici conta poco
    "pass_failed":        -0.1,
    "dribble_complete":    1.2,
    "dribble_failed":     -0.3,
    "tackle_won":          1.5,
    "aerial_won":          0.7,
    "aerial_lost":        -0.2,
    "interception":        1.8,
    "clearance":           0.8,
    "block":               1.0,
    "save":                2.5,
    "error_leading_shot": -3.0,
    "foul_committed":     -0.5,
    "yellow_card":        -2.0,
    "red_card":           -6.0,
    "progressive_carry":   0.4,
    "progressive_pass":    0.8,   # alzato: passaggi progressivi valgono 20x quelli semplici
}

ROLE_MULTIPLIERS = {
    "GK":  {"save": 2.0, "clearance": 1.5, "pass_completed": 0.3, "goal": 5.0},
    "CB":  {"tackle_won": 1.5, "interception": 1.5, "clearance": 1.8, "aerial_won": 1.6,
             "dribble_complete": 2.0, "key_pass": 1.3},
    "FB":  {"tackle_won": 1.2, "dribble_complete": 1.4, "key_pass": 1.5, "progressive_carry": 1.5},
    "CM":  {"key_pass": 1.3, "progressive_pass": 1.5, "progressive_carry": 1.3, "tackle_won": 1.1},
    "AM":  {"key_pass": 1.5, "dribble_complete": 1.3, "shot_on_target": 1.2, "goal": 1.0},
    "FW":  {"goal": 1.2, "shot_on_target": 1.3, "dribble_complete": 1.2, "key_pass": 1.1},
}

POSITION_GROUP_MAP = {
    "Goalkeeper":                   "GK",
    "Right Back":                   "FB", "Left Back":             "FB",
    "Right Wing Back":              "FB", "Left Wing Back":        "FB",
    "Center Back":                  "CB",
    "Right Center Back":            "CB", "Left Center Back":      "CB",
    "Defensive Midfield":           "CM",
    "Central Midfield":             "CM", "Left Midfield":         "CM",
    "Right Midfield":               "CM",
    "Left Defensive Midfield":      "CM", "Right Defensive Midfield": "CM",
    "Left Center Midfield":         "CM", "Right Center Midfield":    "CM",
    "Attacking Midfield":           "AM",
    "Left Wing":                    "AM", "Right Wing":            "AM",
    "Center Forward":               "FW",
    "Left Center Forward":          "FW", "Right Center Forward":  "FW",
    "Secondary Striker":            "FW",
}


def _position_group(position_name: str) -> str:
    return POSITION_GROUP_MAP.get(position_name, "CM")


def _col(df: pd.DataFrame, name: str, default=False) -> pd.Series:
    return df[name] if name in df.columns else pd.Series(default, index=df.index)


def compute(events: pd.DataFrame, positions: dict[int, str]) -> pd.Series:
    scores: dict[int, float] = {}
    ev = events.copy()
    ev["player_id"] = pd.to_numeric(ev.get("player_id", pd.Series(dtype=float)), errors="coerce")

    for pid in ev["player_id"].dropna().unique():
        pid = int(pid)
        p = ev[ev["player_id"] == pid]
        grp = _position_group(positions.get(pid, "Unknown"))

        def w(action: str) -> float:
            return ACTION_WEIGHTS.get(action, 0) * ROLE_MULTIPLIERS.get(grp, {}).get(action, 1.0)

        score = 0.0
        ev_type = _col(p, "type")

        # --- tiri ---
        shot_mask = ev_type == "Shot"
        shot_out = _col(p, "shot_outcome")
        score += (shot_mask & (shot_out == "Goal")).sum() * w("goal")
        score += (shot_mask & shot_out.isin(["Saved", "Goal"])).sum() * w("shot_on_target")
        score += (shot_mask & shot_out.isin(["Off T", "Wayward", "Post"])).sum() * w("shot_off_target")

        # --- assist e key pass ---
        score += _col(p, "pass_goal_assist", False).fillna(False).astype(bool).sum() * w("assist")
        score += _col(p, "pass_shot_assist", False).fillna(False).astype(bool).sum() * w("key_pass")

        # --- passaggi ---
        pass_mask = ev_type == "Pass"
        pass_out = _col(p, "pass_outcome")
        score += (pass_mask & (pass_out.isna() | (pass_out == ""))).sum() * w("pass_completed")
        score += (pass_mask & pass_out.isin(["Incomplete", "Out", "Pass Offside"])).sum() * w("pass_failed")

        # progressive pass: end_x > 60 e avanza > 10m
        if "pass_end_location" in p.columns and "location" in p.columns:
            passes = p[pass_mask]
            prog = passes[passes.apply(
                lambda r: isinstance(r.get("pass_end_location"), list) and
                          isinstance(r.get("location"), list) and
                          r["pass_end_location"][0] > 60 and
                          (r["pass_end_location"][0] - r["location"][0]) > 10,
                axis=1
            )]
            score += len(prog) * w("progressive_pass")

        # --- dribbling ---
        drib_mask = ev_type == "Dribble"
        drib_out = _col(p, "dribble_outcome")
        score += (drib_mask & (drib_out == "Complete")).sum() * w("dribble_complete")
        score += (drib_mask & (drib_out == "Incomplete")).sum() * w("dribble_failed")

        # --- progressive carry ---
        if "carry_end_location" in p.columns and "location" in p.columns:
            carries = p[ev_type == "Carry"]
            prog_c = carries[carries.apply(
                lambda r: isinstance(r.get("carry_end_location"), list) and
                          isinstance(r.get("location"), list) and
                          r["carry_end_location"][0] > 60 and
                          (r["carry_end_location"][0] - r["location"][0]) > 10,
                axis=1
            )]
            score += len(prog_c) * w("progressive_carry")

        # --- duelli ---
        duel_mask = ev_type == "Duel"
        duel_type = _col(p, "duel_type")
        duel_out = _col(p, "duel_outcome")
        tackle_won = duel_mask & (duel_type == "Tackle") & duel_out.isin(["Won", "Success In Play", "Success Out"])
        score += tackle_won.sum() * w("tackle_won")
        aerial_won = duel_mask & (duel_type == "Aerial Lost") & duel_out.isin(["Won", "Success In Play", "Success Out"])
        score += aerial_won.sum() * w("aerial_won")
        aerial_lost = duel_mask & (duel_type == "Aerial Lost") & duel_out.isin(["Lost In Play", "Lost Out"])
        score += aerial_lost.sum() * w("aerial_lost")

        # --- interception ---
        inter_mask = ev_type == "Interception"
        inter_out = _col(p, "interception_outcome")
        score += (inter_mask & inter_out.isin(["Won", "Success", "Success In Play", "Success Out"])).sum() * w("interception")

        # --- clearance / block ---
        score += (ev_type == "Clearance").sum() * w("clearance")
        score += (ev_type == "Block").sum() * w("block")

        # --- portiere: salvataggi ---
        gk_mask = ev_type == "Goal Keeper"
        gk_out = _col(p, "goalkeeper_outcome")
        saves = gk_mask & gk_out.isin(["Saved Twice", "Success", "No Touch", "Touched Out"])
        score += saves.sum() * w("save")

        # --- falli e cartellini ---
        score += (ev_type == "Foul Committed").sum() * w("foul_committed")
        card = _col(p, "foul_committed_card")
        score += (card == "Yellow Card").sum() * w("yellow_card")
        score += (card == "Red Card").sum() * w("red_card")
        score += (card == "Second Yellow").sum() * (w("yellow_card") + w("red_card"))

        scores[pid] = score

    return pd.Series(scores, name="d1_raw")
