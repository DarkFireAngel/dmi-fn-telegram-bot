"""
Main Telegram Bot module for DMI(F-N) infobot.
Provides commands:
- /start: Register user, welcome message, send latest notices
- /avvisi: Fetch and display recent F-N notices
- /docenti: List professors of Canale F-N
- /impostazioni: Toggle general CdS notices and preferences
- /check: Manually trigger check for new notices
- /stop: Unsubscribe from automatic alerts
- /help: Detailed help and bot info
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

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Returns the main inline navigation keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("📢 Ultimi Avvisi", callback_data="btn_avvisi"),
            InlineKeyboardButton("👨‍🏫 Docenti F-N", callback_data="btn_docenti")
        ],
        [
            InlineKeyboardButton("⚙️ Impostazioni", callback_data="btn_settings"),
            InlineKeyboardButton("❓ Aiuto", callback_data="btn_help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_settings_keyboard(include_cds: bool) -> InlineKeyboardMarkup:
    """Returns settings inline keyboard with toggle buttons."""
    cds_label = "✅ Avvisi CdS L-31: ATTIVI" if include_cds else "❌ Avvisi CdS L-31: DISATTIVATI"
    keyboard = [
        [InlineKeyboardButton(cds_label, callback_data="toggle_cds")],
        [InlineKeyboardButton("🔄 Aggiorna Avvisi Adesso", callback_data="btn_avvisi")],
        [InlineKeyboardButton("« Torna al Menu", callback_data="btn_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /start command. Registers user and sends welcome info."""
    user = update.effective_user
    chat = update.effective_chat

    if chat.type != ChatType.PRIVATE:
        await update.message.reply_text(
            "⚠️ Per favore, avvia il bot in una chat privata per ricevere gli avvisi personali!\n"
            "Clicca qui per avviarmi: @DMI_FN_Infobot (o il tuo bot)"
        )
        return

    # Register user in DB
    is_new = database.register_user(
        chat_id=chat.id,
        username=user.username,
        first_name=user.first_name,
        db_path=config.DB_PATH
    )

    status_txt = "ti sei registrato con successo" if is_new else "il tuo abbonamento è attivo"

    welcome_text = (
        f"👋 <b>Ciao {notifier.escape_html(user.first_name)}! Benvenuto nel Bot Avvisi DMI (Canale F-N)</b> 🎓\n\n"
        f"Da adesso {status_txt} per ricevere <b>in privato</b> tutti gli avvisi pubblicati sul sito del "
        f"<b>DMI UniCT</b> (Corso di Laurea in Informatica L-31):\n"
        f"🌐 <a href=\"https://web.dmi.unict.it/corsi/l-31\">web.dmi.unict.it/corsi/l-31</a>\n\n"
        f"📌 <b>Cosa riceverai automaticamente:</b>\n"
        f"• Tutti gli avvisi dei docenti del <b>Canale F-N</b>\n"
        f"• Avvisi con riferimenti diretti al <b>Canale F-N</b>\n"
        f"• Notifiche in tempo reale appena pubblicate sul sito DMI\n\n"
        f"Usa i pulsanti qui sotto o scrivi <code>/avvisi</code> per consultare gli avvisi recenti!"
    )

    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_keyboard(),
        disable_web_page_preview=True
    )

    # Immediately show the 2 latest notices so user sees it in action
    try:
        user_data = database.get_user(chat.id, config.DB_PATH)
        include_cds = bool(user_data.get("include_cds", 0)) if user_data else False
        recent_notices = scraper.fetch_all_fn_notices(max_pages=2, include_cds_general=include_cds)
        if recent_notices:
            await update.message.reply_text(
                "📋 <b>Ecco gli ultimi avvisi rilevati per il Canale F-N:</b>",
                parse_mode=ParseMode.HTML
            )
            for n in recent_notices[:2]:
                msg = notifier.format_notice_message(n, is_alert=False)
                await update.message.reply_text(
                    msg,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
    except Exception as e:
        logger.error(f"Errore nel recupero avvisi di benvenuto: {e}")


async def avvisi_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /avvisi command. Shows recent notices for Canale F-N."""
    chat_id = update.effective_chat.id

    wait_msg = await update.message.reply_text("🔍 Controllo gli ultimi avvisi sul sito DMI...")

    try:
        user_data = database.get_user(chat_id, config.DB_PATH)
        include_cds = bool(user_data.get("include_cds", 0)) if user_data else False

        notices = scraper.fetch_all_fn_notices(max_pages=3, include_cds_general=include_cds)

        await wait_msg.delete()

        if not notices:
            await update.message.reply_text(
                "📭 Al momento non ci sono avvisi recenti per il Canale F-N.",
                reply_markup=get_main_keyboard()
            )
            return

        await update.message.reply_text(
            f"📢 <b>Trovati {len(notices[:5])} avvisi recenti per il Canale F-N:</b>",
            parse_mode=ParseMode.HTML
        )

        for n in notices[:5]:
            msg = notifier.format_notice_message(n, is_alert=False)
            await update.message.reply_text(
                msg,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )

    except Exception as e:
        logger.error(f"Errore in /avvisi: {e}")
        await wait_msg.edit_text(f"❌ Si è verificato un errore durante il recupero degli avvisi: {e}")


async def docenti_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /docenti command. Lists all professors associated with Canale F-N."""
    profs = scraper.get_fn_professors()

    text = (
        "👨‍🏫 <b>Docenti e Insegnamenti del Canale F-N (L-31 Informatica):</b>\n\n"
        "Gli avvisi pubblicati da questi docenti vengono monitorati automaticamente:\n\n"
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
        "💡 <i>La lista viene aggiornata periodicamente in base alla pagina ufficiale:</i>\n"
        "🔗 <a href=\"https://web.dmi.unict.it/corsi/l-31/docenti\">Docenti CdL Informatica L-31</a>"
    )

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_keyboard(),
        disable_web_page_preview=True
    )


