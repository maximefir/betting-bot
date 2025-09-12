"""
betting.py
----------
Gestion des paris : calcul et placement.
"""

from db import add_bet, log
from notifier import notify
from config import MIN_BET, MAX_BET

def calculate_bet_amount(boost):
    """
    Calcule la mise en fonction du multiplicateur et de la mise max.
    (Pour l’instant : 50% de la mise max, bornée par [MIN_BET, MAX_BET])
    """
    amount = boost["max_bet"] * 0.5
    return min(max(amount, MIN_BET), MAX_BET)

def place_bet(boost):
    """
    Simule le placement d’un pari (plus tard → Playwright).
    """
    try:
        amount = calculate_bet_amount(boost)
        log("INFO", f"Pari sur {boost['id']} avec {amount}€ (x{boost['multiplier']})")
        add_bet(boost_id=boost["id"], amount=amount, result="pending", gain=0.0)
        notify(f"✅ Pari placé sur {boost['id']} ({amount}€, x{boost['multiplier']})")
    except Exception as e:
        log("ERROR", f"Erreur lors du placement du pari : {e}")
        notify(f"⚠️ Erreur pari {boost['id']} : {e}")
