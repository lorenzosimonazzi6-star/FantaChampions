"""Formula finale: compone le 5 dimensioni in un voto 0–10.

Logica base:
  - Ogni giocatore parte da 6.0 (media neutra)
  - Le dimensioni spostano il voto su/giù indipendentemente dai minuti giocati
    (chi fa tanto in 15' viene premiato quanto chi fa tanto in 90')
  - Formula: rating = clip(6 + (composite - 0.5) * SPREAD * Phi + malus, 0, 10)
    dove composite ∈ [0,1]:  0.5→6.0 | 1.0→10.0 | 0.0→2.0
  - Soglia minima: almeno 10 minuti giocati per attivare il rating
  - Floor GK = 6.0 se porta inviolata (60'+ senza gol subiti), salvo errori gravi
"""

import pandas as pd
import numpy as np
from d1_direct import POSITION_GROUP_MAP

WEIGHTS   = {"d1": 0.20, "d2": 0.25, "d3": 0.20, "d4": 0.20, "d5": 0.15}
# Sofascore non distingue CB da terzini (manda "D" generico per tutti).
# Rimuoviamo il boost CB=1.05 per evitare di penalizzare/premiare in modo errato.
PHI       = {"GK": 1.05, "CB": 1.00, "FB": 1.00, "CM": 1.00, "AM": 1.00, "FW": 0.95}
BASE        = 6.0   # voto di partenza per ogni giocatore
SPREAD      = 8.0   # ampiezza delta: composite 0→-4 / 0.5→0 / 1→+4 (rating 2–10)
MIN_MINUTES = 10    # minuti minimi per avere un rating

# Malus fissi applicati al rating finale (non al composite)
MALUS_GK_ERROR_GOAL = -1.5  # errorLeadToAGoal per il portiere


def _percentile_normalize_01(series: pd.Series, lo: float = 5, hi: float = 95) -> pd.Series:
    """Normalizza a [0, 1] usando i percentili estremi come ancora."""
    p_lo = series.quantile(lo / 100)
    p_hi = series.quantile(hi / 100)
    if p_hi == p_lo:
        return pd.Series(0.5, index=series.index)
    return (series.clip(p_lo, p_hi) - p_lo) / (p_hi - p_lo)


def _minutes_played(events: pd.DataFrame, player_id: int) -> float:
    """Minuti giocati: usa colonna minutesPlayed se disponibile (Sofascore),
    altrimenti stima dal massimo minuto negli eventi."""
    p = events[events["player_id"] == player_id]
    if p.empty:
        return 0.0
    # Sofascore loader inietta _sofa_stats con minutesPlayed
    for _, row in p.iterrows():
        stats = row.get("_sofa_stats") or {}
        mins = stats.get("minutesPlayed")
        if mins is not None:
            return float(mins)
    # fallback: massimo minuto negli eventi StatsBomb
    if "minute" in p.columns:
        return float(p["minute"].max())
    return 90.0


def _gk_sofa_stats(events: pd.DataFrame, player_id: int) -> dict:
    """Legge _sofa_stats dalla prima riga del portiere."""
    p = events[events["player_id"] == player_id]
    if p.empty:
        return {}
    return p.iloc[0].get("_sofa_stats") or {}


def _compute_gk_composite(gk_stats: dict) -> float | None:
    """
    Composite [0,1] specifico per GK. Bypassa la normalizzazione intra-match
    (i GK non possono competere con gli attaccanti su xG/gol nei percentili).

    Driver:
      1. goalsPrevented (gp)  — peso principale: gol evitati vs xG attesi
      2. saves                — volume di lavoro
      3. passValueNormalized + goalkeeperValueNormalized — distribuzione e footwork

    Scala orientativa del rating finale (con phi=1.05, spread=8):
      composite 0.80 → ~8.4  (grande prestazione)
      composite 0.60 → ~6.7  (sopra la media)
      composite 0.50 → ~6.0  (neutro)
      composite 0.40 → ~5.2  (sotto la media)
      composite 0.30 → ~4.5  (prestazione negativa)

    Ritorna None se saves==0 (GK inoperoso) → il chiamante applica floor 0.5.
    """
    saves    = float(gk_stats.get("saves", 0) or 0)
    gp       = float(gk_stats.get("goalsPrevented", 0) or 0)
    pass_val = float(gk_stats.get("passValueNormalized", 0) or 0)
    gkv      = float(gk_stats.get("goalkeeperValueNormalized", 0) or 0)

    if saves == 0:
        return None  # inoperoso: il chiamante usa floor 0.5

    # 1. goalsPrevented → componente principale ±0.30
    #    tanh comprime gli estremi: gp=+2→+0.30 | gp=0→0 | gp=-1→-0.20 | gp=-2→-0.30
    gp_component = float(np.tanh(gp * 0.55) * 0.30)

    # 2. saves → quantità di lavoro, contributo positivo fino a +0.12
    #    tanh(saves/6): 3 saves→+0.046 | 6 saves→+0.076 | 10 saves→+0.10
    saves_component = float(np.tanh(saves / 6.0) * 0.12)

    # 3. distribuzione (passaggi + footwork) → piccola influenza ±0.05
    dist_component = float(np.tanh((pass_val + gkv * 0.5) * 1.5) * 0.05)

    composite = 0.5 + gp_component + saves_component + dist_component
    return float(np.clip(composite, 0.0, 1.0))


