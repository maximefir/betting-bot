"""
notifier.py
-----------
Gestion des notifications et commandes Telegram.
- Envoi de messages (notify)
- Réception de commandes (/tasks, /logs, /balance, /withdrawals, /scrape, /lastbets, /stop, etc.)
"""

import threading
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from db import (
    get_pending_tasks,
    log,
    get_last_balance,
    get_withdrawals,
    create_task,
    get_conn,
    get_last_bets,   # ✅ import corrigé (vient de db.py maintenant)
)


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
    await update.message.reply_text("🤖 Bot actif. Utilisez /help pour voir les commandes disponibles.")

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

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche le solde courant."""
    bal = get_last_balance()
    if bal is None:
        await update.message.reply_text("💰 Aucun solde trouvé en DB.")
    else:
        await update.message.reply_text(f"💰 Solde actuel : {bal:.2f} €")

async def withdrawals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche l'historique des retraits."""
    rows = get_withdrawals(limit=5)
    if not rows:
        await update.message.reply_text("🏦 Aucun retrait enregistré.")
    else:
        msg = "🏦 Derniers retraits :\n"
        for amt, ts in rows:
            msg += f"- {amt:.2f} € le {ts}\n"
        await update.message.reply_text(msg)

async def scrape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ajoute une tâche 'scrape' dans la DB."""
    create_task("scrape")
    log("INFO", "Tâche 'scrape' ajoutée manuellement via Telegram")
    await update.message.reply_text("🔍 Tâche 'scrape' ajoutée et planifiée.")

async def lastbets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche les derniers paris (nom du boost uniquement)."""
    bets = get_last_bets(limit=5)
    if not bets:
        await update.message.reply_text("🎲 Aucun pari enregistré.")
    else:
        # Récupérer les noms via la DB (boost_id -> name)
        conn = get_conn()
        c = conn.cursor()
        msg = "🎲 Derniers paris :\n"
        for boost_id, amount, result, gain, ts in bets:
            c.execute("SELECT name FROM boosts WHERE boost_id = ?", (boost_id,))
            row = c.fetchone()
            name = row[0] if row else boost_id
            msg += f"- {name} : {amount:.2f} € ({result}) le {ts}\n"
        await update.message.reply_text(msg)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Arrête le bot (manuel)."""
    await update.message.reply_text("🛑 Arrêt manuel demandé.")
    log("INFO", "Bot arrêté par commande /stop")
    import os, signal
    os.kill(os.getpid(), signal.SIGINT)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche l'aide."""
    msg = (
        "🤖 Commandes disponibles :\n"
        "/tasks - Voir les tâches en attente\n"
        "/logs - Voir les derniers logs\n"
        "/balance - Voir le solde actuel\n"
        "/withdrawals - Voir l'historique des retraits\n"
        "/scrape - Ajouter une tâche de scraping\n"
        "/lastbets - Voir les derniers paris\n"
        "/stop - Arrêter le bot\n"
        "/help - Afficher cette aide"
    )
    await update.message.reply_text(msg)


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
        app.add_handler(CommandHandler("balance", balance))
        app.add_handler(CommandHandler("withdrawals", withdrawals))
        app.add_handler(CommandHandler("scrape", scrape))
        app.add_handler(CommandHandler("lastbets", lastbets))
        app.add_handler(CommandHandler("stop", stop))
        app.add_handler(CommandHandler("help", help))

        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        await asyncio.Event().wait()  # boucle infinie

    def run_loop():
        asyncio.run(runner())

    t = threading.Thread(target=run_loop, daemon=True)
    t.start()
