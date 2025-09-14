"""
main.py
-------
Point d'entrée du bot.
- Initialise la DB
- Lance le bot Telegram
- Crée une tâche de scraping
- Démarre le scheduler (gestion des tâches en continu)
"""

from db import init_db, create_task, log
from notifier import notify, start_telegram_bot
from scheduler import scheduler_loop


def main():
    # Initialiser la DB
    init_db()
    log("INFO", "Bot démarré")
    notify("🤖 Bot démarré")

    # Démarrer le bot Telegram en arrière-plan
    start_telegram_bot()

    # Créer une tâche de scraping (au lancement)
    create_task("scrape")

    # Lancer le scheduler (boucle infinie)
    scheduler_loop(interval=10)  # vérifie toutes les 10 sec


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("INFO", "Bot arrêté manuellement")
        notify("🛑 Bot arrêté manuellement")