def _gk_goals_conceded(events: pd.DataFrame, player_id: int) -> int:
    """Gol subiti dalla squadra del portiere.
    Legge _sofa_stats._goals_against (iniettato da sofascore_loader).
    Fallback: conta eventi Shot/Goal dell'altra squadra nel DataFrame.
    """
    stats = _gk_sofa_stats(events, player_id)
    ga = stats.get("_goals_against")
    if ga is not None:
        return int(ga)
    # fallback per StatsBomb (nessun _sofa_stats)
    p = events[events["player_id"] == player_id]
    if p.empty:
        return 0
    my_team_id = p.iloc[0].get("team_id")
    if "type" not in events.columns or "shot_outcome" not in events.columns:
        return 0
    goals_against = events[
        (events["type"] == "Shot") &
        (events["shot_outcome"] == "Goal") &
        (events["team_id"] != my_team_id)
    ]
    return len(goals_against)


def _rating_malus(events: pd.DataFrame, player_id: int, role_group: str, minutes: float) -> float:
    """
    Malus/bonus applicati al rating finale (non mediati dal composite).
    Legge _sofa_stats dalla prima riga del giocatore (dati identici su tutte le righe).
    """
    malus = 0.0
    p = events[events["player_id"] == player_id]
    if p.empty:
        return malus

    stats = p.iloc[0].get("_sofa_stats") or {}

    # GK: errore che porta direttamente a un gol subito
    if role_group == "GK":
        errors = int(stats.get("errorLeadToAGoal", 0) or 0)
        malus += errors * MALUS_GK_ERROR_GOAL

    # Qualsiasi giocatore outfield: errore diretto che porta a un gol
    if role_group != "GK":
        errors = int(stats.get("errorLeadToAGoal", 0) or 0)
        if errors > 0:
            malus += errors * -1.0

    # Cartellino rosso: malus proporzionale ai minuti rimanenti dopo l'espulsione.
    # Un rosso al 30' (60 min in 10) vale molto di più di uno all'85' (5 min in 10).
    # Formula: -(minuti_rimanenti / 90) * 2.5
    if "foul_committed_card" in p.columns and (p["foul_committed_card"] == "Red Card").any():
        minutes_remaining = max(0.0, 90.0 - minutes)
        malus += -(minutes_remaining / 90.0) * 2.5

    return malus


