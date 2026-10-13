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

# Check interval in seconds for background periodic scraper (default: 300s = 5 minutes)
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "300"))

# Number of pages to scan on avvisi-docente (default: 2)
SCAN_MAX_PAGES = int(os.getenv("SCAN_MAX_PAGES", "2"))

# Database path
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "dmi_bot.db"))

# Optional admin chat ID for broadcasts, stats, and management
ADMIN_IDS_RAW = os.getenv("ADMIN_CHAT_ID", "848188619").strip()
ADMIN_CHAT_IDS = set()
for _part in ADMIN_IDS_RAW.split(","):
    _part = _part.strip()
    if _part.isdigit():
        ADMIN_CHAT_IDS.add(int(_part))
if not ADMIN_CHAT_IDS:
    ADMIN_CHAT_IDS.add(848188619)

ADMIN_CHAT_ID = next(iter(ADMIN_CHAT_IDS), 848188619)
