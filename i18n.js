// ============================================================
// FANTASY ARENA — i18n.js
// Sistema di internazionalizzazione IT / EN
// ============================================================

const TRANSLATIONS = {
  it: {
    meta: {
      title: "ArenaUCL – Fantasy Football Champions League 2026/27"
    },
    nav: {
      home: "Home",
      regolamento: "Regolamento",
      classifica: "Classifica",
      stats: "Statistiche",
      giornata: "Giornata",
      squadra: "La mia Squadra",
      giocatori: "Giocatori",
      admin: "Admin",
      chat: "Chat",
      menu: "Menu",
      profile_title: "Profilo e Leghe"
    },
    hero: {
      subtitle: "Fantasy Football · Champions League 2026/27",
      desc: "La piattaforma di giochi fantasy sul calcio. Gioca con la UEFA Champions League 2026/27 e conquista il trofeo più prestigioso del calcio per club.",
      login: "Accedi",
      register: "Registrati"
    },
    intro: {
      title: "Cos'è ArenaUCL?",
      p1: "<strong>ArenaUCL</strong> è il <strong>gioco di fantasy football dedicato alla UEFA Champions League 2026/27</strong>. Crea la tua lega privata, costruisci una rosa di <strong>36 giocatori</strong> — uno per ogni club partecipante — e sfida i tuoi amici per tutta la durata del torneo, dalla League Phase alla Finale.",
      p2: "Il regolamento è semplice: ogni giocatore della tua rosa accumula punti in base alle prestazioni reali in campo. I voti, i bonus ed i malus si basano sulle statistiche ufficiali fornite da <strong>SofaScore</strong>, ma fai attenzione perché ai nostri bonus piace cambiare in base al ruolo del giocatore.. e scegli con cura il tuo <strong>Capitano</strong>! Potrà rivelarsi l'arma in più per battere i tuoi amici e alzare la coppa.",
      stories_title: "Highlights UCL",
      wc_title: "UEFA Champions League 2026/27",
      wc_desc: "36 club &nbsp;·&nbsp; League Phase + Fase Eliminatoria &nbsp;·&nbsp; Settembre 2026 – Maggio 2027"
    },
    rules: {
      section_title: "Il Regolamento",
      read_full: "Leggi il regolamento completo",
      back_home: "Torna alla Home",
      goals_title: "Gol e Bonus",
      goals_text: "I Bonus variano in base al ruolo! : <strong>Gol di portieri e difensori +5</strong>, <strong>Gol di centrocampisti +4</strong>, <strong>gol di attaccanti +3</strong>.<br>Anche gli assist cambiano! <strong>+2</strong> per difensori e portieri, <strong>+1,5</strong> per i centrocampisti e <strong>+1</strong> per gli attaccanti.",
      malus_title: "Malus Decisivi",
      malus_text: "Espulsione (-1), Ammonizione (-0.5), Autogol (-2) e Rigore Sbagliato (-3). Evita i giocatori troppo fallosi nella tua rosa per non scendere in classifica.",
      captain_title: "Capitano",
      captain_text: "Scegli con attenzione il tuo Capitano: riceve un bonus <strong>+2</strong> per ogni giornata in cui scende in campo con voto base ≥ 7. Non puoi scegliere un attaccante come capitano. <strong>Il capitano non può essere cambiato né sostituito dopo la conferma della rosa.</strong>",
      keeper_title: "Portieri",
      keeper_text: "La porta inviolata conferisce un fantastico <strong>+2</strong>. Rigore parato <strong>+3</strong>. Ogni gol subito vale <strong>−1</strong>. Prenderai un portiere di un top club europeo?",
      subs_title: "Sostituzioni",
      subs_text: "Hai a disposizione <strong>8 sostituzioni totali</strong> (al massimo <strong>2 per ruolo</strong>) da usare nelle <strong>4 finestre disponibili durante la League Phase</strong>. Il giocatore entrante deve avere lo <strong>stesso ruolo e lo stesso club</strong> di quello uscente. <strong>Il capitano non può essere sostituito.</strong><br>Le finestre si aprono dopo le Giornate 2, 4, 6 e 8. <strong>Nessun cambio è possibile dalla fase a eliminazione diretta in avanti.</strong>",
      votes_title: "Voti",
      votes_text: "La redazione di riferimento per voti ed eventuali bonus e malus sarà quella di Sofascore.com; ricordo che lo standard della redazione per una prestazione \"normale\" è di 6.5."
    },
    classifica: {
      title: "Classifica",
      subtitle: "Champions League 2026/27 – Aggiornamento live",
      event_title: "UEFA Champions League 2026/27",
      event_sub: "36 club · League Phase + Fase Eliminatoria · Settembre 2026 – Maggio 2027",
      col_rank: "#",
      col_name: "Partecipante",
      sort_day: "Giornata corrente ↕",
      sort_total: "Totale ↕",
      col_day: "Giornata",
      col_total: "Totale",
      empty: "Nessun partecipante. Aggiungili in Admin.",
      pending: "in attesa"
    },
    giornata: {
      title: "Giornata",
      subtitle: "Rose di tutti i partecipanti con voti aggiornati",
      search_placeholder: "Nome partecipante...",
      expand: "Espandi",
      collapse: "Chiudi"
    },
    voti: {
      title: "Voti Squadre",
      subtitle: "Voti ufficiali per ogni giocatore",
      edit_mode: "Modalità modifica",
      exit: "Esci",
      pwd_placeholder: "Password admin...",
      edit_btn: "Modifica",
      squadra: "Squadra",
      giornata: "Giornata",
      save: "Salva voti"
    },
    giocatori: {
      title: "Giocatori",
      subtitle: "Database giocatori selezionabili",
      search_placeholder: "Cerca giocatore o squadra...",
      all: "Tutti",
      portieri: "🧤 Portieri",
      difensori: "🛡 Difensori",
      centrocampisti: "⚙️ Centrocampisti",
      attaccanti: "⚽ Attaccanti"
    },
    admin: {
      locked_title: "Area Riservata",
      locked_text: "Questa sezione è accessibile solo all'amministratore della lega.",
      title: "Amministrazione",
      subtitle: "Gestione partecipanti e rose",
      exit: "Esci",
      participants: "Partecipanti",
      add: "Aggiungi",
      name_placeholder: "Nome partecipante",
      clear: "Svuota partecipanti e rose",
      load_squad: "Carica Rosa da File",
      participant_label: "Partecipante",
      file_label: "Carica file rosa (.csv)",
      file_format: "Formato: Ruolo,Giocatore,Club",
      manual_label: "Oppure inserisci manualmente:",
      manual_btn: "Inserimento manuale",
      captains: "Capitani",
      captains_desc: "Imposta il capitano (+2 pt se voto ≥ 7, non attaccanti).",
      subs: "Sostituzioni",
      subs_desc: "8 sostituzioni totali • al massimo 2 per ruolo • stesso ruolo e stesso club.",
      danger: "Zona Pericolosa",
      danger_text: "Questa azione è irreversibile. La lega, tutti i partecipanti, le rose e i voti verranno eliminati definitivamente.",
      delete_league: "Elimina questa Lega"
    },
    modal: {
      superadmin_title: "⚡ Superadmin",
      superadmin_pwd: "Password",
      superadmin_placeholder: "Password superadmin...",
      superadmin_btn: "Accedi",
      manual_title: "Inserimento Manuale Rosa",
      manual_save: "Salva Rosa"
    },
    sidebar: {
      title: "Menu",
      loading: "⏳ Caricamento...",
      login_header: "Accedi o Registrati",
      tab_login: "Accedi",
      tab_register: "Registrati",
      btn_login: "Accedi",
      btn_register: "Registrati",
      my_leagues: "🏆 Le mie Leghe",
      create_league: "➕ Crea Lega",
      join_league: "🔗 Unisciti a una Lega",
      logout: "Esci",
      forgot_pwd: "Password dimenticata?",
      reset_desc: "Inserisci la tua email e ti invieremo un link per reimpostare la password.",
      reset_btn: "Invia link di reset",
      reset_sent: "✓ Email inviata! Controlla la tua casella (anche spam).",
      back_login: "Torna al login"
    },
    footer: {
      tagline: "🏆 ArenaUCL — Gioco fantasy gratuito a scopo puramente ricreativo e non commerciale",
      copyright_pre: "© 2026",
      copyright_post: "— Tutti i diritti riservati sul codice e sui contenuti originali di Fantasy Arena (fantaarena.it). È vietata la riproduzione, anche parziale, senza autorizzazione scritta dell'autore.",
      disclaimer: "I voti, le statistiche e i dati di gioco sono forniti da Sofascore, di cui Fantasy Arena non rivendica alcuna proprietà. I nomi, i loghi e i marchi relativi alla UEFA, ai club di calcio e ai calciatori appartengono ai rispettivi titolari e sono citati esclusivamente a scopo informativo e ludico.",
      privacy: "Privacy Policy",
      cookie: "Cookie Policy",
      terms: "Termini e Condizioni",
      back_home: "Torna a Fantasy Arena",
      manage_cookies: "Gestisci Cookie"
    },
    roles: {
      P: "Portiere", D: "Difensore", C: "Centrocampista", A: "Attaccante",
      Ps: "Portieri", Ds: "Difensori", Cs: "Centrocampisti", As: "Attaccanti"
    },
    giornate: {
      "1": "G1", "2": "G2", "3": "G3", "4": "G4",
      "5": "G5", "6": "G6", "7": "G7", "8": "G8",
      "9": "Playoff A", "10": "Playoff R",
      "11": "Ottavi A", "12": "Ottavi R",
      "13": "Quarti A", "14": "Quarti R",
      "15": "Semifinali A", "16": "Semifinali R",
      "17": "Finale"
    },
    match_status: {
      upcoming: "In programma",
      live: "IN CORSO 🔴",
      recent: "Appena finita",
      done: "Conclusa"
    },
    common: {
      save: "Salva",
      cancel: "Annulla",
      confirm: "Conferma",
      delete: "Elimina",
      back: "Indietro",
      close: "Chiudi",
      loading: "Caricamento...",
      sv: "SV",
      captain: "Capitano",
      substitute: "Sostituto",
      no_players: "Nessun giocatore trovato.",
      no_data: "Nessun dato disponibile."
    }
  },

  en: {
    meta: {
      title: "ArenaUCL – Fantasy Football Champions League 2026/27"
    },
    nav: {
      home: "Home",
      regolamento: "Rules",
      classifica: "Standings",
      stats: "Statistics",
      giornata: "Matchday",
      squadra: "My Team",
      giocatori: "Players",
      admin: "Admin",
      chat: "Chat",
      menu: "Menu",
      profile_title: "Profile & Leagues"
    },
    hero: {
      subtitle: "Fantasy Football · Champions League 2026/27",
      desc: "The fantasy football platform dedicated to club football. Play the UEFA Champions League 2026/27 and conquer the most prestigious trophy in European club football.",
      login: "Sign In",
      register: "Sign Up"
    },
    intro: {
      title: "What is ArenaUCL?",
      p1: "<strong>ArenaUCL</strong> is the <strong>fantasy football game dedicated to the UEFA Champions League 2026/27</strong>. Create your private league, build a squad of <strong>36 players</strong> — one for each participating club — and challenge your friends for the entire tournament, from the League Phase to the Final.",
      p2: "The rules are simple: each player in your squad earns points based on their real match performances. Ratings, bonuses and penalties are based on official statistics provided by <strong>SofaScore</strong>, but watch out — our bonuses change based on the player's position. Choose your <strong>Captain</strong> wisely! They could be the key to beating your friends and lifting the trophy.",
      stories_title: "UCL Highlights",
      wc_title: "UEFA Champions League 2026/27",
      wc_desc: "36 clubs &nbsp;·&nbsp; League Phase + Knockout Stage &nbsp;·&nbsp; September 2026 – May 2027"
    },
    rules: {
      section_title: "Rules",
      read_full: "Read the full rulebook",
      back_home: "Back to Home",
      goals_title: "Goals & Bonuses",
      goals_text: "Bonuses vary by position! <strong>Goalkeeper and defender goals +5</strong>, <strong>Midfielder goals +4</strong>, <strong>Forward goals +3</strong>.<br>Assists also vary: <strong>+2</strong> for defenders and goalkeepers, <strong>+1.5</strong> for midfielders and <strong>+1</strong> for forwards.",
      malus_title: "Key Penalties",
      malus_text: "Red card (-1), Yellow card (-0.5), Own goal (-2) and Missed penalty (-3). Avoid error-prone players in your squad to stay at the top of the standings.",
      captain_title: "Captain",
      captain_text: "Choose your Captain carefully: they receive a <strong>+2</strong> bonus for each matchday they play with a base rating ≥ 7. You cannot choose a forward as captain. <strong>The captain cannot be changed or substituted after confirming your squad.</strong>",
      keeper_title: "Goalkeepers",
      keeper_text: "A clean sheet earns a fantastic <strong>+2</strong> bonus. Penalty saved <strong>+3</strong>. Every goal conceded is <strong>−1</strong>. Will you pick a goalkeeper from a top European club?",
      subs_title: "Substitutions",
      subs_text: "You have <strong>8 total substitutions</strong> (at most <strong>2 per position</strong>) to use in the <strong>4 windows available during the League Phase</strong>. The incoming player must have the <strong>same position and the same club</strong> as the outgoing one. <strong>The captain cannot be substituted.</strong><br>Windows open after Matchdays 2, 4, 6 and 8. <strong>No changes are allowed from the knockout stage onwards.</strong>",
      votes_title: "Ratings",
      votes_text: "The reference source for ratings and any bonuses/penalties is Sofascore.com. The standard rating for a \"normal\" performance is 6.5."
    },
    classifica: {
      title: "Standings",
      subtitle: "Champions League 2026/27 – Live updates",
      event_title: "UEFA Champions League 2026/27",
      event_sub: "36 clubs · League Phase + Knockout Stage · September 2026 – May 2027",
      col_rank: "#",
      col_name: "Participant",
      sort_day: "Current matchday ↕",
      sort_total: "Total ↕",
      col_day: "Matchday",
      col_total: "Total",
      empty: "No participants yet. Add them in Admin.",
      pending: "pending"
    },
    giornata: {
      title: "Matchday",
      subtitle: "All participants' squads with updated ratings",
      search_placeholder: "Participant name...",
      expand: "Expand",
      collapse: "Close"
    },
    voti: {
      title: "Team Ratings",
      subtitle: "Official ratings for each player",
      edit_mode: "Edit mode",
      exit: "Exit",
      pwd_placeholder: "Admin password...",
      edit_btn: "Edit",
      squadra: "Team",
      giornata: "Matchday",
      save: "Save ratings"
    },
    giocatori: {
      title: "Players",
      subtitle: "Selectable players database",
      search_placeholder: "Search player or team...",
      all: "All",
      portieri: "🧤 Goalkeepers",
      difensori: "🛡 Defenders",
      centrocampisti: "⚙️ Midfielders",
      attaccanti: "⚽ Forwards"
    },
    admin: {
      locked_title: "Restricted Area",
      locked_text: "This section is only accessible to the league administrator.",
      title: "Administration",
      subtitle: "Manage participants and squads",
      exit: "Exit",
      participants: "Participants",
      add: "Add",
      name_placeholder: "Participant name",
      clear: "Clear participants and squads",
      load_squad: "Load Squad from File",
      participant_label: "Participant",
      file_label: "Load squad file (.csv)",
      file_format: "Format: Role,Player,Club",
      manual_label: "Or enter manually:",
      manual_btn: "Manual entry",
      captains: "Captains",
      captains_desc: "Set the captain (+2 pts if rating ≥ 7, no forwards).",
      subs: "Substitutions",
      subs_desc: "8 total substitutions • at most 2 per position • same role and same club.",
      danger: "Danger Zone",
      danger_text: "This action is irreversible. The league, all participants, squads and ratings will be permanently deleted.",
      delete_league: "Delete this League"
    },
    modal: {
      superadmin_title: "⚡ Superadmin",
      superadmin_pwd: "Password",
      superadmin_placeholder: "Superadmin password...",
      superadmin_btn: "Sign In",
      manual_title: "Manual Squad Entry",
      manual_save: "Save Squad"
    },
    sidebar: {
      title: "Menu",
      loading: "⏳ Loading...",
      login_header: "Sign In or Register",
      tab_login: "Sign In",
      tab_register: "Register",
      btn_login: "Sign In",
      btn_register: "Register",
      my_leagues: "🏆 My Leagues",
      create_league: "➕ Create League",
      join_league: "🔗 Join a League",
      logout: "Sign Out",
      forgot_pwd: "Forgot password?",
      reset_desc: "Enter your email and we'll send you a link to reset your password.",
      reset_btn: "Send reset link",
      reset_sent: "✓ Email sent! Check your inbox (and spam folder).",
      back_login: "Back to login"
    },
    footer: {
      tagline: "⚽ Fantasy Arena — Free fantasy game for purely recreational and non-commercial purposes",
      copyright_pre: "© 2026",
      copyright_post: "— All rights reserved on the original code and content of Fantasy Arena (fantaarena.it). Reproduction, even partial, without written permission from the author is prohibited.",
      disclaimer: "Ratings, statistics and game data are provided by Sofascore, of which Fantasy Arena claims no ownership. Names, logos and trademarks related to UEFA, football clubs and players belong to their respective owners and are cited solely for informational and recreational purposes.",
      privacy: "Privacy Policy",
      cookie: "Cookie Policy",
      terms: "Terms & Conditions",
      back_home: "Back to Fantasy Arena",
      manage_cookies: "Manage Cookies"
    },
    roles: {
      P: "Goalkeeper", D: "Defender", C: "Midfielder", A: "Forward",
      Ps: "Goalkeepers", Ds: "Defenders", Cs: "Midfielders", As: "Forwards"
    },
    giornate: {
      "1": "G1", "2": "G2", "3": "G3", "4": "G4",
      "5": "G5", "6": "G6", "7": "G7", "8": "G8",
      "9": "Playoff 1L", "10": "Playoff 2L",
      "11": "R16 1L", "12": "R16 2L",
      "13": "QF 1L", "14": "QF 2L",
      "15": "SF 1L", "16": "SF 2L",
      "17": "Final"
    },
    match_status: {
      upcoming: "Scheduled",
      live: "LIVE 🔴",
      recent: "Just finished",
      done: "Finished"
    },
    common: {
      save: "Save",
      cancel: "Cancel",
      confirm: "Confirm",
      delete: "Delete",
      back: "Back",
      close: "Close",
      loading: "Loading...",
      sv: "DNP",
      captain: "Captain",
      substitute: "Substitute",
      no_players: "No players found.",
      no_data: "No data available."
    }
  }
};

