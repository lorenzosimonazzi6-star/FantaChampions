"""Mostra distribuzione rating + top players per verificare il modello."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from export_excel import build_comparison
import pandas as pd

MATCHES = [
    ("15186854", "Argentina", "Algeria"),
    ("15186850", "Brasile",   "Marocco"),
]

for eid, home, away in MATCHES:
    print(f"\n{'='*60}")
    print(f"  {home} vs {away}")
    print(f"{'='*60}")
    df = build_comparison(eid)
    top = df[["player_name","role_group","minuti","d1_norm","d2_norm","d3_norm","d4_norm","d5_norm","rating","sofa_rating"]].head(12)
    pd.set_option("display.max_columns", 20)
    pd.set_option("display.width", 160)
    pd.set_option("display.float_format", "{:.3f}".format)
    print(top.to_string(index=False))
    print(f"\n  Rating stats: min={df['rating'].min():.2f}, median={df['rating'].median():.2f}, max={df['rating'].max():.2f}")
    # quanti D2_norm == 1.0?
    for d in ["d1_norm","d2_norm","d3_norm","d4_norm","d5_norm"]:
        n_ones = (df[d] >= 0.999).sum()
        if n_ones > 0:
            print(f"  {d}=1.0: {n_ones} giocatori")
