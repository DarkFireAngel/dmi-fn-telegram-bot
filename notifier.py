"""
Notifier module for DMI(F-N) infobot.
Formats notices and broadcasts new announcements to subscribed users.
"""

import html
import logging
from typing import Dict, Any, List
from telegram.constants import ParseMode
from telegram.error import Forbidden, BadRequest
from telegram.ext import ContextTypes, Application

import database
import scraper
import config

logger = logging.getLogger(__name__)


def escape_html(text: str) -> str:
    """Escapes HTML entities for Telegram HTML parse mode."""
    if not text:
        return ""
    return html.escape(str(text))


def format_notice_message(notice: Dict[str, Any], is_alert: bool = True) -> str:
    """
    Formats a notice into clean Telegram HTML.
    """
    title = escape_html(notice.get("title", "Senza titolo"))
    author = escape_html(notice.get("author", "Docente DMI"))
    date = escape_html(notice.get("date", "Data non indicata"))
    link = notice.get("link", "")
    reason = escape_html(notice.get("reason", "Avviso per il Canale F-N"))

    body = notice.get("body", "").strip()
    if len(body) > 450:
        body = body[:450].rsplit(" ", 1)[0] + "..."
    body_escaped = escape_html(body)

    header = "🚨 <b>NUOVO AVVISO CANALE F-N</b>" if is_alert else "📌 <b>AVVISO CANALE F-N</b>"

    msg = (
        f"{header}\n\n"
        f"<b>{title}</b>\n\n"
        f"👤 <b>Docente / Fonte:</b> {author}\n"
        f"📅 <b>Data:</b> {date}\n"
        f"🎯 <b>Rilevanza:</b> <i>{reason}</i>\n"
    )

    if body_escaped:
        msg += f"\n📝 <b>Estratto:</b>\n<i>«{body_escaped}»</i>\n"

    if link:
        msg += f"\n🔗 <a href=\"{link}\">Leggi l'avviso completo sul sito DMI</a>"

    return msg


async def check_and_notify(app: Application) -> int:
    """
    Checks DMI site for new notices.
    Sends alerts to subscribed users for any newly published notice.
    Returns the number of new notices processed.
    """
    logger.info("Verifica nuovi avvisi DMI in corso...")

    # Fetch both docenti notices and general CdS notices
    try:
        notices = scraper.fetch_all_fn_notices(
            max_pages=config.SCAN_MAX_PAGES,
            include_cds_general=True
        )
    except Exception as e:
        logger.error(f"Errore durante lo scraping: {e}")
        return 0

    active_users = database.get_all_active_users(config.DB_PATH)
    if not active_users:
        logger.info("Nessun utente attivo registrato. Salvo solo gli avvisi.")

    new_notices_count = 0

    # Process notices in chronological order (oldest to newest)
    for n in reversed(notices):
        notice_id = n.get("id")
        if database.is_notice_seen(notice_id, config.DB_PATH):
            continue

        # Mark as seen in DB immediately
        database.mark_notice_seen(n, config.DB_PATH)
        new_notices_count += 1
        logger.info(f"Nuovo avviso rilevato: [{n.get('date')}] {n.get('title')}")

        # Broadcast to active users
        msg_text = format_notice_message(n, is_alert=True)
        source_type = n.get("source_type", "docente")

        for user in active_users:
            chat_id = user["chat_id"]
            include_cds = bool(user.get("include_cds", 0))

            # If notice is general CdS notice (without specific F-N mention)
            # and user disabled general CdS notices, skip for this user
            if source_type == "cds" and "menzione esplicita" not in n.get("reason", "").lower() and not include_cds:
                continue

            try:
                await app.bot.send_message(
                    chat_id=chat_id,
                    text=msg_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=False
                )
            except Forbidden:
                # User blocked or deleted the bot
                logger.warning(f"L'utente {chat_id} ha bloccato il bot. Disattivo.")
                database.set_user_active(chat_id, False, config.DB_PATH)
            except BadRequest as e:
                logger.error(f"Errore nell'invio a {chat_id}: {e}")
            except Exception as e:
                logger.error(f"Eccezione nell'invio a {chat_id}: {e}")

    logger.info(f"Controllo completato. Nuovi avvisi inviati: {new_notices_count}")
    return new_notices_count


async def check_and_notify_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Scheduled job runner for JobQueue."""
    await check_and_notify(context.application)
