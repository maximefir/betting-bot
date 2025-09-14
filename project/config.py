"""
config.py
---------
Paramètres globaux du bot.
"""

# --- Base de données ---
DB_PATH = "bot.db"

# --- Telegram ---
TELEGRAM_TOKEN = "8329591563:AAHD3KFDCK7u3kkPqGfFzJLSVVZ-IIjhdgw"        # fournis par BotFather
TELEGRAM_CHAT_ID = "5746873259"    # ton chat perso ou groupe

# --- Paris ---
MIN_BET = 5.0             # Mise minimale (€)
MAX_BET = 50.0            # Mise maximale (€)
WITHDRAW_THRESHOLD = 500  # Retrait automatique si solde >= 500€

# --- Scraper ---
BOOSTS_URL = "https://ton-site.com/boosts"

# --- Scheduler ---
MAX_RETRIES = 3
RETRY_DELAY = 5   # secondes entre deux tentatives en cas d'échec

# --- Mode ---
DEBUG = True
