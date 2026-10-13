"""
Main Telegram Bot module for DMI(F-N) infobot.
Comandi disponibili:
- /start       : Registra utente, messaggio di benvenuto (senza spam avvisi)
- /avvisi      : Pulisce la chat e mostra avvisi aggiornati Canale F-N
- /orario      : Orario lezioni F-N con commenti dinamici basati sull'ora
- /docenti     : Lista docenti Canale F-N
- /impostazioni: Toggle avvisi generali CdS
- /check       : Controllo manuale nuovi avvisi
- /stop        : Disiscriviti dalle notifiche automatiche
- /help        : Guida comandi
Admin only:
- /broadcast <testo> : Invia messaggio a tutti gli iscritti
- /iscritti          : Numero di utenti attivi
"""

import logging
import asyncio
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode, ChatType
from telegram.error import Forbidden, BadRequest
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    Application
)

import config
import database
import scraper
import notifier
import schedule_fn

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  KEYBOARDS
# ─────────────────────────────────────────────

def get_main_keyboard() -> InlineKeyboardMarkup:
    """Returns the main inline navigation keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("📢 Avvisi F-N", callback_data="btn_avvisi"),
            InlineKeyboardButton("📅 Orario", callback_data="btn_orario"),
        ],
        [
            InlineKeyboardButton("👨‍🏫 Docenti F-N", callback_data="btn_docenti"),
            InlineKeyboardButton("⚙️ Impostazioni", callback_data="btn_settings"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_avvisi_keyboard() -> InlineKeyboardMarkup:
    """Returns keyboard shown below avvisi with a refresh button."""
    keyboard = [
        [InlineKeyboardButton("🔄 Aggiorna Avvisi", callback_data="btn_avvisi_refresh")],
        [InlineKeyboardButton("« Menu principale", callback_data="btn_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_settings_keyboard(include_cds: bool) -> InlineKeyboardMarkup:
    """Returns settings inline keyboard with toggle buttons."""
    cds_label = "✅ Avvisi CdS L-31: ATTIVI" if include_cds else "❌ Avvisi CdS L-31: DISATTIVATI"
    keyboard = [
        [InlineKeyboardButton(cds_label, callback_data="toggle_cds")],
        [InlineKeyboardButton("« Torna al Menu", callback_data="btn_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def is_admin(chat_id: int) -> bool:
    """Returns True if the user is the configured admin."""
    if hasattr(config, "ADMIN_CHAT_IDS") and chat_id in config.ADMIN_CHAT_IDS:
        return True
    return config.ADMIN_CHAT_ID is not None and chat_id == config.ADMIN_CHAT_ID


async def delete_old_avvisi(bot, chat_id: int) -> None:
    """Deletes all previously tracked avvisi messages for a user."""
    msg_ids = database.pop_avvisi_messages(chat_id, config.DB_PATH)
    for mid in msg_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=mid)
        except Exception:
            pass  # Message may be too old or already deleted


async def send_and_track(update_or_message, chat_id: int, text: str, **kwargs):
    """Sends a message and tracks its ID for later deletion."""
    if hasattr(update_or_message, "reply_text"):
        msg = await update_or_message.reply_text(text, **kwargs)
    else:
        msg = await update_or_message.reply_text(text, **kwargs)
    database.save_avvisi_message(chat_id, msg.message_id, config.DB_PATH)
    return msg


async def show_avvisi(bot, chat_id: int, include_cds: bool, reply_target=None):
    """
    Core avvisi logic. Deletes old avvisi messages, fetches fresh ones, sends them.
    reply_target: a Message object to reply to (for /avvisi command), or None.
    """
    # 1. Delete old avvisi messages
    await delete_old_avvisi(bot, chat_id)

    # 2. Send temporary loading message
    if reply_target:
        loading_msg = await reply_target.reply_text("🔍 Aggiorno gli avvisi dal sito DMI...")
    else:
        loading_msg = await bot.send_message(chat_id=chat_id, text="🔍 Aggiorno gli avvisi dal sito DMI...")

    try:
        notices = scraper.fetch_all_fn_notices(max_pages=3, include_cds_general=include_cds)
    except Exception as e:
        logger.error(f"Errore fetch avvisi: {e}")
        try:
            await loading_msg.edit_text("❌ Errore durante il recupero degli avvisi. Riprova tra poco.")
        except Exception:
            pass
        return
    finally:
        try:
            await loading_msg.delete()
        except Exception:
            pass

    if not notices:
        msg = await bot.send_message(
            chat_id=chat_id,
            text="📭 Nessun avviso recente trovato per il Canale F-N.",
            reply_markup=get_avvisi_keyboard()
        )
        database.save_avvisi_message(chat_id, msg.message_id, config.DB_PATH)
        return

    # 3. Header message
    header_msg = await bot.send_message(
        chat_id=chat_id,
        text=f"📢 <b>{len(notices[:5])} avvisi recenti — Canale F-N:</b>",
        parse_mode=ParseMode.HTML
    )
    database.save_avvisi_message(chat_id, header_msg.message_id, config.DB_PATH)

    # 4. Each notice
    for n in notices[:5]:
        text = notifier.format_notice_message(n, is_alert=False)
        m = await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        database.save_avvisi_message(chat_id, m.message_id, config.DB_PATH)

    # 5. Footer with refresh button
    footer_msg = await bot.send_message(
        chat_id=chat_id,
        text="↩️ Usa il pulsante per aggiornare o tornare al menu:",
        reply_markup=get_avvisi_keyboard()
    )
    database.save_avvisi_message(chat_id, footer_msg.message_id, config.DB_PATH)


# ─────────────────────────────────────────────
#  COMMAND HANDLERS
# ─────────────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /start. Registers user and shows welcome (no avvisi spam)."""
    user = update.effective_user
    chat = update.effective_chat

    if chat.type != ChatType.PRIVATE:
        await update.message.reply_text(
            "⚠️ Avviami in chat privata per ricevere gli avvisi personali!"
        )
        return

    is_new = database.register_user(
        chat_id=chat.id,
        username=user.username,
        first_name=user.first_name,
        db_path=config.DB_PATH
    )

    if is_new:
        status_txt = "🎉 Ti sei registrato con successo!"
    else:
        status_txt = "✅ Il tuo abbonamento è già attivo."

    welcome_text = (
        f"👋 <b>Ciao {notifier.escape_html(user.first_name)}!</b>\n\n"
        f"{status_txt}\n\n"
        f"Riceverai in automatico tutti gli <b>avvisi del Canale F-N</b> "
        f"del CdL Informatica L-31 (DMI UniCT) appena vengono pubblicati.\n\n"
        f"🌐 <a href=\"https://web.dmi.unict.it/corsi/l-31\">web.dmi.unict.it/corsi/l-31</a>\n\n"
        f"Scegli un'opzione qui sotto:"
    )

    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_keyboard(),
        disable_web_page_preview=True
    )


