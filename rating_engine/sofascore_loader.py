"""Loader alternativo: dati da Sofascore via RapidAPI.

Usa gli stessi due endpoint del proxy Netlify:
  - /matches/get-lineups?matchId={eventId}   → stats per giocatore
  - /matches/get-incidents?matchId={eventId} → gol, cartellini, sostituzioni

La chiave viene letta da env var RAPIDAPI_KEY o da file .env nella stessa directory.

Uso:
    from sofascore_loader import load_match_sofascore
    events, positions = load_match_sofascore("15186798")
"""

import os
import json
import urllib.request
import urllib.error
import pathlib
import pandas as pd

RAPIDAPI_HOST = "sofascore.p.rapidapi.com"


def _load_env():
    """Carica .env dalla directory del file se RAPIDAPI_KEY non è già in env."""
    if os.environ.get("RAPIDAPI_KEY"):
        return
    env_path = pathlib.Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _rapidapi_get(path: str, retries: int = 3, timeout: int = 15) -> dict:
    _load_env()
    key = os.environ.get("RAPIDAPI_KEY", "")
    if not key:
        raise RuntimeError(
            "RAPIDAPI_KEY non trovata.\n"
            "Crea rating_engine/.env con:\n  RAPIDAPI_KEY=la_tua_chiave"
        )
    url = f"https://{RAPIDAPI_HOST}{path}"
    req = urllib.request.Request(url, headers={
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key":  key,
        "Accept": "application/json",
    })
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"RapidAPI HTTP {e.code} su {path}") from e
        except Exception as e:
            last_err = e
            if attempt < retries:
                import time
                print(f"    Timeout (tentativo {attempt}/{retries}), riprovo...")
                time.sleep(2)
    raise RuntimeError(f"RapidAPI fallito dopo {retries} tentativi su {path}") from last_err


# ── mapping posizione Sofascore → position_group del modello ──────────────────
_POS_MAP = {
    "G":  "Goalkeeper",
    "GK": "Goalkeeper",
    "D":  "Center Back",
    "DC": "Center Back",   "DL": "Left Back",    "DR": "Right Back",
    "WB": "Right Wing Back",
    "M":  "Central Midfield",
    "MC": "Central Midfield", "ML": "Left Midfield", "MR": "Right Midfield",
    "AM": "Attacking Midfield", "DM": "Defensive Midfield",
    "F":  "Center Forward",
    "ST": "Center Forward", "SS": "Secondary Striker",
    "LW": "Left Wing",     "RW": "Right Wing",
}


def _map_position(pos: str | None) -> str:
    return _POS_MAP.get((pos or "M").upper(), "Central Midfield")


# ── parsing incidents → gol per minuto, cartellini ───────────────────────────
def _parse_incidents(incidents: dict) -> tuple[dict, dict, dict]:
    """
    Ritorna:
      goals_by_player  = {player_name: [(minute, team_id), ...]}
      cards_by_player  = {player_name: {amm, esp}}
      subs_by_player   = {player_name: minute_in or minute_out}
    """
    goals: dict = {}
    cards: dict = {}
    subs:  dict = {}

    for inc in (incidents.get("incidents") or []):
        itype  = inc.get("incidentType", "")
        iclass = inc.get("incidentClass", "")
        minute = inc.get("time", 0) + inc.get("addedTime", 0)
        player = (inc.get("player") or {}).get("name")
        team_id = inc.get("team", {}).get("id") if inc.get("team") else None

        if itype == "goal" and player:
            goals.setdefault(player, []).append((minute, team_id))

        elif itype == "card" and player:
            entry = cards.setdefault(player, {"amm": False, "esp": False})
            if iclass == "yellow":
                entry["amm"] = True
            elif iclass in ("red", "yellowRed"):
                entry["esp"] = True
                entry["amm"] = False

        elif itype == "substitution":
            pin  = (inc.get("playerIn")  or {}).get("name")
            pout = (inc.get("playerOut") or {}).get("name")
            if pin:  subs[pin]  = {"in":  minute}
            if pout: subs[pout] = {"out": minute}

    return goals, cards, subs


