import os, sys
import pytest
from db import (
    init_db, get_conn,
    log, add_boost, get_boosts,
    create_task, get_pending_tasks, update_task_status,
    update_balance, get_last_balance
)


sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# Active TEST_MODE pour utiliser une DB en mémoire
os.environ["TEST_MODE"] = "1"


@pytest.fixture(autouse=True)
def setup_db():
    """Réinitialise une DB en mémoire avant chaque test."""
    conn = get_conn()
    c = conn.cursor()
    # Drop tables si elles existent
    c.execute("DROP TABLE IF EXISTS logs")
    c.execute("DROP TABLE IF EXISTS boosts")
    c.execute("DROP TABLE IF EXISTS tasks")
    c.execute("DROP TABLE IF EXISTS balances")
    conn.commit()
    # Recrée les tables
    init_db()
    yield
    # Pas besoin de fermer : c'est en mémoire


# -----------------------------
# Tests Logs
# -----------------------------

def test_log_insertion_and_retrieval():
    log("INFO", "Test message")
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT level, message FROM logs ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    assert row is not None
    assert row[0] == "INFO"
    assert row[1] == "Test message"


# -----------------------------
# Tests Boosts
# -----------------------------

def test_add_and_get_boost():
    add_boost("B001", 2.0, 50, "2025-09-14T10:00:00", "2025-09-14T12:00:00")
    boosts = get_boosts()
    assert len(boosts) == 1
    b = boosts[0]
    assert b[1] == "B001"
    assert b[2] == 2.0
    assert b[3] == 50


# -----------------------------
# Tests Tasks
# -----------------------------

def test_create_and_get_task():
    create_task("scrape", boost_id="B001", scheduled_time="2025-09-14T11:00:00")
    tasks = get_pending_tasks()
    assert len(tasks) == 1
    t = tasks[0]
    assert t[1] == "scrape"
    assert t[2] == "B001"
    assert t[3] == "pending"

def test_update_task_status_in_progress_and_done():
    create_task("scrape", boost_id="B001")
    tasks = get_pending_tasks()
    task_id = tasks[0][0]

    update_task_status(task_id, "in_progress")
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT status, started_at FROM tasks WHERE id=?", (task_id,))
    row = c.fetchone()
    assert row[0] == "in_progress"
    assert row[1] is not None

    update_task_status(task_id, "done")
    c.execute("SELECT status, finished_at FROM tasks WHERE id=?", (task_id,))
    row = c.fetchone()
    assert row[0] == "done"
    assert row[1] is not None

def test_update_task_status_failed():
    create_task("scrape", boost_id="B002")
    tasks = get_pending_tasks()
    task_id = tasks[0][0]

    update_task_status(task_id, "failed", error_message="Boom")
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT status, error_message FROM tasks WHERE id=?", (task_id,))
    row = c.fetchone()
    assert row[0] == "failed"
    assert row[1] == "Boom"


# -----------------------------
# Tests Balances
# -----------------------------

def test_update_and_get_balance():
    update_balance(1000.0)
    last = get_last_balance()
    assert last == 1000.0

    update_balance(950.0)
    last = get_last_balance()
    assert last == 950.0
