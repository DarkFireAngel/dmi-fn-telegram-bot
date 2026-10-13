"""
Orario lezioni Canale F-N - CdL Informatica L-31 UniCT
Anno Accademico 2026/27 - I Semestre (Ottobre 2026 - Gennaio 2027)

Supporta 1° Anno, 2° Anno e 3° Anno con orari estratti dai documenti ufficiali DMI.
Fonte ufficiale: https://web.dmi.unict.it/corsi/l-31/orario-delle-lezioni
"""

import datetime
import random
from typing import Optional, List, Dict, Any

try:
    from zoneinfo import ZoneInfo
    ROME_TZ = ZoneInfo("Europe/Rome")
except Exception:
    ROME_TZ = None


def get_current_rome_time() -> datetime.datetime:
    """Returns current datetime in Europe/Rome timezone."""
    if ROME_TZ:
        return datetime.datetime.now(ROME_TZ)
    return datetime.datetime.now()


# ===========================================================
# ORARIO UFFICIALE 1° ANNO — CANALE F-N (I Semestre AA 2026/27)
# Fonte: 1anno.pdf (DMI UniCT)
# ===========================================================
LEZIONI_1_ANNO = [
    # Lunedì
    {"giorno": 0, "inizio": "08:00", "fine": "11:00", "corso": "Algebra Lineare e Geometria (Prof. Zappalà)", "aula": "Aula 4"},
    # Martedì
    {"giorno": 1, "inizio": "09:00", "fine": "11:00", "corso": "Strutture Discrete (Prof. Cutello / Cavallaro)", "aula": "Aula 4"},
    {"giorno": 1, "inizio": "11:00", "fine": "14:00", "corso": "Programmazione 1 (Prof. Farinella / Calvagna)", "aula": "Aula 4"},
    # Mercoledì
    {"giorno": 2, "inizio": "08:00", "fine": "10:00", "corso": "Algebra Lineare e Geometria (Prof. Zappalà)", "aula": "Aula 4"},
    {"giorno": 2, "inizio": "10:00", "fine": "13:00", "corso": "Architettura degli Elaboratori (Prof. Spata)", "aula": "Aula 4"},
    # Giovedì
    {"giorno": 3, "inizio": "09:00", "fine": "11:00", "corso": "Strutture Discrete (Prof. Cutello / Cavallaro)", "aula": "Aula 4"},
    {"giorno": 3, "inizio": "11:00", "fine": "14:00", "corso": "Programmazione 1 (Prof. Farinella / Calvagna)", "aula": "Aula 4"},
    # Venerdì
    {"giorno": 4, "inizio": "08:00", "fine": "11:00", "corso": "Architettura degli Elaboratori (Prof. Spata)", "aula": "Aula 4"},
]

# ===========================================================
# ORARIO UFFICIALE 2° ANNO — CANALE F-N / A-L (I Semestre AA 2026/27)
# Fonte: 2anno_0.pdf (DMI UniCT)
# ===========================================================
LEZIONI_2_ANNO = [
    # Lunedì
    {"giorno": 0, "inizio": "08:00", "fine": "11:00", "corso": "Algoritmi e laboratorio (Prof. Faro)", "aula": "Aula 3"},
    {"giorno": 0, "inizio": "11:00", "fine": "13:00", "corso": "Database (Prof. Pulvirenti / Micale)", "aula": "Aula 3"},
    # Martedì
    {"giorno": 1, "inizio": "08:00", "fine": "10:00", "corso": "Elementi di Analisi Matematica 2 (Prof. Naselli)", "aula": "Aula 3"},
    {"giorno": 1, "inizio": "10:00", "fine": "13:00", "corso": "Interazione e Multimedia (Prof. Stanco / Guarnera F.)", "aula": "Aula 3"},
    # Mercoledì
    {"giorno": 2, "inizio": "08:00", "fine": "10:00", "corso": "Database (Prof. Pulvirenti / Micale)", "aula": "Aula 3"},
    {"giorno": 2, "inizio": "10:00", "fine": "13:00", "corso": "Elementi di Analisi Matematica 2 (Prof. Naselli)", "aula": "Aula 3"},
    # Giovedì
    {"giorno": 3, "inizio": "10:00", "fine": "13:00", "corso": "Interazione e Multimedia (Prof. Stanco / Guarnera F.)", "aula": "Aula 3"},
    # Venerdì
    {"giorno": 4, "inizio": "08:00", "fine": "11:00", "corso": "Algoritmi e laboratorio (Prof. Faro)", "aula": "Aula 3"},
    {"giorno": 4, "inizio": "11:00", "fine": "13:00", "corso": "Database (Prof. Pulvirenti / Micale)", "aula": "Aula 3"},
]

