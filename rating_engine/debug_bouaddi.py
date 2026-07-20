import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from sofascore_loader import load_match_sofascore
from sofascore_dimensions import compute_d2, compute_d3
from d1_direct import compute as compute_d1
from d4_context import compute as compute_d4
from d5_role import compute as compute_d5
import pandas as pd
import numpy as np

events, positions = load_match_sofascore("15186850")

bouaddi_row = None
for _, row in events.drop_duplicates("player_id").iterrows():
    if "bouaddi" in str(row.get("player", "")).lower():
        bouaddi_row = row
        break

if bouaddi_row is None:
    print("Bouaddi non trovato")
    sys.exit(1)

pid = int(bouaddi_row["player_id"])
stats = bouaddi_row.get("_sofa_stats") or {}
print(f"=== BOUADDI (pid={pid}) ===")
print(f"Posizione: {bouaddi_row['position']}")
print(f"Minuti: {stats.get('minutesPlayed')}")
print()
print("--- STATS SOFASCORE ---")
for k, v in sorted(stats.items()):
    if v not in (None, 0, 0.0, "", False):
        print(f"  {k}: {v}")

d1 = compute_d1(events, positions)
d2 = compute_d2(events)
d3 = compute_d3(events)
d4 = compute_d4(events, positions)
d5 = compute_d5(events, positions)

print()
print("--- SCORES GREZZI ---")
print(f"  D1 raw: {d1.get(pid, 0):.4f}")
print(f"  D2 raw: {d2.get(pid, 0):.4f}")
print(f"  D3 raw: {d3.get(pid, 0):.4f}")
print(f"  D4 raw: {d4.get(pid, 0):.4f}")
print(f"  D5 raw: {d5.get(pid, 0):.4f}")

all_pids = list(set(d1.index) | set(d2.index) | set(d3.index) | set(d4.index) | set(d5.index))

def pnorm(s, lo=5, hi=95):
    s2 = s.reindex(all_pids, fill_value=0)
    plo = s2.quantile(lo / 100)
    phi_val = s2.quantile(hi / 100)
    if phi_val == plo:
        return pd.Series(0.5, index=s2.index)
    return (s2.clip(plo, phi_val) - plo) / (phi_val - plo)

d1n = pnorm(d1)
d2n = pnorm(d2)
d3n = pnorm(d3)
d4n = pnorm(d4)
d5n = d5.reindex(all_pids, fill_value=0).clip(0, 1)

print()
print("--- DIMENSIONI NORMALIZZATE ---")
print(f"  D1 norm: {d1n.get(pid, 0.5):.3f}  (w=20%)")
print(f"  D2 norm: {d2n.get(pid, 0.5):.3f}  (w=25%)")
print(f"  D3 norm: {d3n.get(pid, 0.5):.3f}  (w=20%)")
print(f"  D4 norm: {d4n.get(pid, 0.5):.3f}  (w=20%)")
print(f"  D5 norm: {d5n.get(pid, 0.5):.3f}  (w=15%)")

composite = (
    0.20 * d1n.get(pid, 0.5) +
    0.25 * d2n.get(pid, 0.5) +
    0.20 * d3n.get(pid, 0.5) +
    0.20 * d4n.get(pid, 0.5) +
    0.15 * d5n.get(pid, 0.5)
)
print(f"  Composite: {composite:.3f}")
print(f"  Rating: {6 + (composite - 0.5) * 8 * 1.0:.2f}")

print()
print("--- TOP 5 D2 RAW nel match ---")
pid_names = {int(float(k)): v for k, v in
             events.drop_duplicates("player_id").set_index("player_id")["player"].to_dict().items()}
for pid2, val in d2.nlargest(5).items():
    print(f"  {pid_names.get(int(pid2), pid2)}: {val:.4f}  (norm: {d2n.get(pid2, 0.5):.3f})")

print()
print("--- TOP 5 D3 RAW nel match ---")
for pid2, val in d3.nlargest(5).items():
    print(f"  {pid_names.get(int(pid2), pid2)}: {val:.4f}  (norm: {d3n.get(int(pid2), 0.5):.3f})")

print()
print("--- DISTRIBUZIONE D2 nel match (min, p25, p50, p75, max) ---")
d2_all = d2.reindex(all_pids, fill_value=0)
print(f"  min={d2_all.min():.3f}, p25={d2_all.quantile(0.25):.3f}, p50={d2_all.quantile(0.5):.3f}, p75={d2_all.quantile(0.75):.3f}, max={d2_all.max():.3f}")
