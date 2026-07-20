"""D3 — Network Influence (peso 20%)."""

import pandas as pd
import numpy as np
import networkx as nx


def _build_pass_graph(events: pd.DataFrame, team_id) -> nx.DiGraph:
    G = nx.DiGraph()
    if "type" not in events.columns:
        return G
    passes = events[(events["type"] == "Pass") & (events.get("team_id", pd.Series()) == team_id)]
    pass_out = passes.get("pass_outcome", pd.Series())
    completed = passes[pass_out.isna() | (pass_out == "")]

    for _, row in completed.iterrows():
        passer = row.get("player_id")
        recipient = row.get("pass_recipient_id")
        if pd.isna(passer) or pd.isna(recipient) if recipient is not None else True:
            continue
        passer, recipient = int(passer), int(recipient)
        if G.has_edge(passer, recipient):
            G[passer][recipient]["weight"] += 1
        else:
            G.add_edge(passer, recipient, weight=1)
    return G


def compute(events: pd.DataFrame, positions: dict[int, str]) -> pd.Series:
    if "type" not in events.columns or "team_id" not in events.columns:
        return pd.Series(dtype=float, name="d3_raw")

    ev = events.copy()
    ev["player_id"] = pd.to_numeric(ev.get("player_id", pd.Series(dtype=float)), errors="coerce")
    scores: dict[int, float] = {}

    for team_id in ev["team_id"].dropna().unique():
        G = _build_pass_graph(ev, team_id)
        if len(G.nodes) < 2:
            continue

        try:
            pr = nx.pagerank(G, weight="weight", alpha=0.85)
        except Exception:
            pr = {n: 1 / len(G.nodes) for n in G.nodes}

        try:
            bw = nx.betweenness_centrality(G, weight="weight", normalized=True)
        except Exception:
            bw = {n: 0.0 for n in G.nodes}

        pr_arr = np.array(list(pr.values()))
        bw_arr = np.array(list(bw.values()))
        pr_rng = float(pr_arr.max() - pr_arr.min()) or 1.0
        bw_rng = float(bw_arr.max() - bw_arr.min()) or 1.0

        for node in G.nodes:
            pid = int(node)
            pr_norm = (pr.get(node, 0) - pr_arr.min()) / pr_rng
            bw_norm = (bw.get(node, 0) - bw_arr.min()) / bw_rng

            # combo pass: sequenze >= 3 passaggi in cui il giocatore è coinvolto
            combo_count = 0
            if "possession" in ev.columns:
                team_passes = ev[(ev["type"] == "Pass") & (ev["team_id"] == team_id)]
                for _, poss_grp in team_passes.groupby("possession"):
                    if pid in poss_grp["player_id"].values and len(poss_grp) >= 3:
                        combo_count += 1

            combo_norm = min(combo_count / 10.0, 1.0)
            scores[pid] = 0.5 * pr_norm + 0.3 * bw_norm + 0.2 * combo_norm

    return pd.Series(scores, name="d3_raw")
