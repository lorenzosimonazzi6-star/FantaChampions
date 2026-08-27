// ============================================================
// ARENA UCL — matches.js
// Configurazione partite con eventId Sofascore e kickoff UTC
//
// STRUTTURA GIORNATE:
//  G1–G8  : League Phase (18 partite/giornata)
//  G9–G10 : Playoff Andata + Ritorno
//  G11–G12: Ottavi Andata + Ritorno
//  G13–G14: Quarti Andata + Ritorno
//  G15–G16: Semifinali Andata + Ritorno
//  G17    : Finale
//
// NOTE:
//  - SEGNAPOSTO 2026-08-23: una voce per giornata con SOLO la data della prima
//    partita (kickoff), così il grafico "andamento classifica" segna le giornate
//    come disputate man mano. home/away/eventId da riempire con il calendario
//    ufficiale (in arrivo). Orari indicativi: League Phase 18:45 CEST,
//    eliminazione diretta 21:00 CEST.
// ============================================================

const MATCHES = {
  // ── LEAGUE PHASE ─────────────────────────────────────────────
  "1": [ { eventId: "", home: "", away: "", kickoff: "2026-09-08T16:45:00Z" } ], // G1 · 8-9-10 set 2026
  "2": [ { eventId: "", home: "", away: "", kickoff: "2026-10-13T16:45:00Z" } ], // G2 · 13-14 ott 2026
  "3": [ { eventId: "", home: "", away: "", kickoff: "2026-10-20T16:45:00Z" } ], // G3 · 20-21 ott 2026
  "4": [ { eventId: "", home: "", away: "", kickoff: "2026-11-03T16:45:00Z" } ], // G4 · 3-4 nov 2026
  "5": [ { eventId: "", home: "", away: "", kickoff: "2026-11-24T16:45:00Z" } ], // G5 · 24-25 nov 2026
  "6": [ { eventId: "", home: "", away: "", kickoff: "2026-12-08T16:45:00Z" } ], // G6 · 8-9 dic 2026
  "7": [ { eventId: "", home: "", away: "", kickoff: "2027-01-19T16:45:00Z" } ], // G7 · 19-20 gen 2027
  "8": [ { eventId: "", home: "", away: "", kickoff: "2027-01-27T16:45:00Z" } ], // G8 · 27 gen 2027

  // ── PLAYOFF ──────────────────────────────────────────────────
  "9":  [ { eventId: "", home: "", away: "", kickoff: "2027-02-16T19:00:00Z" } ], // Playoff Andata · 16-17 feb 2027
  "10": [ { eventId: "", home: "", away: "", kickoff: "2027-02-23T19:00:00Z" } ], // Playoff Ritorno · 23-24 feb 2027

  // ── OTTAVI DI FINALE ─────────────────────────────────────────
  "11": [ { eventId: "", home: "", away: "", kickoff: "2027-03-09T19:00:00Z" } ], // Ottavi Andata · 9-10 mar 2027
  "12": [ { eventId: "", home: "", away: "", kickoff: "2027-03-16T19:00:00Z" } ], // Ottavi Ritorno · 16-17 mar 2027

  // ── QUARTI DI FINALE ─────────────────────────────────────────
  "13": [ { eventId: "", home: "", away: "", kickoff: "2027-04-06T19:00:00Z" } ], // Quarti Andata · 6-7 apr 2027
  "14": [ { eventId: "", home: "", away: "", kickoff: "2027-04-13T19:00:00Z" } ], // Quarti Ritorno · 13-14 apr 2027

  // ── SEMIFINALI ───────────────────────────────────────────────
  "15": [ { eventId: "", home: "", away: "", kickoff: "2027-04-27T19:00:00Z" } ], // Semifinali Andata · 27-28 apr 2027
  "16": [ { eventId: "", home: "", away: "", kickoff: "2027-05-04T19:00:00Z" } ], // Semifinali Ritorno · 4-5 mag 2027

  // ── FINALE ───────────────────────────────────────────────────
  "17": [ { eventId: "", home: "", away: "", kickoff: "2027-06-05T19:00:00Z" } ], // Finale · 5 giu 2027
};

// Non modificare — usato da app.js per il polling live
const POLLING_INTERVAL_MS = 5 * 60 * 1000; // 5 minuti
