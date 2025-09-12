"""
db.py
-----
Gestion de la base SQLite.
"""

import sqlite3
from datetime import datetime
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Logs
    c.execute("""CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    level TEXT,
                    message TEXT)""")

    # Boosts
    c.execute("""CREATE TABLE IF NOT EXISTS boosts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    boost_id TEXT,
                    multiplier REAL,
                    max_bet REAL,
                    start_time TEXT,
                    end_time TEXT,
                    status TEXT)""")  # pending, scheduled, done, failed

    # Bets
    c.execute("""CREATE TABLE IF NOT EXISTS bets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    boost_id TEXT,
                    amount REAL,
                    result TEXT,
                    gain REAL,
                    timestamp TEXT)""")

    # Solde
    c.execute("""CREATE TABLE IF NOT EXISTS balances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    balance REAL,
                    timestamp TEXT)""")

    conn.commit()
    conn.close()


# Logs
def log(level: str, message: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO logs (timestamp, level, message) VALUES (?, ?, ?)",
              (datetime.now().isoformat(), level, message))
    conn.commit()
    conn.close()


# Boosts
def add_boost(boost_id, multiplier, max_bet, start_time, end_time):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO boosts (boost_id, multiplier, max_bet, start_time, end_time, status)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (boost_id, multiplier, max_bet, start_time, end_time, "pending"))
    conn.commit()
    conn.close()


# Bets ✅ (manquant avant)
def add_bet(boost_id: str, amount: float, result: str = "pending", gain: float = 0.0):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO bets (boost_id, amount, result, gain, timestamp)
                 VALUES (?, ?, ?, ?, ?)""",
              (boost_id, amount, result, gain, datetime.now().isoformat()))
    conn.commit()
    conn.close()


# Balance
def update_balance(balance: float):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO balances (balance, timestamp) VALUES (?, ?)",
              (balance, datetime.now().isoformat()))
    conn.commit()
    conn.close()
