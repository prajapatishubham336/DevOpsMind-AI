import sqlite3
from app.config import DATABASE_PATH


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS monitored_apps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id INTEGER,
                log_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(app_id) REFERENCES monitored_apps(id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS health_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id INTEGER NOT NULL,
                status_code INTEGER,
                response_time REAL,
                status TEXT NOT NULL,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(app_id) REFERENCES monitored_apps(id)
            )
        """)


def add_app(name, url):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO monitored_apps (name, url) VALUES (?, ?)",
            (name, url)
        )
        return cursor.lastrowid


def get_apps():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM monitored_apps ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_app(app_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM monitored_apps WHERE id = ?",
            (app_id,)
        ).fetchone()
        return dict(row) if row else None


def save_log(app_id, log_text):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO monitoring_logs (app_id, log_text) VALUES (?, ?)",
            (app_id, log_text)
        )


def save_health_check(app_id, status_code, response_time, status):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO health_checks
            (app_id, status_code, response_time, status)
            VALUES (?, ?, ?, ?)
        """, (app_id, status_code, response_time, status))


def get_recent_checks(app_id, limit=10):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM health_checks
            WHERE app_id = ?
            ORDER BY id DESC LIMIT ?
        """, (app_id, limit)).fetchall()
        return [dict(row) for row in rows]