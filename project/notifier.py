"""
notifier.py
-----------
Gestion des notifications et commandes Telegram.
- Envoi de messages (notify)
- Réception de commandes (/tasks, /logs, /retry, /stop, etc.)
"""

import threading
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from db import get_pending_tasks, log


# -----------------------------
# Notification simple
# -----------------------------

async def _send_message_async(message: str):
    """Coroutine pour envoyer un message."""
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def notify(message: str):
    """Envoie un message synchrone (utilisé dans tout le code)."""
    try:
        asyncio.run(_send_message_async(message))
    except RuntimeError:
        # Si une boucle existe déjà → lancer dans un thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_send_message_async(message))
        loop.close()


# -----------------------------
# Commandes Telegram
# -----------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot actif. Utilise /tasks ou /logs pour consulter l'état.")

async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche les tâches en attente."""
    tasks = get_pending_tasks()
    if not tasks:
        await update.message.reply_text("✅ Aucune tâche en attente.")
    else:
        msg = "📋 Tâches pending :\n"
        for t in tasks:
            msg += f"- Task {t[0]} ({t[1]}) liée à boost {t[2]}\n"
        await update.message.reply_text(msg)

async def logs_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche les 5 derniers logs."""
    import sqlite3
    from config import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT timestamp, level, message FROM logs ORDER BY id DESC LIMIT 5")
    rows = c.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("Aucun log trouvé.")
    else:
        msg = "📝 Derniers logs :\n"
        for ts, lvl, m in rows:
            msg += f"[{lvl}] {ts} → {m}\n"
        await update.message.reply_text(msg)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Arrête le bot (manuel)."""
    await update.message.reply_text("🛑 Arrêt manuel demandé.")
    log("INFO", "Bot arrêté par commande /stop")
    import os, signal
    os.kill(os.getpid(), signal.SIGINT)


# -----------------------------
# Lancement du bot Telegram
# -----------------------------

def start_telegram_bot():
    """Démarre le bot Telegram dans un thread séparé."""
    async def runner():
        app = Application.builder().token(TELEGRAM_TOKEN).build()

        # Commandes disponibles
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("tasks", tasks))
        app.add_handler(CommandHandler("logs", logs_cmd))
        app.add_handler(CommandHandler("stop", stop))

        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        await asyncio.Event().wait()  # boucle infinie

    def run_loop():
        asyncio.run(runner())

    t = threading.Thread(target=run_loop, daemon=True)
    t.start()
