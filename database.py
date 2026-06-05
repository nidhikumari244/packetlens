"""SQLite persistence for diagnosis history."""

from __future__ import annotations

import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


PROJECT_DB_PATH = Path(__file__).resolve().with_name("network_diagnoses.db")
FALLBACK_DB_PATH = Path(tempfile.gettempdir()) / "ai_network_troubleshooting_assistant.db"
ACTIVE_DB_PATH: Optional[Path] = None


def get_connection() -> sqlite3.Connection:
    if ACTIVE_DB_PATH is not None:
        return connect(ACTIVE_DB_PATH)

    for db_path in (PROJECT_DB_PATH, FALLBACK_DB_PATH):
        try:
            conn = connect(db_path)
            return conn
        except sqlite3.OperationalError:
            if db_path == FALLBACK_DB_PATH:
                raise
    raise sqlite3.OperationalError("Could not open SQLite database.")


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=MEMORY")
    conn.execute("PRAGMA temp_store=MEMORY")
    return conn


def init_db() -> None:
    global ACTIVE_DB_PATH

    for db_path in (PROJECT_DB_PATH, FALLBACK_DB_PATH):
        try:
            with connect(db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS diagnoses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_input TEXT NOT NULL,
                        category TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        ai_diagnosis TEXT NOT NULL,
                        recommended_commands TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )
                conn.execute("SELECT COUNT(*) FROM diagnoses").fetchone()
            ACTIVE_DB_PATH = db_path
            return
        except sqlite3.OperationalError:
            if db_path == FALLBACK_DB_PATH:
                raise


def save_diagnosis(user_input: str, diagnosis: Dict[str, object]) -> int:
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO diagnoses (
                user_input, category, severity, ai_diagnosis, recommended_commands, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_input,
                str(diagnosis.get("category", "Unknown")),
                str(diagnosis.get("severity", "Low")),
                json.dumps(diagnosis, indent=2),
                json.dumps(diagnosis.get("recommended_commands", [])),
                created_at,
            ),
        )
        return int(cursor.lastrowid)


def get_diagnoses(category: Optional[str] = None, search_text: str = "") -> List[sqlite3.Row]:
    query = "SELECT * FROM diagnoses"
    params: list[str] = []
    filters: list[str] = []

    if category and category != "All":
        filters.append("category = ?")
        params.append(category)
    if search_text:
        filters.append("(user_input LIKE ? OR ai_diagnosis LIKE ?)")
        params.extend([f"%{search_text}%", f"%{search_text}%"])

    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY id DESC"

    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def get_diagnosis(issue_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM diagnoses WHERE id = ?", (issue_id,)).fetchone()


def delete_diagnosis(issue_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM diagnoses WHERE id = ?", (issue_id,))


def get_dashboard_stats() -> Dict[str, object]:
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM diagnoses").fetchone()[0]
        high = conn.execute("SELECT COUNT(*) FROM diagnoses WHERE severity = 'High'").fetchone()[0]
        by_category = conn.execute(
            "SELECT category, COUNT(*) AS count FROM diagnoses GROUP BY category ORDER BY count DESC"
        ).fetchall()
        by_severity = conn.execute(
            "SELECT severity, COUNT(*) AS count FROM diagnoses GROUP BY severity ORDER BY count DESC"
        ).fetchall()
        recent = conn.execute("SELECT * FROM diagnoses ORDER BY id DESC LIMIT 1").fetchone()
        recent_rows = conn.execute("SELECT * FROM diagnoses ORDER BY id DESC LIMIT 5").fetchall()

    return {
        "total": total,
        "high": high,
        "by_category": by_category,
        "by_severity": by_severity,
        "recent": recent,
        "recent_rows": recent_rows,
    }


def row_to_diagnosis(row: sqlite3.Row) -> Dict[str, object]:
    return json.loads(row["ai_diagnosis"])
