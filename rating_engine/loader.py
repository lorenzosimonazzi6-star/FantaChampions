"""Caricamento e preprocessing dati StatsBomb."""

from functools import lru_cache
import pandas as pd
from statsbombpy import sb


WC_2018 = {"competition_id": 43, "season_id": 3}
WC_2022 = {"competition_id": 43, "season_id": 106}


@lru_cache(maxsize=64)
def load_events(match_id: int) -> pd.DataFrame:
    df = sb.events(match_id=match_id, flatten_attrs=True)
    if "location" in df.columns:
        df["loc_x"] = df["location"].apply(lambda v: v[0] if isinstance(v, list) else None)
        df["loc_y"] = df["location"].apply(lambda v: v[1] if isinstance(v, list) else None)
    return df


@lru_cache(maxsize=64)
def load_lineups(match_id: int) -> dict[str, pd.DataFrame]:
    return sb.lineups(match_id=match_id)


def player_positions(match_id: int) -> dict[int, str]:
    """Ritorna {player_id: position} ricavato direttamente dagli eventi."""
    ev = load_events(match_id)
    result = {}
    for _, row in ev.dropna(subset=["player_id", "position"]).drop_duplicates("player_id").iterrows():
        result[int(row["player_id"])] = row["position"]
    return result


def player_teams(match_id: int) -> dict[int, str]:
    """Ritorna {player_id: team}."""
    ev = load_events(match_id)
    result = {}
    for _, row in ev.dropna(subset=["player_id", "team"]).drop_duplicates("player_id").iterrows():
        result[int(row["player_id"])] = row["team"]
    return result


def list_matches(competition_id: int, season_id: int) -> pd.DataFrame:
    return sb.matches(competition_id=competition_id, season_id=season_id)


def list_competitions() -> pd.DataFrame:
    return sb.competitions()
