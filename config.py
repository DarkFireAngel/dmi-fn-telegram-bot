"""
Configuration module for DMI(F-N) infobot.
Loads settings from environment variables or .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Telegram Bot Token (from @BotFather)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

# Check interval in seconds for background periodic scraper (default: 600s = 10 minutes)
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "600"))

# Number of pages to scan on avvisi-docente (default: 2)
SCAN_MAX_PAGES = int(os.getenv("SCAN_MAX_PAGES", "2"))

# Database path
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "dmi_bot.db"))

# Optional admin chat ID for error logs or notifications
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "").strip()
ADMIN_CHAT_ID = int(ADMIN_CHAT_ID) if ADMIN_CHAT_ID.isdigit() else None
