# Betting Bot Project 🎲

Un bot automatisé pour gérer des tâches de paris sportifs simulés, avec :
- Scraping de "boosts" (actuellement simulés, bientôt via Playwright).
- Gestion des tâches planifiées (scheduler).
- Suivi des soldes, retraits, et historique de paris.
- Notifications et commandes via Telegram.

---

## 🚀 Fonctionnalités

- **Scraping des boosts** :
  - Détection de promotions ("boosts") avec ID, nom, multiplicateur, mise max.
  - Ajout automatique en base de données.
  - Création d'une tâche de pari associée.

- **Placement des paris** :
  - Calcule automatiquement la mise (50% du max, bornée entre `MIN_BET` et `MAX_BET`).
  - Simule un pari (inséré en base avec statut `pending`).
  - Mise à jour du solde.

- **Gestion des tâches** :
  - Scheduler qui exécute périodiquement les tâches `scrape`, `bet`, etc.
  - Statuts de tâches : `pending → in_progress → done/failed`.

- **Notifications Telegram** :
  - Suivi des actions et erreurs en direct.
  - Commandes disponibles :
    - `/tasks` → Voir les tâches en attente.
    - `/logs` → Derniers logs.
    - `/balance` → Solde actuel.
    - `/withdrawals` → Derniers retraits.
    - `/scrape` → Ajouter une tâche de scraping.
    - `/lastbets` → Historique des derniers paris.
    - `/stop` → Arrêter le bot.
    - `/help` → Liste des commandes.

- **Base de données SQLite** :
  - Tables : `logs`, `boosts`, `tasks`, `bets`, `balances`, `withdrawals`.
  - Historisation des actions.

---

## 📂 Structure du projet

```
project/
│── betting.py      # Logique de placement des paris
│── config.py       # Variables de configuration (DB path, Telegram token, etc.)
│── db.py           # Gestion SQLite (logs, boosts, tasks, bets, balances, withdrawals)
│── main.py         # Point d'entrée du programme
│── notifier.py     # Bot Telegram (notifications + commandes)
│── scheduler.py    # Orchestration des tâches
│── scraper.py      # Scraping des boosts (simulation pour l'instant)
│── tasks.py        # Exécution & gestion des statuts des tâches
```

---

## ⚙️ Installation

1. **Cloner le projet** :
   ```bash
   git clone https://github.com/username/betting-bot.git
   cd betting-bot/project
   ```

2. **Créer un environnement virtuel et installer les dépendances** :
   ```bash
   python -m venv venv
   source venv/bin/activate  # ou venv\Scripts\activate sous Windows
   pip install -r requirements.txt
   ```

3. **Configurer le fichier `config.py`** :
   - Mettre le chemin de la base de données `DB_PATH`.
   - Ajouter le token et le chat ID Telegram.

4. **Initialiser la base de données** :
   ```bash
   python -c "from db import init_db; init_db()"
   ```

5. **Lancer le bot** :
   ```bash
   python main.py
   ```

---

## 🔧 Dépendances

- `python-telegram-bot`
- `sqlite3`
- (optionnel futur) `playwright`

---

## 📌 Notes

- Actuellement, les paris sont **simulés** et marqués comme `pending`.
- La partie scraping est aussi simulée, mais remplacera bientôt par du **Playwright**.
- Pour éviter les erreurs `no such column`, supprimez `bot.db` après chaque modification du schéma, ou ajoutez une migration auto dans `db.py`.

---

## 📜 Licence

Projet académique (utilisation pédagogique uniquement).
