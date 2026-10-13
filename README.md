# 🤖 DMI UniCT (L-31 Informatica) - Bot Avvisi Canale F-N

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/new)

Un bot Telegram intelligente e completo progettato per monitorare in tempo reale il portale ufficiale del **Dipartimento di Matematica e Informatica (DMI) dell'Università di Catania** per il Corso di Laurea in Informatica (L-31):
🌐 [https://web.dmi.unict.it/corsi/l-31](https://web.dmi.unict.it/corsi/l-31)

Il bot recapita direttamente **in privato su Telegram** tutti gli avvisi pubblicati dai professori del **Canale F-N** e tutti gli avvisi rilevanti per tale canale, con supporto per l'orario delle lezioni, commenti intelligenti in tempo reale, pulizia automatica dei messaggi e strumenti di amministrazione.

---

> [!NOTE]
> ☁️ **Servizio di Hosting Online: Railway**  
> Il bot è ospitato online su **[Railway](https://railway.com)** per restare attivo 24 ore su 24, 7 giorni su 7, senza dover tenere il computer acceso.  
> Ogni modifica pushata su GitHub sul ramo `main` viene automaticamente compilata e deployata da Railway!

---

## 🌟 Caratteristiche Principali

- 📬 **Ricezione Automatica in Privato**: Basta inviare `/start` in chat privata per iscriversi (senza ricevere spam di vecchi avvisi all'avvio). Non appena un docente F-N pubblica un nuovo avviso sul sito DMI, il bot te lo invia subito in chat!
- 🎓 **Scelta Anno di Corso (1°, 2° o 3° Anno)**: Nelle `/impostazioni` puoi impostare il tuo anno di corso (1° Anno impostato di base). L'orario e le notifiche si adattano automaticamente agli insegnamenti ufficiali del tuo anno!
- 📅 **Orario Lezioni con "AI / Smart Time"**: Visualizza l'orario del tuo anno con messaggi dinamici e commenti spiritosi basati sull'ora e sul giorno corrente (*sei in ritardo, lezione tra poco, buona lezione, weekend, lezioni finite, ecc.*). Puoi anche cambiare anno al volo direttamente dai pulsanti dell'orario.
- 🔄 **Chat Sempre Pulita**: Ad ogni `/avvisi`, `/orario` o quando torni al **Menu principale**, la chat viene automaticamente ripulita dai messaggi precedenti per mantenere una vista sempre ordinata.
- 👨‍🏫 **Riconoscimento Automatico Docenti Canale F-N**: Il bot analizza la pagina ufficiale dei docenti del CdS L-31 rilevando automaticamente i docenti assegnati al Canale F-N (*Calvagna, Farinella, Spata, Cavallaro, Cutello, Naselli, Zappala'*).
- 🎯 **Filtro Intelligente**:
  1. Notifica tutti gli avvisi pubblicati dai docenti del Canale F-N.
  2. Notifica tutti gli avvisi con citazione esplicita del `Canale F-N`.
  3. Esclude avvisi riservati ad altri canali (es. `Canale AE`, `Canale O-Z`).
- ⚙️ **Filtro Opzionale Avvisi Generali CdS**: Ricezione opzionale degli avvisi generali del CdS L-31 (orari, appelli riservati, test d'ingresso, ecc.).
- 👑 **Funzioni Admin Riservate**:
  - `/broadcast <testo>`: Per inviare una comunicazione a tutti gli iscritti al bot.
  - `/iscritti`: Per consultare il numero totale e la lista degli utenti attivi.
- 🕒 **Monitoraggio Continuo in Background**: Job programmato ogni 5 minuti per rilevare subito qualsiasi nuovo avviso sul portale DMI.
- 💾 **Database SQLite**: Gestione degli iscritti, anno di studio, preferenze e tracciamento messaggi.

---

## 📁 Struttura del Progetto

```text
DMI(F-N)infobot/
├── bot.py             # Entrypoint principale del Bot Telegram (comandi, tastiere, admin)
├── schedule_fn.py     # Modulo orario lezioni F-N con commenti dinamici sull'ora
├── scraper.py         # Web scraping per docenti e avvisi DMI UniCT
├── notifier.py        # Formattazione messaggi HTML e broadcasting agli utenti
├── database.py        # Database SQLite (utenti, preferenze, avvisi visti, message tracking)
├── config.py          # Configurazione caricata da variabili d'ambiente / .env
├── requirements.txt   # Dipendenze Python (python-telegram-bot, bs4, tzdata, ecc.)
├── test_suite.py      # Test automatici per verificare tutte le funzionalità
├── railway.json       # Configurazione del deploy per Railway
├── Dockerfile         # Immagine Docker con supporto timezone Europe/Rome
├── Procfile           # Definizione processo worker per cloud hosting
├── .env.example       # Template del file delle variabili d'ambiente
└── .env               # File con il token Telegram e le chiavi locali (non committato)
```

---

## 📱 Comandi Disponibili nel Bot

| Comando | Descrizione |
|---|---|
| `/start` | Registra l'utente alle notifiche (senza spam) e apre il menu con i pulsanti. |
| `/avvisi` | Pulisce la chat precedente e mostra gli avvisi recenti del Canale F-N. |
| `/orario` | Mostra l'orario delle lezioni del Canale F-N con commento dinamico basato sull'orario. |
| `/docenti` | Mostra l'elenco dei docenti del Canale F-N e i relativi insegnamenti. |
| `/impostazioni` | Permette di attivare/disattivare gli avvisi generali del CdS L-31. |
| `/check` | Forza un controllo manuale immediato per nuovi avvisi. |
| `/stop` | Disattiva le notifiche automatiche (riattivabili in qualunque momento con `/start`). |
| `/help` | Mostra la guida all'uso del bot. |
| `/broadcast <testo>` | 👑 *(Solo Admin)* Invia un messaggio a tutti gli iscritti al bot. |
| `/iscritti` | 👑 *(Solo Admin)* Mostra il numero e l'elenco degli iscritti attivi. |

---

## ☁️ Deploy su Railway (Hosting 24/7)

Il bot è configurato per funzionare ininterrottamente su **Railway**:

1. Accedi alla dashboard di [Railway](https://railway.com/dashboard).
2. Seleziona il progetto `dmi-fn-telegram-bot` (collegato alla repo GitHub `DarkFireAngel/dmi-fn-telegram-bot`).
3. Nella scheda **Variables**, assicurati che siano impostate:
   - `TELEGRAM_BOT_TOKEN`: Il token del tuo bot fornito da [@BotFather](https://t.me/BotFather).
   - `ADMIN_CHAT_ID`: Il tuo ID Telegram (es. `848188619`) per i comandi admin `/broadcast` e `/iscritti`.
   - `TZ`: `Europe/Rome` (già impostato anche nel Dockerfile).
4. Ogni `git push` sul repository attiva automaticamente una nuova build e il deploy su Railway.

---

## 💻 Esecuzione in Locale

### 1. Installazione dipendenze
```bash
pip install -r requirements.txt
```

### 2. Configurazione `.env`
Crea o modifica il file `.env`:
```env
TELEGRAM_BOT_TOKEN=il_tuo_token_qui
CHECK_INTERVAL_SECONDS=600
SCAN_MAX_PAGES=2
DB_PATH=dmi_bot.db
ADMIN_CHAT_ID=848188619
```

### 3. Avvio
```bash
python bot.py
```

---

## 🧪 Esecuzione dei Test Automatici

Per verificare il corretto funzionamento dello scraper, del calcolo dell'orario e del database:

```bash
python test_suite.py
```