# ===========================================================
# ORARIO UFFICIALE 3° ANNO — Materie Comuni e Principali (I Semestre AA 2026/27)
# Fonte: 3anno_0.pdf (DMI UniCT)
# ===========================================================
LEZIONI_3_ANNO = [
    # Lunedì
    {"giorno": 0, "inizio": "08:00", "fine": "10:00", "corso": "Embedded Systems (Prof. Santoro C.)", "aula": "Aula 24"},
    {"giorno": 0, "inizio": "10:00", "fine": "13:00", "corso": "Artificial Intelligence (Prof. Pavone)", "aula": "Aula 24"},
    # Martedì
    {"giorno": 1, "inizio": "08:00", "fine": "10:00", "corso": "Metodi Matematici e Statistici (Prof. Falsaperla)", "aula": "Aula 23"},
    {"giorno": 1, "inizio": "10:00", "fine": "12:00", "corso": "Fisica (Prof. Ruggieri)", "aula": "Aula 23"},
    # Mercoledì
    {"giorno": 2, "inizio": "15:00", "fine": "17:00", "corso": "Curriculum: Natural Language Processing / Altro", "aula": "Aula 2"},
    # Giovedì
    {"giorno": 3, "inizio": "08:00", "fine": "10:00", "corso": "Metodi Matematici e Statistici (Prof. Falsaperla)", "aula": "Aula 23"},
    {"giorno": 3, "inizio": "10:00", "fine": "12:00", "corso": "Fisica (Prof. Ruggieri)", "aula": "Aula 23"},
    # Venerdì
    {"giorno": 4, "inizio": "08:00", "fine": "11:00", "corso": "Artificial Intelligence (Prof. Pavone)", "aula": "Aula 23"},
    {"giorno": 4, "inizio": "11:00", "fine": "13:00", "corso": "Embedded Systems (Prof. Santoro C.)", "aula": "Aula 23"},
    {"giorno": 4, "inizio": "17:00", "fine": "19:00", "corso": "Machine Learning (Prof. Farinella)", "aula": "Aula 2"},
]

ORARI_PER_ANNO = {
    1: LEZIONI_1_ANNO,
    2: LEZIONI_2_ANNO,
    3: LEZIONI_3_ANNO,
}

GIORNI_IT = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

# Frasi dinamiche spiritose
FRASI_ORA_IN_CORSO = [
    "🔴 <b>Sei in ritardo!</b> <b>{corso}</b> è iniziata alle {inizio} in <b>{aula}</b>. Corri verso l'aula! 🏃💨",
    "⚠️ Ehi! Ti sei perso? <b>{corso}</b> è già iniziata ({inizio}) in <b>{aula}</b>! Entra piano senza fare rumore 🤫",
    "😅 La lezione di <b>{corso}</b> è in corso dalle {inizio} in <b>{aula}</b>. Ci sei o sei ancora al bar?",
]

FRASI_TRA_POCO = [
    "⏰ Tra poco hai <b>{corso}</b> alle {inizio} in <b>{aula}</b>! Prepara zaino e caffè ☕",
    "🎒 Attenzione! <b>{corso}</b> inizia alle {inizio} in <b>{aula}</b>. Tempo di dirigersi verso l'aula!",
    "📚 Fra {minuti} minuti inizia <b>{corso}</b> ({inizio}) in <b>{aula}</b>. Posto preso in prima fila?",
    "🏫 Conto alla rovescia: mancano {minuti} minuti a <b>{corso}</b> in <b>{aula}</b>. Buona lezione! 💪",
]

FRASI_BUONA_LEZIONE = [
    "✏️ <b>Buona lezione!</b> Stai seguendo <b>{corso}</b> in <b>{aula}</b>. Metti il telefono in silenzioso e ascolta il prof! 🎓",
    "🎓 Sei in aula per <b>{corso}</b>! Occhi aperti e prendi appunti che poi all'esame servono 😂",
    "📖 Lezione di <b>{corso}</b> in corso in <b>{aula}</b> fino alle {fine}. Concentrazione al massimo! 💡",
]

FRASI_PROSSIMA_OGGI = [
    "📅 La prossima lezione di oggi è <b>{corso}</b> alle {inizio} in <b>{aula}</b>. Hai ancora {minuti} min di pausa 😎",
    "🕐 Prossimo appuntamento: <b>{corso}</b> alle {inizio} (tra {minuti} min) in <b>{aula}</b>!",
    "☕ Pausa relax! Fra {minuti} minuti ti aspetta <b>{corso}</b> in <b>{aula}</b>.",
]

FRASI_NESSUNA_LEZIONE = [
    "🎉 Oggi non hai lezioni in orario! Sfrutta il tempo libero... o approfittane per studiare 📚",
    "😴 Nessuna lezione oggi. Riposo meritato, ma ricordati che la sessione non aspetta nessuno!",
    "🌟 Giornata libera! Un buon caffè e relax totale.",
]

FRASI_WEEKEND = [
    "🛋️ È weekend! Niente lezioni. Ricarica le batterie per la prossima settimana! 🍕",
    "🎮 Weekend! Zero corsi universitari oggi. Goditi il meritato riposo!",
    "☀️ Sabato e Domenica: libertà assoluta! Ci rivediamo Lunedì 🎊",
]

