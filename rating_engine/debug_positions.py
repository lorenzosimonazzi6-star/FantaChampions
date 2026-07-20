"""Verifica che codici posizione manda Sofascore per ogni giocatore."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from sofascore_loader import _rapidapi_get

lineups = _rapidapi_get("/matches/get-lineups?matchId=15186850")  # Brasile-Marocco
for side in ("home", "away"):
    team = (lineups.get(side, {}).get("team") or {}).get("name", side)
    print(f"\n=== {team} ===")
    for entry in (lineups.get(side, {}).get("players") or []):
        p = entry.get("player") or {}
        ep = entry.get("position", "?")
        pp = p.get("position", {})
        pp_name = pp.get("name", "?") if isinstance(pp, dict) else pp
        print(f"  {p.get('name','?'):30s}  entry.position={ep!r:6}  player.position={pp_name!r}")