async def avvisi_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /avvisi. Cleans chat and shows fresh F-N notices."""
    chat_id = update.effective_chat.id
    user_data = database.get_user(chat_id, config.DB_PATH)
    include_cds = bool(user_data.get("include_cds", 0)) if user_data else False

    # Delete the user's /avvisi command message too for a cleaner chat
    try:
        await update.message.delete()
    except Exception:
        pass

    await show_avvisi(
        bot=context.bot,
        chat_id=chat_id,
        include_cds=include_cds,
        reply_target=None
    )


async def orario_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /orario. Shows F-N timetable with smart time-based comment."""
    msg = schedule_fn.get_orario_message()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Aggiorna orario", callback_data="btn_orario")],
        [InlineKeyboardButton("« Menu principale", callback_data="btn_menu")],
    ])
    await update.message.reply_text(
        msg,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )


async def docenti_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /docenti. Lists all F-N professors."""
    profs = scraper.get_fn_professors()

    text = (
        "👨‍🏫 <b>Docenti Canale F-N — L-31 Informatica:</b>\n\n"
        "Avvisi di questi docenti vengono monitorati automaticamente:\n\n"
    )

    for name, data in profs.items():
        courses_str = "\n".join(f"  • {c}" for c in data.get("fn_courses", []))
        url = data.get("url", "")
        clean_name = notifier.escape_html(name)

        if url:
            text += f"🔹 <a href=\"{url}\"><b>Prof. {clean_name}</b></a>\n{notifier.escape_html(courses_str)}\n\n"
        else:
            text += f"🔹 <b>Prof. {clean_name}</b>\n{notifier.escape_html(courses_str)}\n\n"

    text += (
        "💡 <i>Lista aggiornata da:</i>\n"
        "🔗 <a href=\"https://web.dmi.unict.it/corsi/l-31/docenti\">Docenti CdL Informatica L-31</a>"
    )

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_keyboard(),
        disable_web_page_preview=True
    )


async def impostazioni_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /impostazioni."""
    chat_id = update.effective_chat.id
    user_data = database.get_user(chat_id, config.DB_PATH)
    include_cds = bool(user_data.get("include_cds", 0)) if user_data else False

    cds_desc = "🟢 ATTIVI" if include_cds else "🔴 DISATTIVATI"

    text = (
        "⚙️ <b>Impostazioni Notifiche:</b>\n\n"
        "🟢 <b>Avvisi Docenti Canale F-N:</b> SEMPRE ATTIVI\n"
        f"🔵 <b>Avvisi Generali CdS L-31:</b> {cds_desc}\n\n"
        "Con gli avvisi CdS attivi ricevi anche: orari, appelli riservati, test d'ingresso, ecc."
    )

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_settings_keyboard(include_cds)
    )


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /check. Forces an immediate check for new notices."""
    msg = await update.message.reply_text("🔄 Controllo manuale avvisi in corso...")
    count = await notifier.check_and_notify(context.application)
    if count == 0:
        await msg.edit_text("✅ Nessun nuovo avviso trovato.")
    else:
        await msg.edit_text(f"✅ Trovati e inviati <b>{count}</b> nuovi avvisi!", parse_mode=ParseMode.HTML)


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /stop. Unsubscribes user from automatic alerts."""
    chat_id = update.effective_chat.id
    database.set_user_active(chat_id, False, config.DB_PATH)

    await update.message.reply_text(
        "🛑 <b>Notifiche automatiche disattivate.</b>\n\n"
        "Non riceverai più avvisi automatici.\n"
        "Per riattivare scrivi <code>/start</code> in qualsiasi momento.",
        parse_mode=ParseMode.HTML
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /help."""
    help_text = (
        "ℹ️ <b>Comandi disponibili:</b>\n\n"
        "• <code>/start</code> — Avvia o riattiva il bot\n"
        "• <code>/avvisi</code> — Avvisi aggiornati F-N (pulisce la chat)\n"
        "• <code>/orario</code> — Orario lezioni con commento in tempo reale\n"
        "• <code>/docenti</code> — Lista docenti del Canale F-N\n"
        "• <code>/impostazioni</code> — Attiva/disattiva avvisi generali CdS\n"
        "• <code>/check</code> — Controlla subito nuovi avvisi\n"
        "• <code>/stop</code> — Disattiva notifiche automatiche\n\n"
        "🔍 Il bot controlla ogni 10 minuti il sito DMI UniCT e ti avvisa subito!\n\n"
        "🌐 <a href=\"https://web.dmi.unict.it/corsi/l-31\">DMI UniCT L-31</a>"
    )

    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_keyboard(),
        disable_web_page_preview=True
    )


# ─────────────────────────────────────────────
#  ADMIN COMMANDS
# ─────────────────────────────────────────────

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin only: /broadcast <messaggio> — Sends a message to all active users."""
    chat_id = update.effective_chat.id

    if not is_admin(chat_id):
        await update.message.reply_text("⛔ Comando riservato all'amministratore.")
        return

    if update.message.reply_to_message:
        raw_text = update.message.reply_to_message.text_html or update.message.reply_to_message.text or ""
        broadcast_msg = f"📣 <b>Comunicazione dal gestore del bot:</b>\n\n{raw_text}"
    elif context.args:
        message_text = " ".join(context.args)
        broadcast_msg = (
            f"📣 <b>Comunicazione dal gestore del bot:</b>\n\n"
            f"{notifier.escape_html(message_text)}"
        )
    else:
        await update.message.reply_text(
            "📣 Utilizzo:\n"
            "• <code>/broadcast Il tuo messaggio qui</code>\n"
            "• Oppure rispondi a un messaggio con <code>/broadcast</code> per inoltrarlo a tutti.",
            parse_mode=ParseMode.HTML
        )
        return

    active_users = database.get_all_active_users(config.DB_PATH)
    sent = 0
    failed = 0

    status_msg = await update.message.reply_text(
        f"📤 Invio in corso a {len(active_users)} utenti...",
    )

    for user in active_users:
        try:
            await context.bot.send_message(
                chat_id=user["chat_id"],
                text=broadcast_msg,
                parse_mode=ParseMode.HTML
            )
            sent += 1
        except Forbidden:
            database.set_user_active(user["chat_id"], False, config.DB_PATH)
            failed += 1
        except Exception as e:
            logger.error(f"Broadcast error per {user['chat_id']}: {e}")
            failed += 1

    await status_msg.edit_text(
        f"✅ <b>Broadcast completato!</b>\n\n"
        f"• Inviato a: <b>{sent}</b> utenti\n"
        f"• Falliti/bloccati: <b>{failed}</b>",
        parse_mode=ParseMode.HTML
    )


async def iscritti_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin only: /iscritti — Shows count of active subscribers."""
    chat_id = update.effective_chat.id

    if not is_admin(chat_id):
        await update.message.reply_text("⛔ Comando riservato all'amministratore.")
        return

    count = database.count_active_users(config.DB_PATH)
    all_users = database.get_all_active_users(config.DB_PATH)

    # Build a short list of users
    users_list = ""
    for u in all_users[:20]:
        name = u.get("first_name") or "?"
        username = f"@{u['username']}" if u.get("username") else "no username"
        users_list += f"\n  • {notifier.escape_html(name)} ({username}) — <code>{u['chat_id']}</code>"

    extra = f"\n  <i>...e altri {count - 20}</i>" if count > 20 else ""

    await update.message.reply_text(
        f"👥 <b>Utenti iscritti attivi: {count}</b>\n{users_list}{extra}",
        parse_mode=ParseMode.HTML
    )


# ─────────────────────────────────────────────
#  CALLBACK HANDLER
# ─────────────────────────────────────────────

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles all inline button clicks."""
    query = update.callback_query
    await query.answer()

    data = query.data
    chat_id = update.effective_chat.id

    if data in ("btn_avvisi", "btn_avvisi_refresh"):
        # Delete the message with the button before refreshing
        try:
            await query.message.delete()
        except Exception:
            pass

        user_data = database.get_user(chat_id, config.DB_PATH)
        include_cds = bool(user_data.get("include_cds", 0)) if user_data else False
        await show_avvisi(
            bot=context.bot,
            chat_id=chat_id,
            include_cds=include_cds,
            reply_target=None
        )

    elif data == "btn_orario":
        msg = schedule_fn.get_orario_message()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Aggiorna orario", callback_data="btn_orario")],
            [InlineKeyboardButton("« Menu principale", callback_data="btn_menu")],
        ])
        try:
            await query.message.edit_text(msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        except BadRequest:
            # Message unchanged (same time, same lesson) — ignore
            pass
        try:
            await query.answer("⏱️ Orario aggiornato!")
        except Exception:
            pass

    elif data == "btn_docenti":
        profs = scraper.get_fn_professors()
        text = "👨‍🏫 <b>Docenti e Insegnamenti Canale F-N:</b>\n\n"
        for name, pdata in profs.items():
            courses_str = "\n".join(f"  • {c}" for c in pdata.get("fn_courses", []))
            url = pdata.get("url", "")
            clean_name = notifier.escape_html(name)
            if url:
                text += f"🔹 <a href=\"{url}\"><b>Prof. {clean_name}</b></a>\n{notifier.escape_html(courses_str)}\n\n"
            else:
                text += f"🔹 <b>Prof. {clean_name}</b>\n{notifier.escape_html(courses_str)}\n\n"

        await query.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Menu principale", callback_data="btn_menu")]]),
            disable_web_page_preview=True
        )

    elif data == "btn_settings":
        user_data = database.get_user(chat_id, config.DB_PATH)
        include_cds = bool(user_data.get("include_cds", 0)) if user_data else False
        cds_desc = "🟢 ATTIVI" if include_cds else "🔴 DISATTIVATI"
        text = (
            "⚙️ <b>Impostazioni Notifiche:</b>\n\n"
            "🟢 <b>Avvisi Docenti Canale F-N:</b> SEMPRE ATTIVI\n"
            f"🔵 <b>Avvisi Generali CdS L-31:</b> {cds_desc}\n\n"
            "Con gli avvisi CdS attivi ricevi anche: orari, appelli riservati, test d'ingresso, ecc."
        )
        await query.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_settings_keyboard(include_cds)
        )

    elif data == "toggle_cds":
        new_state = database.toggle_user_cds(chat_id, config.DB_PATH)
        cds_desc = "🟢 ATTIVI" if new_state else "🔴 DISATTIVATI"
        text = (
            "⚙️ <b>Impostazioni aggiornate!</b>\n\n"
            "🟢 <b>Avvisi Docenti Canale F-N:</b> SEMPRE ATTIVI\n"
            f"🔵 <b>Avvisi Generali CdS L-31:</b> {cds_desc}"
        )
        await query.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_settings_keyboard(new_state)
        )

    elif data == "btn_menu":
        await query.message.edit_text(
            "📋 <b>Menu principale — Bot Avvisi DMI (Canale F-N)</b>\n\nCosa vuoi fare?",
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_keyboard()
        )


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main() -> None:
    """Initializes and runs the bot."""
    if not config.BOT_TOKEN or config.BOT_TOKEN == "IL_TUO_TOKEN_TELEGRAM_QUI":
        print("\n" + "=" * 65)
        print("ERRORE: TELEGRAM_BOT_TOKEN non configurato!")
        print("Apri il file '.env' e inserisci il token ottenuto da @BotFather.")
        print("Esempio: TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
        print("=" * 65 + "\n")
        return

    # Initialize SQLite database
    database.init_db(config.DB_PATH)

    # Seed initial existing notices to avoid spam on startup
    logger.info("Seed avvisi storici iniziali...")
    try:
        initial_notices = scraper.fetch_all_fn_notices(max_pages=2, include_cds_general=True)
        seeded = database.seed_initial_notices(initial_notices, config.DB_PATH)
        logger.info(f"Seed completato: {seeded} avvisi registrati.")
    except Exception as e:
        logger.error(f"Errore seed iniziale: {e}")

    # Build PTB Application
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("avvisi", avvisi_command))
    app.add_handler(CommandHandler("orario", orario_command))
    app.add_handler(CommandHandler("docenti", docenti_command))
    app.add_handler(CommandHandler("impostazioni", impostazioni_command))
    app.add_handler(CommandHandler("check", check_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("help", help_command))

    # Admin-only handlers
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("iscritti", iscritti_command))

    # Inline button handler
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Periodic background job
    if app.job_queue:
        logger.info(f"JobQueue attivo: controllo ogni {config.CHECK_INTERVAL_SECONDS}s.")
        app.job_queue.run_repeating(
            notifier.check_and_notify_job,
            interval=config.CHECK_INTERVAL_SECONDS,
            first=30
        )
    else:
        logger.warning("JobQueue non disponibile! Notifiche automatiche disabilitate.")

    logger.info("Bot DMI(F-N) avviato. In attesa di messaggi...")
    app.run_polling()


if __name__ == "__main__":
    main()
