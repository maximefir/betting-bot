"""
db.py
-----
Gestion complète de la base SQLite :
- Logs
- Boosts
- Tasks
- Bets
- Balances
- Withdrawals
"""

import sqlite3
from datetime import datetime
from config import DB_PATH
import os

# Détecte si on est en mode test
TEST_MODE = os.environ.get("TEST_MODE", "0") == "1"

# Connexion persistante unique en mode test
_test_conn = None


# -----------------------------
# Connexion & initialisation
# -----------------------------

def get_conn():
    """Retourne une connexion SQLite persistante en test, sinon classique."""
    global _test_conn
    if TEST_MODE:
        if _test_conn is None:
            _test_conn = sqlite3.connect(":memory:", check_same_thread=False)
        return _test_conn
    return sqlite3.connect(DB_PATH)


def init_db():
    """Crée toutes les tables si elles n'existent pas encore."""
    conn = get_conn()
    c = conn.cursor()

    # Logs
    c.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        level TEXT,
        message TEXT
    )""")

    # Boosts (⚡ ajout de "name")
    c.execute("""
    CREATE TABLE IF NOT EXISTS boosts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        boost_id TEXT UNIQUE,
        name TEXT,
        multiplier REAL,
        max_bet REAL,
        start_time TEXT,
        end_time TEXT,
        created_at TEXT
    )""")

    # Tasks
    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        boost_id TEXT,
        status TEXT,
        scheduled_time TEXT,
        started_at TEXT,
        finished_at TEXT,
        error_message TEXT,
        retry_count INTEGER DEFAULT 0
    )""")

    # Bets
    c.execute("""
    CREATE TABLE IF NOT EXISTS bets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        boost_id TEXT,
        amount REAL,
        result TEXT,
        gain REAL,
        timestamp TEXT
    )""")

    # Balances
    c.execute("""
    CREATE TABLE IF NOT EXISTS balances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        balance REAL,
        timestamp TEXT
    )""")

    # Withdrawals (historique des retraits)
    c.execute("""
    CREATE TABLE IF NOT EXISTS withdrawals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        timestamp TEXT
    )""")

    conn.commit()


# -----------------------------
# Logs
# -----------------------------

def log(level: str, message: str):
    """Ajoute un log en DB et l'affiche en console."""
    ts = datetime.now().isoformat()
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO logs (timestamp, level, message) VALUES (?, ?, ?)",
              (ts, level, message))
    conn.commit()
    # Print aussi en console
    print(f"[{level}] {ts} → {message}")


# -----------------------------
# Boosts
# -----------------------------

def add_boost(boost_id, name, multiplier, max_bet, start_time, end_time):
    """Ajoute un boost en DB avec un nom."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT OR IGNORE INTO boosts 
                 (boost_id, name, multiplier, max_bet, start_time, end_time, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (boost_id, name, multiplier, max_bet, start_time, end_time, datetime.now().isoformat()))
    conn.commit()

def get_boosts():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM boosts")
    rows = c.fetchall()
    return rows


# -----------------------------
# Tasks
# -----------------------------

def create_task(task_type, boost_id=None, scheduled_time=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO tasks (type, boost_id, status, scheduled_time)
                 VALUES (?, ?, 'pending', ?)""",
              (task_type, boost_id, scheduled_time))
    conn.commit()

def get_pending_tasks():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE status = 'pending' ORDER BY id ASC")
    rows = c.fetchall()
    return rows

def update_task_status(task_id, status, error_message=None):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()

    if status == "in_progress":
        c.execute("""UPDATE tasks SET status=?, started_at=? WHERE id=?""",
                  (status, now, task_id))
    elif status in ("done", "failed"):
        c.execute("""UPDATE tasks SET status=?, finished_at=?, error_message=? WHERE id=?""",
                  (status, now, error_message, task_id))

    conn.commit()


# -----------------------------
# Balance
# -----------------------------

def update_balance(balance: float):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO balances (balance, timestamp) VALUES (?, ?)",
              (balance, datetime.now().isoformat()))
    conn.commit()

def get_last_balance():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT balance FROM balances ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    return row[0] if row else None


# -----------------------------
# Bets
# -----------------------------

def get_last_bets(limit=5):
    """Retourne les derniers paris enregistrés."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT boost_id, amount, result, gain, timestamp
        FROM bets
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    return rows


# -----------------------------
# Withdrawals
# -----------------------------

def add_withdrawal(amount: float):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO withdrawals (amount, timestamp) VALUES (?, ?)",
              (amount, datetime.now().isoformat()))
    conn.commit()

def get_withdrawals(limit=5):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT amount, timestamp FROM withdrawals ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    return rows
