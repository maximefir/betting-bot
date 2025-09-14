"""
scheduler.py
------------
Orchestrateur des tâches.
- Récupère les tasks 'pending'
- Attends jusqu'à 'scheduled_time'
- Lance leur exécution (une seule à la fois grâce à un verrou global)
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

# Verrou global pour éviter l'exécution simultanée
task_lock = threading.Lock()


# -----------------------------
# Exécution planifiée
# -----------------------------

def _execute_task_later(task):
    """
    Attends jusqu'à scheduled_time puis exécute la tâche.
    Garantit qu'une seule tâche s'exécute à la fois.
    """
    task_id, task_type, boost_id, status, scheduled_time = task[0], task[1], task[2], task[3], task[4]

    # Gestion du délai si la tâche est planifiée dans le futur
    if scheduled_time:
        delay = (datetime.fromisoformat(scheduled_time) - datetime.now()).total_seconds()
        if delay > 0:
            log("INFO", f"Tâche {task_id} ({task_type}) planifiée dans {int(delay)} sec")
            time.sleep(delay)

    func = TASK_FUNCTIONS.get(task_type)
    if not func:
        log("ERROR", f"Tâche {task_id} : type {task_type} non reconnu")
        return

    # 🔒 Mutex global : attend si une autre tâche est en cours
    with task_lock:
        log("INFO", f"Tâche {task_id} ({task_type}) démarrée (lock acquis)")
        if boost_id:
            run_task_async(task_id, task_type, func, boost_id)
        else:
            run_task_async(task_id, task_type, func)
        log("INFO", f"Tâche {task_id} ({task_type}) terminée (lock libéré)")


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
            # Chaque tâche est lancée dans un thread,
            # mais le verrou global empêche l'exécution simultanée
            t = threading.Thread(target=_execute_task_later, args=(task,), daemon=True)
            t.start()
        time.sleep(interval)
