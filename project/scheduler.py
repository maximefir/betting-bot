"""
scheduler.py
------------
Planifie les paris sur la base des boosts récupérés.
Chaque boost est géré dans un thread séparé pour éviter
que l'attente bloque le reste du programme.
"""

import threading
import time
import numpy as np
from datetime import datetime, timedelta
from db import log
from betting import place_bet

def schedule_boost(boost):
    """
    Planifie un boost dans un thread séparé.
    """
    t = threading.Thread(target=_execute_boost, args=(boost,), daemon=True)
    t.start()

def _execute_boost(boost):
    """
    Fonction exécutée par chaque thread pour gérer un boost.
    Elle attend jusqu'à l'heure choisie dans la plage du boost,
    puis place le pari.
    """
    start = datetime.fromisoformat(boost["start"])
    end = datetime.fromisoformat(boost["end"])
    duration = (end - start).seconds

    # Tirage normal autour du début (distribution normale tronquée)
    mean = 0
    sigma = duration / 4
    offset = abs(int(np.random.normal(mean, sigma)))
    target_time = start + timedelta(seconds=min(offset, duration))

    log("INFO", f"Boost {boost['id']} programmé pour {target_time}")

    # Attendre jusqu'à l'heure programmée
    delay = (target_time - datetime.now()).total_seconds()
    if delay > 0:
        time.sleep(delay)

    # Quand l'heure est atteinte → placer le pari
    place_bet(boost)