# ── costruisce il DataFrame eventi compatibile con il modello ─────────────────
def _build_events(lineups: dict, incidents: dict, match_id: str) -> pd.DataFrame:
    """
    Trasforma lineups + incidents in un DataFrame "events" compatibile
    con le dimensioni del modello di rating.

    Colonne generate (sottoinsieme delle colonne StatsBomb):
      player_id, player, team_id, team, position, minute, period, type,
      shot_statsbomb_xg, shot_outcome, pass_goal_assist, pass_shot_assist,
      duel_type, duel_outcome, interception_outcome, goalkeeper_outcome,
      foul_committed_card, location, carry_end_location, pass_end_location,
      possession (proxy), pass_recipient_id
    """
    goals_by_player, cards_by_player, subs_by_player = _parse_incidents(incidents)

    # pre-calcola gol segnati per ciascuna squadra (dalla somma dei gol dei giocatori).
    # teamId è nel player entry, NON in lineups["home"]["team"] (che non esiste nell'API).
    team_goals: dict[int, int] = {}
    for side in ("home", "away"):
        players_list = (lineups.get(side, {}).get("players") or [])
        tid = (players_list[0] or {}).get("teamId", 0) if players_list else 0
        total = sum(
            int((entry.get("statistics") or {}).get("goals") or 0)
            for entry in players_list
        )
        team_goals[tid] = total

    rows = []

    for side in ("home", "away"):
        team_data = lineups.get(side, {})
        team_name = (team_data.get("team") or {}).get("name", side)
        players   = team_data.get("players") or []
        # team_id di squadra: da primo giocatore (l'header di lineups non espone teamId)
        team_id   = (players[0] or {}).get("teamId", 0) if players else 0
        # gol subiti da questa squadra = gol segnati dall'altra
        opp_goals = sum(v for k, v in team_goals.items() if k != team_id)

        for entry in players:
            p      = entry.get("player") or {}
            stats  = entry.get("statistics") or {}
            pid    = p.get("id", 0)
            pname  = p.get("name", "Unknown")
            pos    = _map_position(entry.get("position") or p.get("position"))
            mins   = int(stats.get("minutesPlayed") or 0)
            sofa_rating = stats.get("rating")
            # teamId per-player (più affidabile del team-level)
            entry_team_id = entry.get("teamId", team_id)
            # inietta gol subiti per TUTTI i giocatori (GK: clean sheet; difensori: malus)
            stats = dict(stats)  # copia per non mutare il dict originale
            stats["_goals_against"] = sum(v for k, v in team_goals.items() if k != entry_team_id)

            if mins == 0 and not stats.get("goals"):
                continue  # non entrato

            base = {
                "player_id": float(pid),
                "player":    pname,
                "team_id":   entry_team_id,
                "team":      team_name,
                "position":  pos,
                "period":    1,
                "possession": pid,  # proxy: ogni giocatore ha il suo "possesso"
                "location":  None,
                "carry_end_location": None,
                "pass_end_location":  None,
                "pass_recipient_id":  None,
                "shot_statsbomb_xg":  None,
                "shot_outcome":       None,
                "pass_goal_assist":   False,
                "pass_shot_assist":   False,
                "duel_type":          None,
                "duel_outcome":       None,
                "interception_outcome": None,
                "goalkeeper_outcome": None,
                "foul_committed_card": None,
                "match_id": match_id,
                "_sofa_rating": sofa_rating,
                "_sofa_stats": stats,
            }

            # --- sintetizza eventi dal box score ---

            # Gol segnati
            for _ in range(int(stats.get("goals") or 0)):
                player_goals = goals_by_player.get(pname, [(45, team_id)])
                minute = player_goals[0][0] if player_goals else 45
                rows.append({**base, "type": "Shot", "minute": minute,
                             "shot_outcome": "Goal", "shot_statsbomb_xg": 0.5})

            # Assist
            for _ in range(int(stats.get("goalAssist") or 0)):
                rows.append({**base, "type": "Pass", "minute": 45,
                             "pass_goal_assist": True, "pass_shot_assist": True})

            # Tiri in porta (no gol)
            for _ in range(max(0, int(stats.get("onTargetScoringAttempt") or 0) - int(stats.get("goals") or 0))):
                rows.append({**base, "type": "Shot", "minute": 45,
                             "shot_outcome": "Saved", "shot_statsbomb_xg": 0.12})

            # Tiri fuori
            for _ in range(int(stats.get("blockedScoringAttempt") or stats.get("totalShot", 0) or 0)
                           - int(stats.get("onTargetScoringAttempt") or 0)):
                if _ < 0: break
                rows.append({**base, "type": "Shot", "minute": 45,
                             "shot_outcome": "Blocked", "shot_statsbomb_xg": 0.05})

            # Passaggi accurati: separa long ball (proxy progressivo) da passaggi semplici.
            # accurateLongBalls è incluso in accuratePass → sottraiamo per non doppiare.
            accurate   = int(stats.get("accuratePass") or stats.get("totalPass") or 0)
            long_balls = int(stats.get("accurateLongBalls") or 0)
            simple     = max(0, accurate - long_balls)
            for _ in range(simple):
                rows.append({**base, "type": "Pass", "minute": 45, "pass_outcome": None})
            # long ball accurate: location settata → d1_direct le conta come progressive_pass
            for _ in range(long_balls):
                rows.append({**base, "type": "Pass", "minute": 45, "pass_outcome": None,
                             "location": [50.0, 40.0], "pass_end_location": [75.0, 40.0]})

            # Key pass
            for _ in range(int(stats.get("keyPass") or 0)):
                rows.append({**base, "type": "Pass", "minute": 45,
                             "pass_shot_assist": True, "pass_outcome": None})

            # Dribbling vinti
            for _ in range(int(stats.get("wonContest") or 0)):
                rows.append({**base, "type": "Dribble", "minute": 45,
                             "dribble_outcome": "Complete"})

            # Tackle
            for _ in range(int(stats.get("totalTackle") or 0)):
                rows.append({**base, "type": "Duel", "minute": 45,
                             "duel_type": "Tackle", "duel_outcome": "Won"})

            # Intercetti
            for _ in range(int(stats.get("interceptionWon") or 0)):
                rows.append({**base, "type": "Interception", "minute": 45,
                             "interception_outcome": "Won"})

            # Clearance
            for _ in range(int(stats.get("totalClearance") or 0)):
                rows.append({**base, "type": "Clearance", "minute": 45})

            # Block
            for _ in range(int(stats.get("outfielderBlock") or 0)):
                rows.append({**base, "type": "Block", "minute": 45})

            # Duelli aerei
            for _ in range(int(stats.get("aerialWon") or 0)):
                rows.append({**base, "type": "Duel", "minute": 45,
                             "duel_type": "Aerial Lost", "duel_outcome": "Won"})
            for _ in range(int(stats.get("aerialLost") or 0)):
                rows.append({**base, "type": "Duel", "minute": 45,
                             "duel_type": "Aerial Lost", "duel_outcome": "Lost In Play"})

            # Pressioni proxy (totalPress non è di Sofascore, usiamo dribbledPast)
            for _ in range(int(stats.get("dribbledPast") or 0)):
                rows.append({**base, "type": "Pressure", "minute": 45})

            # Falli subiti / commessi
            for _ in range(int(stats.get("foulsCommited") or stats.get("foulsCommitted") or 0)):
                rows.append({**base, "type": "Foul Committed", "minute": 45})

            # Cartellini
            card_info = cards_by_player.get(pname, {})
            if card_info.get("amm"):
                rows.append({**base, "type": "Bad Behaviour", "minute": 45,
                             "foul_committed_card": "Yellow Card"})
            if card_info.get("esp"):
                rows.append({**base, "type": "Bad Behaviour", "minute": 45,
                             "foul_committed_card": "Red Card"})

            # Portiere: salvataggi
            for _ in range(int(stats.get("savedShotsFromInsideTheBox") or 0)
                           + int(stats.get("savedShotsFromOutsideTheBox") or 0)):
                rows.append({**base, "type": "Goal Keeper", "minute": 45,
                             "goalkeeper_outcome": "Touched Out"})

            # Azioni neutre per completare il profilo D5
            rows.append({**base, "type": "Ball Receipt*", "minute": 45})

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows).reset_index(drop=True)
    return df


