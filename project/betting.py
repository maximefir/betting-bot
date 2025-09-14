"""
betting.py
----------
Tâche de placement des paris.
Actuellement en mode simulation (pas de Playwright).
"""

import os
from db import get_conn, log, update_balance, get_last_balance
from notifier import notify
from config import MIN_BET, MAX_BET


# -----------------------------
# Fonctions utilitaires
# -----------------------------

def _get_boost_by_id(boost_id):
    """Récupère un boost en DB à partir de son ID."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM boosts WHERE boost_id = ?", (boost_id,))
    row = c.fetchone()
    if not os.environ.get("TEST_MODE", "0") == "1":
        conn.close()
    return row


def _calculate_bet_amount(multiplier, max_bet):
    """
    Calcule la mise à placer.
    Actuellement : 50% de la mise max, bornée entre MIN_BET et MAX_BET.
    """
    amount = max_bet * 0.5
    return min(max(amount, MIN_BET), MAX_BET)


# -----------------------------
# Tâche "bet"
# -----------------------------

def place_bet(boost_id):
    """
    Simule le placement d'un pari lié à un boost.
    """
    boost = _get_boost_by_id(boost_id)
    if not boost:
        log("ERROR", f"Boost {boost_id} introuvable en DB")
        notify(f"❌ Boost introuvable")
        return

    # boost tuple : (id, boost_id, name, multiplier, max_bet, start_time, end_time, created_at)
    boost_name = boost[2]
    multiplier = boost[3]
    max_bet = boost[4]

    # Calcul de la mise
    amount = _calculate_bet_amount(multiplier, max_bet)

    # Simulation du pari
    log("INFO", f"Pari simulé sur {boost_id} - {boost_name} : {amount}€ @ x{multiplier}")
    notify(f"🎲 Pari simulé sur {boost_name} → {amount}€ @ x{multiplier}")

    # Enregistrer dans la DB (bets)
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO bets (boost_id, amount, result, gain, timestamp)
                 VALUES (?, ?, ?, ?, datetime('now'))""",
              (boost_id, amount, "pending", 0.0))
    conn.commit()
    if not os.environ.get("TEST_MODE", "0") == "1":
        conn.close()

    # Mettre à jour le solde (simulation : -amount)
    last_balance = get_last_balance()
    if last_balance is None:
        new_balance = 1000 - amount  # solde initial fictif : 1000€
    else:
        new_balance = last_balance - amount
    update_balance(new_balance)
