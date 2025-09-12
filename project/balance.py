"""
balance.py
----------
Gère le solde et les retraits automatiques.
Un thread indépendant vérifie régulièrement si le solde
dépasse un seuil et déclenche un retrait si nécessaire.
"""

import threading
import time
from db import update_balance, log
from notifier import notify
from config import WITHDRAW_THRESHOLD

def refresh_balance():
    """
    Récupère le solde actuel (simulation).
    En vrai → scraper ou appeler API.
    """
    # Exemple : valeur fixe pour l’instant
    balance = 600
    update_balance(balance)
    return balance

def check_withdraw():
    """
    Vérifie si on doit retirer l’argent (bloquant).
    Appelé périodiquement par un thread dédié.
    """
    balance = refresh_balance()
    if balance >= WITHDRAW_THRESHOLD:
        log("INFO", f"Seuil atteint ({balance}€) → retrait lancé")
        notify(f"💸 Retrait automatique lancé ({balance}€)")
        perform_withdraw(balance)

def perform_withdraw(amount):
    """
    Effectue un retrait (simulation).
    """
    log("INFO", f"Retrait de {amount}€ effectué")
    notify(f"✅ Retrait de {amount}€ effectué")

def start_balance_watcher(interval=600):
    """
    Lance un thread qui vérifie le solde toutes les `interval` secondes.
    """
    def watcher():
        while True:
            check_withdraw()
            time.sleep(interval)

    t = threading.Thread(target=watcher, daemon=True)
    t.start()