def load_match_sofascore(event_id: str) -> tuple[pd.DataFrame, dict[int, str]]:
    """
    Carica la partita da Sofascore e ritorna (events_df, positions_dict)
    compatibili con il rating engine.
    """
    print(f"  Fetching lineups  (eventId={event_id})...")
    lineups   = _rapidapi_get(f"/matches/get-lineups?matchId={event_id}")
    print(f"  Fetching incidents (eventId={event_id})...")
    incidents = _rapidapi_get(f"/matches/get-incidents?matchId={event_id}")

    events = _build_events(lineups, incidents, event_id)

    positions = {}
    for _, row in events.drop_duplicates("player_id").iterrows():
        if not pd.isna(row["player_id"]):
            positions[int(row["player_id"])] = row["position"]

    print(f"  {len(events)} eventi sintetici, {len(positions)} giocatori.")
    return events, positions


def available_stats_report(event_id: str) -> None:
    """Stampa tutte le statistiche disponibili per ogni giocatore (debug)."""
    lineups = _rapidapi_get(f"/matches/get-lineups?matchId={event_id}")
    for side in ("home", "away"):
        team = lineups.get(side, {}).get("team", {}).get("name", side)
        print(f"\n{'='*50}\n{team}\n{'='*50}")
        for entry in (lineups.get(side, {}).get("players") or []):
            p     = entry.get("player", {})
            stats = entry.get("statistics") or {}
            if not stats:
                continue
            print(f"  {p.get('name','?')} ({entry.get('position','?')}):")
            for k, v in stats.items():
                if v not in (None, 0, 0.0, ""):
                    print(f"    {k}: {v}")
