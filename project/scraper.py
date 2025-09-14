"""
scraper.py
----------
Tâche de scraping des boosts.
Pour l’instant → simulation (boosts factices).
Plus tard, on remplacera par du vrai scraping Playwright.
"""

from datetime import datetime, timedelta
from db import add_boost, create_task, log
from notifier import notify


def scrape_boosts():
    """
    Simule la récupération des boosts.
    - Enregistre chaque boost en DB
    - Crée une tâche "bet" associée
    """
    log("INFO", "Scraping des boosts lancé (simulation)")
    notify("🔍 Scraping des boosts lancé (simulation)")

    # --- Boosts fictifs ---
    fake_boosts = [
        {
            "id": "B001",
            "multiplier": 2.0,
            "max_bet": 20,
            "start": datetime.now().isoformat(),
            "end": (datetime.now() + timedelta(minutes=10)).isoformat()
        },
        {
            "id": "B002",
            "multiplier": 1.5,
            "max_bet": 50,
            "start": datetime.now().isoformat(),
            "end": (datetime.now() + timedelta(minutes=20)).isoformat()
        }
    ]

    for b in fake_boosts:
        # Enregistrer le boost
        add_boost(b["id"], b["multiplier"], b["max_bet"], b["start"], b["end"])
        log("INFO", f"Boost {b['id']} ajouté à la DB")
        notify(f"➕ Boost détecté : {b['id']} (x{b['multiplier']}, max {b['max_bet']}€)")

        # Créer une tâche de pari associée
        create_task("bet", boost_id=b["id"], scheduled_time=b["start"])
        log("INFO", f"Tâche 'bet' créée pour boost {b['id']}")
        notify(f"📝 Tâche 'bet' créée pour boost {b['id']}")

    log("INFO", "Scraping terminé (simulation)")
    notify("✅ Scraping terminé (simulation)")
