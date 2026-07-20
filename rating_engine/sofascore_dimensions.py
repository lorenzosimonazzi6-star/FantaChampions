"""Calcolo D2 e D3 direttamente dai dati box-score Sofascore.

Sofascore fornisce:
  expectedGoals, expectedAssists → D2 reale senza simulazione eventi
  totalProgression, passValueNormalized, dribbleValueNormalized,
  defensiveValueNormalized, goalkeeperValueNormalized → D3 proxy ottimo
  goalsPrevented, keeperSaveValue → D2 portiere
"""

import pandas as pd
import numpy as np


def _stat(stats: dict, *keys, default=0.0) -> float:
    for k in keys:
        v = stats.get(k)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return default


def compute_d2(events: pd.DataFrame) -> pd.Series:
    """
    D2 = impatto sul match, sia offensivo che difensivo.

    Componente offensiva (crea occasioni):
      xG, xA, keyPass, bigChanceCreated → cattura chi crea pericoli reali

    Componente difensiva (rimuove pericoli):
      wonTackle, ballRecovery, interceptions → cattura chi recupera palloni
      e vince duelli — altrimenti i centrocampisti difensivi (Bouaddi-style)
      ricevono D2≈0 pur avendo avuto un impatto enorme sul match

    Portiere: goalsPrevented e keeperSaveValue.

    I due blocchi vengono normalizzati insieme nella formula (percentili
    intra-match), quindi la scala relativa è ciò che conta, non i valori assoluti.
    """
    scores: dict[int, float] = {}

    seen = set()
    for _, row in events.iterrows():
        pid = int(row["player_id"]) if not pd.isna(row.get("player_id", float("nan"))) else None
        if pid is None or pid in seen:
            continue
        seen.add(pid)

        stats = row.get("_sofa_stats") or {}

        # ── offensiva ────────────────────────────────────────────────────
        xg  = _stat(stats, "expectedGoals")
        xa  = _stat(stats, "expectedAssists")
        kp  = _stat(stats, "keyPass")
        bcc = _stat(stats, "bigChanceCreated")

        # ── difensiva ────────────────────────────────────────────────────
        # duelWon: tutti i duelli vinti (inclusi tackle + aerei + contrasti)
        # wonTackle: subset di duelWon, solo tackle riusciti
        # ballRecovery: recupero palla
        # interceptions: intercettazioni
        duel_won   = _stat(stats, "duelWon")
        tackle_won = _stat(stats, "wonTackle")
        recovery   = _stat(stats, "ballRecovery")
        intercept  = _stat(stats, "interceptionWon", "interceptions", "totalInterceptionWon")

        # ── portiere ─────────────────────────────────────────────────────
        gp  = _stat(stats, "goalsPrevented")
        ksv = _stat(stats, "keeperSaveValue")

        offensive  = xg * 2.5 + xa * 2.0 + kp * 0.3 + bcc * 0.5
        # duelWon cattura l'impatto difensivo complessivo (tackle + duelli aerei + contrasti)
        # wonTackle è già incluso in duelWon ma con peso ridotto per il contributo tecnico
        defensive  = duel_won * 0.20 + tackle_won * 0.20 + recovery * 0.15 + intercept * 0.25
        goalkeeper = max(0, gp) * 1.5 + max(0, ksv) * 1.0

        scores[pid] = offensive + defensive + goalkeeper

    return pd.Series(scores, name="d2_raw")


def compute_d3(events: pd.DataFrame) -> pd.Series:
    """
    D3 dai metric di valore normalizzato + progressione Sofascore.

    passValueNormalized, dribbleValueNormalized, defensiveValueNormalized
    sono componenti VAEP-style già calcolate da Sofascore: misurano quanto
    ogni azione ha aumentato la probabilità di segnare / ridotto quella di subire.

    totalProgression = metri di avanzamento verso porta tramite carry+pass.
    """
    scores: dict[int, float] = {}

    seen = set()
    for _, row in events.iterrows():
        pid = int(row["player_id"]) if not pd.isna(row.get("player_id", float("nan"))) else None
        if pid is None or pid in seen:
            continue
        seen.add(pid)

        stats = row.get("_sofa_stats") or {}

        # clip passValueNormalized a 0: un CM difensivo fa passaggi corti/sicuri
        # che Sofascore VAEP penalizza, ma non è un demerito per il suo ruolo
        pv  = max(0.0, _stat(stats, "passValueNormalized"))
        dv  = _stat(stats, "dribbleValueNormalized")
        dfv = _stat(stats, "defensiveValueNormalized")
        gkv = _stat(stats, "goalkeeperValueNormalized")
        sv  = _stat(stats, "shotValueNormalized")

        # progressione totale (metri verso porta), normalizzata su base 200m
        prog = _stat(stats, "totalProgression")
        prog_norm = np.tanh(prog / 150)  # scala morbida: 150m ≈ 0.76, 300m ≈ 0.96

        # touches: misura del coinvolgimento nel gioco
        touches = _stat(stats, "touches")
        touches_norm = np.tanh(touches / 80)

        # value composito: somma pesata delle componenti Sofascore
        # shotValue lo escludiamo perché già catturato da D2
        value_composite = (
            pv  * 0.35 +
            dv  * 0.15 +
            dfv * 0.25 +
            gkv * 0.25  # solo per GK, è 0 per gli altri
        )

        score = (
            value_composite * 0.50 +
            prog_norm       * 0.30 +
            touches_norm    * 0.20
        )
        scores[pid] = score

    return pd.Series(scores, name="d3_raw")


def sofa_rating_as_d3_override(events: pd.DataFrame) -> pd.Series:
    """
    Alternativa: usa direttamente il rating Sofascore come proxy D3.
    Scala da [1,10] a [0,1]. Da usare se le value metrics non sono disponibili.
    """
    scores: dict[int, float] = {}
    seen = set()
    for _, row in events.iterrows():
        pid = int(row["player_id"]) if not pd.isna(row.get("player_id", float("nan"))) else None
        if pid is None or pid in seen:
            continue
        seen.add(pid)
        r = row.get("_sofa_rating")
        scores[pid] = (float(r) - 1) / 9 if r else 0.5
    return pd.Series(scores, name="d3_raw")