def compute(
    events: pd.DataFrame,
    positions: dict[int, str],
    d1: pd.Series,
    d2: pd.Series,
    d3: pd.Series,
    d4: pd.Series,
    d5: pd.Series,
) -> pd.DataFrame:
    all_pids = list(set(d1.index) | set(d2.index) | set(d3.index) | set(d4.index) | set(d5.index))

    # normalizza D1, D2, D4 a [0,1] con percentili intra-match
    # D3 e D5 sono già [0,1] dai rispettivi moduli
    d1n = _percentile_normalize_01(d1.reindex(all_pids, fill_value=0))
    d2n = _percentile_normalize_01(d2.reindex(all_pids, fill_value=0))
    d3n = (d3.reindex(all_pids, fill_value=0) * 2.3).clip(0, 0.85)
    d4n = _percentile_normalize_01(d4.reindex(all_pids, fill_value=0))
    d5n = d5.reindex(all_pids, fill_value=0).clip(0, 1)

    ev = events.copy()
    ev["player_id"] = pd.to_numeric(ev.get("player_id", pd.Series(dtype=float)), errors="coerce")

    pid_name = {}
    if "player" in ev.columns:
        pid_name = (
            ev.dropna(subset=["player_id", "player"])
            .drop_duplicates("player_id")
            .set_index("player_id")["player"]
            .to_dict()
        )

    rows = []
    for pid in all_pids:
        pid     = int(pid)
        minutes = _minutes_played(ev, pid)

        # soglia minima: non assegniamo rating a chi non è entrato
        if minutes < MIN_MINUTES:
            continue

        pos = positions.get(pid, "Unknown")
        grp = POSITION_GROUP_MAP.get(pos, "CM")
        phi = PHI.get(grp, 1.0)

        # VAEP factor: comprime o amplifica D1 (solo CB/FB), D3 e D4 in base
        # al defensiveValueNormalized Sofascore.
        # dfv < 0 → il giocatore ha peggiorato la difesa della squadra → penalità su D1/D3/D4
        # dfv > 0 → difensore di qualità VAEP → bonus
        # Floor 0.35: evita collasso totale per difensori con dfv molto negativo
        p_rows = ev[ev["player_id"] == pid]
        sofa = (p_rows.iloc[0].get("_sofa_stats") or {}) if not p_rows.empty else {}
        dfv = float(sofa.get("defensiveValueNormalized", 0) or 0)
        vaep_factor = max(0.35, 1.0 + dfv * 2.0)

        d2_v   = float(d2n.get(pid, 0.5))
        d3_raw = float(d3n.get(pid, 0.5))
        d5_v   = float(d5n.get(pid, 0.5))

        # D1 e D4: per i sub (<45 min) usa il tasso per-minuto anziché la normalizzazione
        # percentile. Un sub che segna in 10 min ha una densità di contributo altissima
        # (9× un titolare) che la normalizzazione percentile non cattura.
        # Scala: tanh(score × (90/min) / 15) — goal in 10 min → D1≈1.0;
        #        nessuna azione → D1≈0 → la regressione porta il composite verso 6.0.
        # Cap del moltiplicatore a 6× (corrisponde a 15 min di gioco).
        if minutes < 45:
            _rate = min(90.0 / max(minutes, 5.0), 6.0)
            d1_raw = float(np.tanh(float(d1.get(pid, 0)) * _rate / 15.0))
            d4_raw = float(np.tanh(float(d4.get(pid, 0)) * _rate / 15.0))
        else:
            d1_raw = float(d1n.get(pid, 0.5))
            d4_raw = float(d4n.get(pid, 0.5))

        # vaep_factor per CB/FB: comprime (dfv<0) o amplifica (dfv>0) D1+D3+D4.
        # Per CM/AM/FW: solo boost (vaep_factor>1) su D3+D4; dfv negativo è fisiologico
        # (non difendono per ruolo) e non va penalizzato.
        if grp in ("CB", "FB"):
            d1_v = float(np.clip(d1_raw * vaep_factor, 0.0, 1.0))
            d3_v = float(np.clip(d3_raw * vaep_factor, 0.0, 0.85))
            d4_v = float(np.clip(d4_raw * vaep_factor, 0.0, 1.0))
        elif vaep_factor > 1.0:
            d1_v = d1_raw
            d3_v = float(np.clip(d3_raw * vaep_factor, 0.0, 0.85))
            d4_v = float(np.clip(d4_raw * vaep_factor, 0.0, 1.0))
        else:
            d1_v, d3_v, d4_v = d1_raw, d3_raw, d4_raw

        # composite ∈ [0,1]: media pesata delle 5 dimensioni
        composite = (
            WEIGHTS["d1"] * d1_v +
            WEIGHTS["d2"] * d2_v +
            WEIGHTS["d3"] * d3_v +
            WEIGHTS["d4"] * d4_v +
            WEIGHTS["d5"] * d5_v
        )

        # GK: bypass normalizzazione intra-match con composite dedicato.
        # Il composite GK è costruito da gp + saves + distribuzione, senza
        # competere con gli attaccanti nei percentili di match.
        if grp == "GK" and minutes >= 60:
            gk_stats  = _gk_sofa_stats(ev, pid)
            gk_comp   = _compute_gk_composite(gk_stats)
            if gk_comp is None:
                composite = 0.50   # inoperoso (saves==0) → neutro
            else:
                composite = gk_comp

        # Soft cap: sopra 0.76 la curva si comprime del 40%.
        # Questo evita rating >9 pur mantenendo differenziazione tra buone e ottime prestazioni.
        # Soglia 0.76 lascia invariati i giocatori "molto buoni" (Bouaddi ~0.73).
        if composite > 0.76:
            composite = 0.76 + (composite - 0.76) * 0.40

        # Regressione asimmetrica: chi ha composite < 0.5 (performance sotto la media)
        # viene attratto verso 0.5 inversamente proporzionale ai minuti giocati.
        # Chi ha composite >= 0.5 non viene toccato: la buona performance vale piena
        # indipendentemente dai minuti (un sub che fa 1 gol in 15' merita il voto alto).
        # Effetto: sostituti senza impatto → vicino a 6; chi ha fatto qualcosa → pieno merito.
        if composite < 0.5:
            confidence = min(minutes / 90.0, 1.0)
            composite = 0.5 - (0.5 - composite) * confidence

        # delta attorno al base 6: Phi scala il delta, malus applicate dopo
        delta  = (composite - 0.5) * SPREAD * phi
        malus  = _rating_malus(ev, pid, grp, minutes)
        rating = round(float(np.clip(BASE + delta + malus, 0.0, 10.0)), 2)

        rows.append({
            "player_id":   pid,
            "player_name": pid_name.get(float(pid), f"Player {pid}"),
            "position":    pos,
            "role_group":  grp,
            "minutes":     int(minutes),
            "d1_norm":    round(d1_v, 3),
            "d2_norm":    round(d2_v, 3),
            "d3_norm":    round(d3_v, 3),
            "d4_norm":    round(d4_v, 3),
            "d5_norm":    round(d5_v, 3),
            "vaep_factor": round(vaep_factor, 3),
            "composite":   round(composite, 3),
            "phi":         phi,
            "malus":       round(malus, 2),
            "rating":      rating,
        })

    return pd.DataFrame(rows).sort_values("rating", ascending=False).reset_index(drop=True)