FRASI_DOPO_ULTIMA = [
    "🌆 Lezioni finite per oggi! Ultima in programma era <b>{corso}</b>. Ora relax meritato 🛁",
    "✅ Bel lavoro! Giornata accademica conclusa. Ultima: <b>{corso}</b>. Sei libero!",
    "🎯 Finito per oggi! Ultima lezione completata. Chiudi i libri e svagati 🍔",
]


def _parse_time(t: str) -> datetime.time:
    h, m = t.split(":")
    return datetime.time(int(h), int(m))


def get_orario_message(year: int = 1, now: Optional[datetime.datetime] = None) -> str:
    """
    Returns a dynamic timetable message for the specified year of study (1, 2, or 3),
    with a smart/funny comment based on the current time and day.
    """
    if now is None:
        now = get_current_rome_time()

    lessons_list = ORARI_PER_ANNO.get(year, LEZIONI_1_ANNO)
    weekday = now.weekday()  # 0=Mon, 6=Sun
    current_time = now.time()

    giorno_str = GIORNI_IT[weekday] if weekday < 7 else "?"
    data_str = now.strftime("%d/%m/%Y")

    timetable_lines = []
    timetable_lines.append(f"📅 <b>Orario {year}° Anno (Canale F-N) — {giorno_str} {data_str}</b>")
    timetable_lines.append("━" * 28)

    # Weekend
    if weekday >= 5:
        timetable_lines.append("\n🏖️ <i>Nessuna lezione nel weekend!</i>")
        orario_text = "\n".join(timetable_lines)
        commento = random.choice(FRASI_WEEKEND)
        return f"{orario_text}\n\n{commento}"

    # Filter today's lessons
    today_lessons = sorted(
        [l for l in lessons_list if l["giorno"] == weekday],
        key=lambda x: x["inizio"]
    )

    if not today_lessons:
        timetable_lines.append(f"\n🗓️ <i>Nessuna lezione programmata per oggi ({year}° anno).</i>")
        orario_text = "\n".join(timetable_lines)
        commento = random.choice(FRASI_NESSUNA_LEZIONE)
        return f"{orario_text}\n\n{commento}"

    # Build today's timetable
    for l in today_lessons:
        timetable_lines.append(f"\n🕐 <b>{l['inizio']} – {l['fine']}</b>")
        timetable_lines.append(f"   📚 {l['corso']}")
        timetable_lines.append(f"   📍 {l['aula']}")

    # Full week timetable (summary)
    timetable_lines.append("\n" + "━" * 28)
    timetable_lines.append(f"📆 <b>Orario settimanale completo ({year}° Anno):</b>")
    for giorno_idx in range(5):
        giorno_name = GIORNI_IT[giorno_idx]
        lez_giorno = sorted(
            [l for l in lessons_list if l["giorno"] == giorno_idx],
            key=lambda x: x["inizio"]
        )
        if lez_giorno:
            lez_str = " | ".join(f"{l['inizio']} {l['corso'].split('(')[0].strip()}" for l in lez_giorno)
            timetable_lines.append(f"<b>{giorno_name[:3]}:</b> {lez_str}")

    orario_text = "\n".join(timetable_lines)

    # Smart comment based on time
    commento = _get_smart_comment(today_lessons, current_time)

    return f"{orario_text}\n\n{commento}"


def _get_smart_comment(lessons: List[Dict[str, Any]], current_time: datetime.time) -> str:
    """Returns a dynamic/funny message about current lesson status."""
    now_total = current_time.hour * 60 + current_time.minute
    ongoing = None
    upcoming_today = []

    for l in lessons:
        start = _parse_time(l["inizio"])
        end = _parse_time(l["fine"])
        start_total = start.hour * 60 + start.minute
        end_total = end.hour * 60 + end.minute

        if start_total <= now_total <= end_total:
            ongoing = l
        elif start_total > now_total:
            upcoming_today.append((start_total - now_total, l))

    if ongoing:
        start = _parse_time(ongoing["inizio"])
        start_total = start.hour * 60 + start.minute
        minutes_since_start = now_total - start_total

        if minutes_since_start < 20:
            return random.choice(FRASI_ORA_IN_CORSO).format(
                corso=ongoing["corso"], inizio=ongoing["inizio"], aula=ongoing["aula"]
            )
        else:
            return random.choice(FRASI_BUONA_LEZIONE).format(
                corso=ongoing["corso"], inizio=ongoing["inizio"], aula=ongoing["aula"], fine=ongoing["fine"]
            )

    if upcoming_today:
        upcoming_today.sort(key=lambda x: x[0])
        minuti, next_l = upcoming_today[0]

        if minuti <= 30:
            return random.choice(FRASI_TRA_POCO).format(
                corso=next_l["corso"], inizio=next_l["inizio"],
                aula=next_l["aula"], minuti=minuti
            )
        else:
            return random.choice(FRASI_PROSSIMA_OGGI).format(
                corso=next_l["corso"], inizio=next_l["inizio"],
                aula=next_l["aula"], minuti=minuti
            )

    # All lessons done for today
    last_l = lessons[-1]
    return random.choice(FRASI_DOPO_ULTIMA).format(
        corso=last_l["corso"], inizio=last_l["inizio"], aula=last_l["aula"]
    )
