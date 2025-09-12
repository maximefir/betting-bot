"""
main.py
-------
Orchestration du bot.
- Scrape les boosts
- Planifie chaque boost dans un thread
- Lance un thread séparé pour surveiller le solde
- Watchdog surveille tout et relance si crash
"""

from db import init_db, log
from scraper import get_boosts
from scheduler import schedule_boost
from balance import start_balance_watcher
from notifier import notify
from watchdog import watchdog

def main():
    # Initialisation
    init_db()
    log("INFO", "Bot démarré")
    notify("🤖 Bot démarré")

    # Étape 1 : récupération des boosts
    boosts = get_boosts()
    if not boosts:
        log("INFO", "Aucun boost trouvé")
        notify("ℹ️ Aucun boost trouvé")
    else:
        for b in boosts:
            schedule_boost(b)  # Chaque boost a son thread

    # Étape 2 : surveillance du solde en parallèle
    start_balance_watcher(interval=600)  # Vérifie toutes les 10 min

    # Étape 3 : garder le bot vivant
    # → Ici, on boucle pour que le process principal reste actif
    try:
        while True:
            pass  # Threads font le boulot
    except KeyboardInterrupt:
        log("INFO", "Bot arrêté manuellement")
        notify("🛑 Bot arrêté manuellement")

if __name__ == "__main__":
    watchdog(main)
