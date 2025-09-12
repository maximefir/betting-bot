"""
config.py
---------
Paramètres globaux du bot.
"""

# --- Telegram ---
TELEGRAM_TOKEN = "8329591563:AAHD3KFDCK7u3kkPqGfFzJLSVVZ-IIjhdgw"
TELEGRAM_CHAT_ID = "5746873259"

# --- Base de données ---
DB_PATH = "bot.db"

# --- Scraper ---
BOOSTS_URL = "https://ton-site.com/boosts"

# --- Paris ---
MIN_BET = 5.0             # Mise minimale (€)
MAX_BET = 50.0            # Mise maximale (€)
WITHDRAW_THRESHOLD = 500  # Retrait auto si solde >= 500€

# --- Playwright ---
CHROME_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"
USER_DATA_DIR = "C:/Users/TonProfil/AppData/Local/Google/Chrome/User Data"

# --- Watchdog ---
MAX_RETRIES = 3
RETRY_DELAY = 5

# --- Mode ---
DEBUG = True
