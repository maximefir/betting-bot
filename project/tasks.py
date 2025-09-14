"""
tasks.py
--------
Gestion des tâches (scraping, paris, retraits…).
Chaque tâche est persistée en DB avec un statut.
- pending      : en attente
- in_progress  : en cours
- done         : terminée avec succès
- failed       : échouée (erreur HTML, réseau, etc.)
"""

import time
import traceback
import threading
from datetime import datetime
from db import create_task, update_task_status, log
from notifier import notify
from config import MAX_RETRIES, RETRY_DELAY


# -----------------------------
# Exécuteur générique
# -----------------------------

def run_task(task_id, task_type, func, *args, **kwargs):
    """
    Exécute une tâche donnée :
    - Passe en 'in_progress'
    - Lance la fonction associée
    - Met à jour le statut (done/failed)
    """

    # Marquer la tâche comme en cours
    update_task_status(task_id, "in_progress")
    log("INFO", f"Tâche {task_id} ({task_type}) démarrée")
    notify(f"▶️ Tâche {task_id} ({task_type}) démarrée")

    try:
        func(*args, **kwargs)  # Exécution réelle
        update_task_status(task_id, "done")
        log("INFO", f"Tâche {task_id} ({task_type}) terminée avec succès")
        notify(f"✅ Tâche {task_id} ({task_type}) terminée")
    except Exception as e:
        err = "".join(traceback.format_exception_only(type(e), e)).strip()
        update_task_status(task_id, "failed", error_message=err)
        log("ERROR", f"Tâche {task_id} ({task_type}) échouée : {err}")
        notify(f"❌ Tâche {task_id} ({task_type}) échouée : {err}")


# -----------------------------
# Gestion des retries
# -----------------------------

def retry_task(task_id, task_type, func, *args, **kwargs):
    """
    Retente une tâche plusieurs fois si elle échoue.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            run_task(task_id, task_type, func, *args, **kwargs)
            return  # succès → on sort
        except Exception as e:
            log("WARNING", f"Tâche {task_id} ({task_type}) tentative {attempt}/{MAX_RETRIES} échouée")
            time.sleep(RETRY_DELAY)
    # Si toutes les tentatives échouent, on laisse le statut 'failed'
    log("CRITICAL", f"Tâche {task_id} ({task_type}) a échoué après {MAX_RETRIES} tentatives")
    notify(f"⚠️ Tâche {task_id} ({task_type}) a échoué après {MAX_RETRIES} tentatives")


# -----------------------------
# Gestion multithread
# -----------------------------

def run_task_async(task_id, task_type, func, *args, **kwargs):
    """
    Lance une tâche dans un thread séparé.
    """
    t = threading.Thread(target=retry_task, args=(task_id, task_type, func) + args, kwargs=kwargs, daemon=True)
    t.start()
    