// ── Helper functions ─────────────────────────────────────────

let currentLang = localStorage.getItem("ucl_lang") || "it";

function t(key) {
  const keys = key.split(".");
  let val = TRANSLATIONS[currentLang];
  for (const k of keys) {
    if (val == null) return key;
    val = val[k];
  }
  return val != null ? val : key;
}

function setLang(lang) {
  currentLang = lang;
  localStorage.setItem("ucl_lang", lang);
  document.documentElement.lang = lang;
  applyTranslations();
  // Re-render current page to update dynamic content
  if (typeof renderPage === "function" && typeof currentPage === "function") {
    renderPage(currentPage());
  }
}

function toggleLang() {
  setLang(currentLang === "it" ? "en" : "it");
}

function applyTranslations() {
  // Text/HTML content (use innerHTML to support <strong>, <br> etc.)
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const val = t(el.dataset.i18n);
    if (val !== el.dataset.i18n) el.innerHTML = val;
  });
  // Placeholders
  document.querySelectorAll("[data-i18n-ph]").forEach(el => {
    const val = t(el.dataset.i18nPh);
    if (val !== el.dataset.i18nPh) el.placeholder = val;
  });
  // Title attributes
  document.querySelectorAll("[data-i18n-title]").forEach(el => {
    const val = t(el.dataset.i18nTitle);
    if (val !== el.dataset.i18nTitle) el.title = val;
  });
  // Document title
  document.title = t("meta.title");
  // Language switcher button
  const btn = document.getElementById("langSwitcher");
  if (btn) btn.textContent = currentLang === "it" ? "🇬🇧 EN" : "🇮🇹 IT";
}
