// ============================================================
// ARENA UCL — matches.js
// Configurazione partite con eventId Sofascore e kickoff UTC
//
// STRUTTURA GIORNATE:
//  G1–G8  : League Phase (18 partite/giornata × 8 = 144 totali)
//  G9–G10 : Playoff Andata + Ritorno (8+8)
//  G11–G12: Ottavi Andata + Ritorno (8+8)
//  G13–G14: Quarti Andata + Ritorno (4+4)
//  G15–G16: Semifinali Andata + Ritorno (2+2)
//  G17    : Finale (1)
//
// NOTE:
//  - Gli eventId SofaScore saranno disponibili con il calendario ufficiale (agosto 2026)
//  - I kickoff sono approssimativi — da aggiornare con il sorteggio
//  - Le giornate G9–G17 vengono popolate man mano che le squadre si qualificano
// ============================================================

const MATCHES = {
  // ── LEAGUE PHASE ─────────────────────────────────────────────
  // 18 partite per giornata · kickoff: settembre 2026 – febbraio 2027
  // eventId da inserire quando il calendario UCL 2026/27 sarà pubblicato (agosto 2026)
  "1": [
    // G1 · ~16-17 settembre 2026
  ],
  "2": [
    // G2 · ~1-2 ottobre 2026
  ],
  "3": [
    // G3 · ~22-23 ottobre 2026
  ],
  "4": [
    // G4 · ~5-6 novembre 2026
  ],
  "5": [
    // G5 · ~26-27 novembre 2026
  ],
  "6": [
    // G6 · ~10-11 dicembre 2026
  ],
  "7": [
    // G7 · ~21-22 gennaio 2027
  ],
  "8": [
    // G8 · ~11-12 febbraio 2027
  ],

  // ── PLAYOFF ──────────────────────────────────────────────────
  // Classificate 9°-24° del League Phase
  "9": [
    // Playoff Andata · ~18-19 febbraio 2027
  ],
  "10": [
    // Playoff Ritorno · ~25-26 febbraio 2027
  ],

  // ── OTTAVI DI FINALE ─────────────────────────────────────────
  // Top 8 + 8 vincitori playoff
  "11": [
    // Ottavi Andata · ~4-5 marzo 2027
  ],
  "12": [
    // Ottavi Ritorno · ~11-12 marzo 2027
  ],

  // ── QUARTI DI FINALE ─────────────────────────────────────────
  "13": [
    // Quarti Andata · ~8-9 aprile 2027
  ],
  "14": [
    // Quarti Ritorno · ~15-16 aprile 2027
  ],

  // ── SEMIFINALI ───────────────────────────────────────────────
  "15": [
    // Semifinali Andata · ~29-30 aprile 2027
  ],
  "16": [
    // Semifinali Ritorno · ~6-7 maggio 2027
  ],

  // ── FINALE ───────────────────────────────────────────────────
  "17": [
    // Finale · ~29 maggio 2027 — sede da definire
  ],
};

// Non modificare — usato da app.js per il polling live
const POLLING_INTERVAL_MS = 5 * 60 * 1000; // 5 minuti
