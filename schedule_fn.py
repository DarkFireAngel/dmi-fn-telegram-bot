"""
Orario lezioni Canale F-N - CdL Informatica L-31 UniCT
Anno Accademico 2026/27 - I Semestre (Ottobre 2026 - Gennaio 2027)

Struttura: lista di lezioni con giorno (0=lun, 1=mar, ..., 4=ven),
ora inizio e fine (HH:MM), nome corso abbreviato, aula.

AGGIORNARE questo file ogni anno accademico con i nuovi orari ufficiali!
Fonte: https://web.dmi.unict.it/corsi/l-31/orario-delle-lezioni
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
# ORARIO F-N - I SEMESTRE AA 2026/27
# Modifica qui per aggiornare l'orario!
# ===========================================================
LEZIONI_FN = [
    # (giorno_settimana, ora_inizio, ora_fine, corso, aula)
    # Lunedì
    {"giorno": 0, "inizio": "09:00", "fine": "11:00", "corso": "Programmazione I e Lab (F-N)", "aula": "Aula Magna"},
    {"giorno": 0, "inizio": "11:00", "fine": "13:00", "corso": "Algebra Lineare e Geometria (F-N)", "aula": "Aula 10"},
    # Martedì
    {"giorno": 1, "inizio": "09:00", "fine": "11:00", "corso": "Strutture Discrete (F-N)", "aula": "Aula 8"},
    {"giorno": 1, "inizio": "14:00", "fine": "16:00", "corso": "Architettura degli Elaboratori e Lab (F-N)", "aula": "Aula 12"},
    # Mercoledì
    {"giorno": 2, "inizio": "09:00", "fine": "11:00", "corso": "Elementi di Analisi Matematica 2 (F-N)", "aula": "Aula 8"},
    {"giorno": 2, "inizio": "11:00", "fine": "13:00", "corso": "Programmazione I e Lab (F-N)", "aula": "Lab Informatica"},
    # Giovedì
    {"giorno": 3, "inizio": "09:00", "fine": "11:00", "corso": "Architettura degli Elaboratori e Lab (F-N)", "aula": "Aula 12"},
    {"giorno": 3, "inizio": "11:00", "fine": "13:00", "corso": "Strutture Discrete (F-N)", "aula": "Aula 8"},
    # Venerdì
    {"giorno": 4, "inizio": "09:00", "fine": "11:00", "corso": "Algebra Lineare e Geometria (F-N)", "aula": "Aula 10"},
    {"giorno": 4, "inizio": "11:00", "fine": "13:00", "corso": "Elementi di Analisi Matematica 2 (F-N)", "aula": "Aula 8"},
]

GIORNI_IT = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

# Frasi dinamiche per le situazioni
FRASI_ORA_IN_CORSO = [
    "🔴 <b>Sei in ritardo!</b> {corso} è iniziata alle {inizio} in <b>{aula}</b>. Corri!!! 🏃",
    "⚠️ Ehi, hai dimenticato qualcosa? <b>{corso}</b> è già iniziata ({inizio}) in <b>{aula}</b>! Sbrigati!",
    "😅 La lezione di <b>{corso}</b> è in corso dalle {inizio} in <b>{aula}</b>. Ci sei o stai dormendo?",
]

FRASI_TRA_POCO = [
    "⏰ Tra poco hai <b>{corso}</b> alle {inizio} in <b>{aula}</b>! Prepara zaino e caffè ☕",
    "🎒 Attenzione! <b>{corso}</b> inizia alle {inizio} in <b>{aula}</b>. Meglio muoversi!",
    "📚 Fra {minuti} minuti inizia <b>{corso}</b> ({inizio}) in <b>{aula}</b>. Sei già lì?",
    "🏫 Conto alla rovescia: {minuti} minuti a <b>{corso}</b> in <b>{aula}</b>. Non mancare!",
]

FRASI_BUONA_LEZIONE = [
    "✏️ <b>Buona lezione!</b> Stai frequentando <b>{corso}</b> in <b>{aula}</b>. Occhi aperti e domande al prof! 🎓",
    "🎓 Sei (probabilmente) in aula per <b>{corso}</b>! Buona lezione, spegni il telefono — ah aspetta, sei qui 😂",
    "📖 Lezione di <b>{corso}</b> in corso in <b>{aula}</b>. Studia duro che poi l'esame arriva in fretta! 💪",
]

FRASI_PROSSIMA_OGGI = [
    "📅 La prossima lezione di oggi è <b>{corso}</b> alle {inizio} in <b>{aula}</b>. Hai ancora {minuti} min di libertà 😎",
    "🕐 Prossimo appuntamento con la sofferenza: <b>{corso}</b> alle {inizio} ({minuti} min) in <b>{aula}</b>!",
    "☕ Goditi il tuo tempo libero! Fra {minuti} minuti ti aspetta <b>{corso}</b> in <b>{aula}</b>.",
]

FRASI_NESSUNA_LEZIONE = [
    "🎉 Oggi non hai lezioni del canale F-N! Sfrutta il tempo libero... o studia per gli esami 📚",
    "😴 Nessuna lezione oggi per il canale F-N. Riposa pure, ma non troppo eh!",
    "🌟 Giornata libera dal canale F-N! Forse è il momento giusto per ripassare... o per la PlayStation. Scegli sapientemente.",
]

FRASI_WEEKEND = [
    "🛋️ È weekend! Niente lezioni. Goditi il riposo (o studia, se sei masochista 😅)",
    "🎮 Weekend! Il canale F-N ti dà una pausa. Ricarica le energie per la settimana che verrà!",
    "🍕 Sabato/Domenica: zero lezioni, massima libertà! Buon weekend 🎊",
]

FRASI_DOPO_ULTIMA = [
    "🌆 Hai finito le lezioni per oggi! <b>Ultima lezione era {corso}</b>. Ora meriti del relax 🛁",
    "✅ Bel lavoro! Le lezioni F-N di oggi sono finite. Ultima: <b>{corso}</b>. Sei libero!",
    "🎯 Lezioni finite per oggi! Ultima in lista: <b>{corso}</b>. Ora studia o vai a mangiare, sei grande 🍔",
]


def _parse_time(t: str) -> datetime.time:
    h, m = t.split(":")
    return datetime.time(int(h), int(m))


def get_orario_message(now: Optional[datetime.datetime] = None) -> str:
    """
    Returns a dynamic timetable message for the F-N channel,
    with a smart/funny comment based on the current time and day.
    """
    if now is None:
        now = get_current_rome_time()

    weekday = now.weekday()  # 0=Mon, 6=Sun
    current_time = now.time()

    # Header: today's timetable
    giorno_str = GIORNI_IT[weekday] if weekday < 7 else "?"
    data_str = now.strftime("%d/%m/%Y")

    timetable_lines = []
    timetable_lines.append(f"📅 <b>Orario Canale F-N — {giorno_str} {data_str}</b>")
    timetable_lines.append("━" * 28)

    # Weekend
    if weekday >= 5:
        timetable_lines.append("\n🏖️ <i>Nessuna lezione nel weekend!</i>")
        orario_text = "\n".join(timetable_lines)
        commento = random.choice(FRASI_WEEKEND)
        return f"{orario_text}\n\n{commento}"

    # Filter today's lessons
    today_lessons = sorted(
        [l for l in LEZIONI_FN if l["giorno"] == weekday],
        key=lambda x: x["inizio"]
    )

    if not today_lessons:
        timetable_lines.append("\n🗓️ <i>Nessuna lezione del canale F-N oggi.</i>")
        orario_text = "\n".join(timetable_lines)
        commento = random.choice(FRASI_NESSUNA_LEZIONE)
        return f"{orario_text}\n\n{commento}"

    # Build timetable
    for l in today_lessons:
        timetable_lines.append(f"\n🕐 <b>{l['inizio']} – {l['fine']}</b>")
        timetable_lines.append(f"   📚 {l['corso']}")
        timetable_lines.append(f"   📍 {l['aula']}")

    # Full week timetable (collapsed)
    timetable_lines.append("\n" + "━" * 28)
    timetable_lines.append("📆 <b>Orario settimanale completo F-N:</b>")
    for giorno_idx in range(5):
        giorno_name = GIORNI_IT[giorno_idx]
        lez_giorno = sorted(
            [l for l in LEZIONI_FN if l["giorno"] == giorno_idx],
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
    """Returns a dynamic/funny message about the current lesson status."""
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
        # Check if it just started (within 20 min) → "sei in ritardo"
        start = _parse_time(ongoing["inizio"])
        start_total = start.hour * 60 + start.minute
        minutes_since_start = now_total - start_total

        if minutes_since_start < 20:
            return random.choice(FRASI_ORA_IN_CORSO).format(
                corso=ongoing["corso"], inizio=ongoing["inizio"], aula=ongoing["aula"]
            )
        else:
            return random.choice(FRASI_BUONA_LEZIONE).format(
                corso=ongoing["corso"], inizio=ongoing["inizio"], aula=ongoing["aula"]
            )

    if upcoming_today:
        # Sort by soonest
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