async def impostazioni_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /impostazioni command."""
    chat_id = update.effective_chat.id
    user_data = database.get_user(chat_id, config.DB_PATH)
    include_cds = bool(user_data.get("include_cds", 0)) if user_data else False

    cds_desc = "Attiva (ricevi anche gli avvisi generali del CdS L-31)" if include_cds else "Disattivata (solo avvisi inerenti a docenti e canale F-N)"

    text = (
        "⚙️ <b>Impostazioni Notifiche:</b>\n\n"
        "🟢 <b>Avvisi Docenti Canale F-N:</b> SEMPRE ATTIVI\n"
        f"🔵 <b>Avvisi Generali CdS L-31:</b> {cds_desc}\n\n"
        "Premi il pulsante qui sotto per attivare o disattivare la ricezione degli avvisi generali del Corso di Studi (es. orari, appelli riservati, test d'ingresso):"
    )

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_settings_keyboard(include_cds)
    )


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /check command. Forces an immediate check for new notices."""
    msg = await update.message.reply_text("🔄 Controllo manuale avvisi in corso...")
    count = await notifier.check_and_notify(context.application)
    if count == 0:
        await msg.edit_text("✅ Controllo completato! Nessun nuovo avviso da notificare.")
    else:
        await msg.edit_text(f"✅ Controllo completato! Trovati e inviati {count} nuovi avvisi.")


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /stop command. Unsubscribes user from automatic alerts."""
    chat_id = update.effective_chat.id
    database.set_user_active(chat_id, False, config.DB_PATH)

    await update.message.reply_text(
        "🛑 <b>Hai disattivato le notifiche automatiche.</b>\n\n"
        "Non riceverai più messaggi per i nuovi avvisi.\n"
        "Per riattivare il servizio in qualunque momento, invia semplicemente <code>/start</code>.",
        parse_mode=ParseMode.HTML
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /help command."""
    help_text = (
        "ℹ️ <b>Guida ai comandi del Bot Avvisi DMI (Canale F-N):</b>\n\n"
        "• <code>/start</code> - Avvia o riattiva il bot e mostra le opzioni principali\n"
        "• <code>/avvisi</code> - Visualizza gli ultimi 5 avvisi rilevati per il Canale F-N\n"
        "• <code>/docenti</code> - Mostra la lista dei docenti e corsi del Canale F-N\n"
        "• <code>/impostazioni</code> - Gestisci le preferenze di notifica (es. avvisi generali CdS)\n"
        "• <code>/check</code> - Forza un controllo immediato di nuovi avvisi sul sito\n"
        "• <code>/stop</code> - Disattiva la ricezione delle notifiche automatiche\n"
        "• <code>/help</code> - Mostra questo messaggio di aiuto\n\n"
        "🔍 <b>Come funziona il monitoraggio:</b>\n"
        "Il bot controlla periodicamente (ogni 10 minuti) la sezione avvisi del sito ufficiale DMI UniCT. "
        "Quando un professore del Canale F-N pubblica un nuovo avviso, o quando viene pubblicato un avviso "
        "con riferimento al Canale F-N, il bot te lo invia all'istante qui in privato!\n\n"
        "Sito web di riferimento: <a href=\"https://web.dmi.unict.it/corsi/l-31\">DMI UniCT L-31</a>"
    )

    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_keyboard(),
        disable_web_page_preview=True
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles inline button clicks."""
    query = update.callback_query
    await query.answer()

    data = query.data
    chat_id = update.effective_chat.id

    if data == "btn_avvisi":
        # Call avvisi logic
        user_data = database.get_user(chat_id, config.DB_PATH)
        include_cds = bool(user_data.get("include_cds", 0)) if user_data else False
        notices = scraper.fetch_all_fn_notices(max_pages=3, include_cds_general=include_cds)

        if not notices:
            await query.message.reply_text("📭 Al momento non ci sono avvisi recenti per il Canale F-N.")
            return

        await query.message.reply_text(
            f"📢 <b>Trovati {len(notices[:5])} avvisi recenti per il Canale F-N:</b>",
            parse_mode=ParseMode.HTML
        )
        for n in notices[:5]:
            msg = notifier.format_notice_message(n, is_alert=False)
            await query.message.reply_text(
                msg,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )

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

        await query.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )

    elif data == "btn_settings":
        user_data = database.get_user(chat_id, config.DB_PATH)
        include_cds = bool(user_data.get("include_cds", 0)) if user_data else False
        cds_desc = "Attiva (ricevi anche gli avvisi generali del CdS L-31)" if include_cds else "Disattivata (solo avvisi inerenti a docenti e canale F-N)"
        text = (
            "⚙️ <b>Impostazioni Notifiche:</b>\n\n"
            "🟢 <b>Avvisi Docenti Canale F-N:</b> SEMPRE ATTIVI\n"
            f"🔵 <b>Avvisi Generali CdS L-31:</b> {cds_desc}\n\n"
            "Premi il pulsante per attivare/disattivare gli avvisi generali del Corso di Studi:"
        )
        await query.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_settings_keyboard(include_cds)
        )

    elif data == "toggle_cds":
        new_state = database.toggle_user_cds(chat_id, config.DB_PATH)
        cds_desc = "Attiva (ricevi anche gli avvisi generali del CdS L-31)" if new_state else "Disattivata (solo avvisi inerenti a docenti e canale F-N)"
        text = (
            "⚙️ <b>Impostazioni Aggiornate!</b>\n\n"
            "🟢 <b>Avvisi Docenti Canale F-N:</b> SEMPRE ATTIVI\n"
            f"🔵 <b>Avvisi Generali CdS L-31:</b> {cds_desc}\n\n"
            "Premi il pulsante per cambiare impostazione:"
        )
        await query.message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_settings_keyboard(new_state)
        )

    elif data == "btn_menu":
        await query.message.edit_text(
            "📋 <b>Menu Principale Bot Avvisi DMI (Canale F-N):</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_keyboard()
        )

    elif data == "btn_help":
        await help_command(update, context)


def main() -> None:
    """Initializes and runs the bot."""
    if not config.BOT_TOKEN or config.BOT_TOKEN == "IL_TUO_TOKEN_TELEGRAM_QUI":
        print("\n" + "=" * 65)
        print("❌ ERRORE: TELEGRAM_BOT_TOKEN non configurato!")
        print("Apri il file '.env' e inserisci il token ottenuto da @BotFather.")
        print("Esempio: TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
        print("=" * 65 + "\n")
        return

    # Initialize SQLite database
    database.init_db(config.DB_PATH)

    # Seed initial existing notices so they don't trigger mass alerts upon initial launch
    logger.info("Verifica seed avvisi storici iniziali...")
    try:
        initial_notices = scraper.fetch_all_fn_notices(max_pages=2, include_cds_general=True)
        seeded = database.seed_initial_notices(initial_notices, config.DB_PATH)
        logger.info(f"Seed completato: {seeded} avvisi registrati nel database.")
    except Exception as e:
        logger.error(f"Errore durante il seed iniziale degli avvisi: {e}")

    # Build PTB Application
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("avvisi", avvisi_command))
    app.add_handler(CommandHandler("docenti", docenti_command))
    app.add_handler(CommandHandler("impostazioni", impostazioni_command))
    app.add_handler(CommandHandler("check", check_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Add periodic background checking job
    if app.job_queue:
        logger.info(f"Configuro JobQueue: controllo ogni {config.CHECK_INTERVAL_SECONDS} secondi.")
        app.job_queue.run_repeating(
            notifier.check_and_notify_job,
            interval=config.CHECK_INTERVAL_SECONDS,
            first=30  # first check 30 seconds after startup
        )
    else:
        logger.warning("JobQueue non disponibile! Le notifiche automatiche periodiche non partiranno.")

    logger.info("Bot DMI(F-N) avviato con successo. In attesa di messaggi...")
    app.run_polling()


if __name__ == "__main__":
    main()
