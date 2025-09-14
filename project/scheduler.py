"""
scheduler.py
------------
Orchestrateur des tâches.
- Récupère les tasks 'pending'
- Attends jusqu'à 'scheduled_time'
- Lance leur exécution en parallèle
"""

import time
import threading
from datetime import datetime
from db import get_pending_tasks, log
from tasks import run_task_async
from scraper import scrape_boosts
from betting import place_bet


# -----------------------------
# Mapping type -> fonction
# -----------------------------

TASK_FUNCTIONS = {
    "scrape": scrape_boosts,
    "bet": place_bet,
    # plus tard : "withdraw": perform_withdraw, etc.
}


# -----------------------------
# Exécution planifiée
# -----------------------------

def _execute_task_later(task):
    """
    Attends jusqu'à scheduled_time puis exécute la tâche.
    Chaque tâche est lancée dans un thread séparé.
    """
    task_id, task_type, boost_id, status, scheduled_time = task[0], task[1], task[2], task[3], task[4]

    if scheduled_time:
        delay = (datetime.fromisoformat(scheduled_time) - datetime.now()).total_seconds()
        if delay > 0:
            log("INFO", f"Tâche {task_id} ({task_type}) planifiée dans {int(delay)} sec")
            time.sleep(delay)

    # Lancer la tâche réelle
    func = TASK_FUNCTIONS.get(task_type)
    if not func:
        log("ERROR", f"Tâche {task_id} : type {task_type} non reconnu")
        return

    if boost_id:
        run_task_async(task_id, task_type, func, boost_id)
    else:
        run_task_async(task_id, task_type, func)


# -----------------------------
# Boucle principale
# -----------------------------

def scheduler_loop(interval=30):
    """
    Boucle infinie du scheduler :
    - Vérifie toutes les `interval` secondes s'il y a des tasks pending
    - Les planifie si nécessaire
    """
    log("INFO", "Scheduler démarré")

    while True:
        tasks = get_pending_tasks()
        for task in tasks:
            # Démarrer chaque tâche dans un thread séparé
            t = threading.Thread(target=_execute_task_later, args=(task,), daemon=True)
            t.start()
        time.sleep(interval)
