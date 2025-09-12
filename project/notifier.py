"""
notifier.py
-----------
Gestion des notifications Telegram (version synchrone avec telepot).
"""

import telepot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

bot = telepot.Bot(TELEGRAM_TOKEN)

def notify(message: str):
    """
    Envoie un message Telegram de façon synchrone.
    """
    try:
        bot.sendMessage(TELEGRAM_CHAT_ID, message)
    except Exception as e:
        print(f"[ERREUR] Impossible d'envoyer le message Telegram : {e}")
