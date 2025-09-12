"""
scraper.py
----------
Récupère les boosts sur le site.
(Pour l’instant → simulation.)
"""

from db import add_boost

def get_boosts():
    """
    Retourne une liste de boosts trouvés.
    Chaque boost est un dict.
    """
    # Simulation : normalement on scrappera avec Playwright
    fake_boosts = [
        {"id": "B001", "multiplier": 2.0, "max_bet": 20, "start": "2025-09-12T18:00:00", "end": "2025-09-12T20:00:00"},
        {"id": "B002", "multiplier": 1.5, "max_bet": 30, "start": "2025-09-13T12:00:00", "end": "2025-09-13T14:00:00"},
    ]
    for b in fake_boosts:
        add_boost(b["id"], b["multiplier"], b["max_bet"], b["start"], b["end"])
    return fake_boosts
