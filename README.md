# 🤖 DMI UniCT (L-31 Informatica) - Bot Avvisi Canale F-N

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/DarkFireAngel/dmi-fn-telegram-bot)


Un bot Telegram intelligente progettato per monitorare in tempo reale il portale ufficiale del **Dipartimento di Matematica e Informatica (DMI) dell'Università di Catania** per il Corso di Laurea in Informatica (L-31):
🌐 [https://web.dmi.unict.it/corsi/l-31](https://web.dmi.unict.it/corsi/l-31)


Il bot recapita direttamente **in privato su Telegram** tutti gli avvisi pubblicati dai professori del **Canale F-N** e tutti gli avvisi con riferimenti a tale canale.

---

## 🌟 Caratteristiche Principali

- 📬 **Ricezione Automatica in Privato**: Basta inviare `/start` in chat privata con il bot per iscriversi alle notifiche.
- 👨‍🏫 **Riconoscimento Automatico Docenti Canale F-N**: Il bot scansiona la pagina ufficiale docenti (`/corsi/l-31/docenti`) rilevando i docenti assegnati al Canale F-N (es. *Calvagna, Farinella, Spata, Cavallaro, Cutello, Naselli, Zappala'*).
- 🎯 **Filtro Intelligente**: Notifica:
  1. Tutti gli avvisi pubblicati dai professori del Canale F-N.
  2. Tutti gli avvisi contenenti nel titolo o nel testo riferimenti espliciti a `Canale F-N`, `F - N` o corsi dedicati.
  3. Esclude avvisi riservati ad altri canali specifici (es. `Canale AE`, `Canale O-Z`).
- ⚙️ **Filtro Opzionale Avvisi Generali CdS**: Possibilità di ricevere (tramite pulsante o `/impostazioni`) anche gli avvisi generali del Corso di Studi (es. orari, appelli riservati, test d'ingresso).
- 🕒 **Monitoraggio in Background**: Job automatico programmato (di default ogni 10 minuti) che rileva nuovi avvisi e li invia all'istante a tutti gli utenti iscritti.
- 💾 **Database SQLite**: Gestione persistente degli iscritti e storico avvisi per prevenire duplicati o notifiche ripetute.
- 🔘 **Pulsanti Interattivi**: Navigazione intuitiva tramite Inline Keyboard direttamente in chat.

---

## 📁 Struttura del Progetto

```text
DMI(F-N)infobot/
├── bot.py             # Entrypoint principale del Bot Telegram con gestione comandi e bottoni
├── scraper.py         # Motore di web scraping per docenti e avvisi DMI UniCT
├── notifier.py        # Formattazione messaggi HTML e broadcasting agli utenti
├── database.py        # Gestione database SQLite (utenti, preferenze, avvisi visti)
├── config.py          # Caricamento configurazioni da file .env
├── requirements.txt   # Dipendenze Python (python-telegram-bot, bs4, python-dotenv, ecc.)
├── test_suite.py      # Test automatici per validare scraper, database e notifiche
├── .env.example       # Template del file di configurazione
└── .env               # File con il token Telegram e le impostazioni locali
```

---

## 🚀 Guida all'Installazione e Configurazione

### 1. Requisiti
- **Python 3.10+** (consigliato Python 3.11, 3.12 o 3.13)
- Le dipendenze già installate tramite:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Creare il Bot su Telegram e ottenere il Token
1. Apri Telegram e cerca [@BotFather](https://t.me/BotFather).
2. Avvia la chat e invia il comando:
   ```text
   /newbot
   ```
3. Scegli un nome per il tuo bot (es. `DMI Info F-N Bot`).
4. Scegli uno username univoco che finisca con `bot` (es. `dmi_fn_unict_bot`).
5. `@BotFather` ti invierà il **token HTTP API** (una stringa del tipo `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`).

### 3. Configurare il file `.env`
Apri il file `.env` nella cartella del progetto e inserisci il token appena ottenuto:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
CHECK_INTERVAL_SECONDS=600
SCAN_MAX_PAGES=2
DB_PATH=dmi_bot.db
```

- `CHECK_INTERVAL_SECONDS`: Intervallo in secondi tra ogni controllo automatico (600 = ogni 10 minuti).
- `SCAN_MAX_PAGES`: Numero di pagine del portale DMI da analizzare (default 2 pagine).

### 4. Avviare il Bot
Esegui il bot con:
```bash
python bot.py
```

Vedrai comparire nella console:
```text
Verifica seed avvisi storici iniziali...
Configuro JobQueue: controllo ogni 600 secondi.
Bot DMI(F-N) avviato con successo. In attesa di messaggi...
```

---

## 📱 Comandi Disponibili nel Bot

| Comando | Descrizione |
|---|---|
| `/start` | Registra l'utente per le notifiche automatiche, invia il messaggio di benvenuto e mostra subito gli ultimi avvisi rilevati. |
| `/avvisi` | Mostra su richiesta gli ultimi avvisi pubblicati per il Canale F-N. |
| `/docenti` | Mostra la lista dei docenti e dei relativi corsi del Canale F-N con link al profilo DMI. |
| `/impostazioni` | Permette di attivare/disattivare la ricezione degli avvisi generali del CdS L-31. |
| `/check` | Forza un controllo immediato sul sito DMI per verificare la presenza di nuovi avvisi. |
| `/stop` | Disattiva le notifiche automatiche (riattivabili in qualunque momento con `/start`). |
| `/help` | Mostra la guida completa all'uso del bot. |

---

## 🧪 Esecuzione dei Test Automatici

Per verificare la corretta connessione al sito del DMI, il funzionamento dello scraper e del database SQLite, puoi eseguire la suite di test:

```bash
python test_suite.py
```

Tutti i test verificheranno:
- Il parsing della tabella docenti Canale F-N dal vivo.
- Il parsing delle schede avvisi dal portale DMI.
- Il ciclo di vita degli utenti e delle preferenze nel database SQLite.
- La corretta formattazione e sanitizzazione HTML dei messaggi per Telegram.
