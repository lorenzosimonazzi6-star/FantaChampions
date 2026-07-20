"""Entry point: calcola il rating per tutti i giocatori di una partita.

Uso:
    python main.py --match_id 7549
    python main.py --competition_id 43 --season_id 3 --list_matches
    python main.py --match_id 7549 --output ratings.csv
"""

import argparse
import sys
import os

# aggiunge il path per import locali
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from loader import load_events, player_positions, list_matches, list_competitions
import d1_direct
import d2_ximpact
import d3_network
import d4_context
import d5_role
import formula


def rate_match(match_id: int) -> pd.DataFrame:
    """Pipeline completa: carica eventi → calcola 5 dimensioni → voto finale."""
    print(f"[1/6] Caricamento eventi partita {match_id}...")
    events = load_events(match_id)
    print(f"      {len(events)} eventi caricati.")

    print("[2/6] Caricamento posizioni giocatori...")
    positions = player_positions(match_id)
    print(f"      {len(positions)} giocatori identificati.")

    print("[3/6] D1 — Azioni Dirette...")
    d1 = d1_direct.compute(events, positions)

    print("[4/6] D2 — xImpact...")
    d2 = d2_ximpact.compute(events, positions)

    print("[5/6] D3 — Network Influence...")
    d3 = d3_network.compute(events, positions)

    print("[6a/6] D4 — Contesto Partita...")
    d4 = d4_context.compute(events, positions)

    print("[6b/6] D5 — Role Fulfillment...")
    d5 = d5_role.compute(events, positions)

    print("[7/7] Formula finale...")
    result = formula.compute(events, positions, d1, d2, d3, d4, d5)
    return result


def rate_match_sofascore(event_id: str) -> pd.DataFrame:
    """Pipeline per partite WC 2026 via Sofascore RapidAPI.

    D2 e D3 usano direttamente i valori reali Sofascore
    (xG, xA, progressione, value metrics) invece di simulare eventi.
    """
    from sofascore_loader import load_match_sofascore
    from sofascore_dimensions import compute_d2 as sofa_d2, compute_d3 as sofa_d3

    print(f"[1/6] Caricamento dati Sofascore (eventId={event_id})...")
    events, positions = load_match_sofascore(event_id)
    print(f"[2/6] {len(positions)} giocatori identificati.")

    print("[3/6] D1 — Azioni Dirette (da stats box-score)...")
    d1 = d1_direct.compute(events, positions)

    print("[4/6] D2 — xImpact (xG + xA reali Sofascore)...")
    d2 = sofa_d2(events)

    print("[5/6] D3 — Network (value metrics + progressione Sofascore)...")
    d3 = sofa_d3(events)

    print("[6a/6] D4 — Contesto Partita (incidents timing)...")
    d4 = d4_context.compute(events, positions)

    print("[6b/6] D5 — Role Fulfillment...")
    d5 = d5_role.compute(events, positions)

    print("[7/7] Formula finale...")
    return formula.compute(events, positions, d1, d2, d3, d4, d5)


def main():
    parser = argparse.ArgumentParser(description="Football Player Rating Engine")
    parser.add_argument("--match_id", type=int, help="ID partita StatsBomb (WC 2018/2022)")
    parser.add_argument("--event_id", type=str, help="ID partita Sofascore (WC 2026 via RapidAPI)")
    parser.add_argument("--debug_stats", action="store_true", help="Stampa tutte le stat Sofascore disponibili")
    parser.add_argument("--competition_id", type=int, default=43, help="ID competizione (default 43 = WC)")
    parser.add_argument("--season_id", type=int, default=3, help="ID stagione (default 3 = WC 2018)")
    parser.add_argument("--list_matches", action="store_true", help="Elenca partite disponibili")
    parser.add_argument("--list_competitions", action="store_true", help="Elenca competizioni disponibili")
    parser.add_argument("--output", type=str, help="Salva risultati in CSV")
    args = parser.parse_args()

    if args.list_competitions:
        comps = list_competitions()
        print(comps[["competition_id", "competition_name", "season_id", "season_name"]].to_string(index=False))
        return

    if args.list_matches:
        matches = list_matches(args.competition_id, args.season_id)
        cols = [c for c in ["match_id", "match_date", "home_team", "away_team", "home_score", "away_score"] if c in matches.columns]
        print(matches[cols].to_string(index=False))
        return

    if args.debug_stats and args.event_id:
        from sofascore_loader import available_stats_report
        available_stats_report(args.event_id)
        return

    if args.event_id:
        result = rate_match_sofascore(args.event_id)
    elif args.match_id:
        result = rate_match(args.match_id)
    else:
        parser.print_help()
        print("\nEsempi:")
        print("  StatsBomb WC 2018:  python main.py --match_id 7549")
        print("  Sofascore WC 2026:  python main.py --event_id 15186798")
        print("  Debug stat Sofa:    python main.py --event_id 15186798 --debug_stats")
        return

    # stampa tabella formattata
    display_cols = ["player_name", "position", "role_group", "d1_norm", "d2_norm",
                    "d3_norm", "d4_norm", "d5_norm", "rating"]
    print("\n" + "="*80)
    print(f"RATING GIOCATORI — Match ID {args.match_id}")
    print("="*80)
    print(result[display_cols].to_string(index=False))
    print("="*80)

    if args.output:
        result.to_csv(args.output, index=False)
        print(f"\nSalvato in {args.output}")


if __name__ == "__main__":
    main()
