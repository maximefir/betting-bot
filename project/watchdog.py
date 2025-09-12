"""
watchdog.py
-----------
Ce fichier implémente un système de "watchdog".
Son but est de lancer la fonction principale, et si elle plante,
il essaie de la relancer un certain nombre de fois.
"""

import time
from db import log
from notifier import notify
from config import MAX_RETRIES, RETRY_DELAY

def watchdog(main_func):
    """
    Lance la fonction principale et la relance en cas d'erreur.
    """
    retries = 0
    while retries < MAX_RETRIES:
        try:
            main_func()
            break  # Si tout va bien → on sort de la boucle
        except Exception as e:
            retries += 1
            error_msg = f"Crash détecté : {e} (tentative {retries}/{MAX_RETRIES})"
            print(error_msg)
            log("ERROR", error_msg)
            notify(error_msg)
            time.sleep(RETRY_DELAY)

    if retries == MAX_RETRIES:
        final_msg = "Le bot a échoué après plusieurs tentatives."
        print(final_msg)
        log("CRITICAL", final_msg)
        notify(final_msg)
