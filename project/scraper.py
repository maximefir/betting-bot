"""
scraper.py
----------
Tâche de scraping des boosts avec Playwright + human_browser.
- Lance un navigateur "humain"
- Se connecte au site des boosts
- Récupère les données (simulation pour l’instant)
- Enregistre en DB et crée les tâches associées
"""

from datetime import datetime, timedelta
from db import add_boost, create_task, log
from notifier import notify
from human_browser import launch_browser, new_page, human_scroll, human_delay


def scrape_boosts():
    """
    Scrape les boosts.
    Pour l’instant → simulation de boosts factices.
    Plus tard → remplacer par du vrai scraping Playwright.
    """
    log("INFO", "Scraping des boosts lancé")
    notify("🔍 Scraping des boosts lancé")

    # --- Étapes communes navigateur ---
    browser, p = launch_browser()
    page = new_page(browser)

    # Aller sur la page cible (à remplacer plus tard par l’URL réelle du bookmaker)
    page.goto("https://fr.wikipedia.org/wiki/Vol_spatial_habit%C3%A9")

    # Scroll de chauffe (évite détection bot)
    human_scroll(page)
    human_delay()

    # --- Boosts fictifs pour test ---
    fake_boosts = [
        {
            "id": "B001",
            "name": "Double Chance Foot",
            "multiplier": 2.0,
            "max_bet": 20,
            "start": datetime.now().isoformat(),
            "end": (datetime.now() + timedelta(minutes=10)).isoformat()
        },
        {
            "id": "B002",
            "name": "Boost Tennis x1.5",
            "multiplier": 1.5,
            "max_bet": 50,
            "start": datetime.now().isoformat(),
            "end": (datetime.now() + timedelta(minutes=20)).isoformat()
        }
    ]

    for b in fake_boosts:
        # Enregistrer le boost
        add_boost(b["id"], b["name"], b["multiplier"], b["max_bet"], b["start"], b["end"])
        log("INFO", f"Boost {b['id']} ({b['name']}) ajouté à la DB")
        notify(f"➕ Boost détecté : {b['name']} (x{b['multiplier']}, max {b['max_bet']}€)")

        # Créer une tâche de pari associée
        create_task("bet", boost_id=b["id"], scheduled_time=b["start"])
        log("INFO", f"Tâche 'bet' créée pour boost {b['id']} ({b['name']})")
        notify(f"📝 Tâche 'bet' créée pour boost {b['name']}")

    # Fermer le navigateur (pour éviter fuite mémoire)
    browser.close()
    p.stop()

    log("INFO", "Scraping terminé")
    notify("✅ Scraping terminé")


if __name__ == "__main__":
    # Initialisation DB
    from db import init_db
    init_db()

    # Appel de la fonction principale de ce module
    scrape_boosts()