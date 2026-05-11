import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List

DB_PATH = "fieldmind.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                location TEXT,
                client_name TEXT,
                issue_type TEXT,
                sentiment TEXT,
                action_needed INTEGER,
                urgency TEXT,
                summary TEXT,
                tags TEXT,
                raw_input TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_report(data: Dict[str, Any]) -> int:
    tags = data.get("tags", [])
    tags_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
    created_at = datetime.utcnow().isoformat()

    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO reports (
                agent_name, location, client_name, issue_type,
                sentiment, action_needed, urgency, summary,
                tags, raw_input, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("agent_name"),
                data.get("location"),
                data.get("client_name"),
                data.get("issue_type"),
                data.get("sentiment"),
                1 if data.get("action_needed") else 0,
                data.get("urgency"),
                data.get("summary"),
                tags_str,
                data.get("raw_input"),
                created_at,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def _rows_to_dicts(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    output = []
    for row in rows:
        row_dict = dict(row)
        row_dict["action_needed"] = bool(row_dict.get("action_needed"))
        output.append(row_dict)
    return output


def get_all_reports() -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM reports ORDER BY datetime(created_at) DESC").fetchall()
    return _rows_to_dicts(rows)


def get_reports_by_urgency(urgency: str) -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM reports WHERE urgency = ? ORDER BY datetime(created_at) DESC",
            (urgency,),
        ).fetchall()
    return _rows_to_dicts(rows)


def get_recent_reports(days: int = 7) -> List[Dict[str, Any]]:
    since = (datetime.utcnow() - timedelta(days=days)).isoformat()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM reports WHERE created_at >= ? ORDER BY datetime(created_at) DESC",
            (since,),
        ).fetchall()
    return _rows_to_dicts(rows)


def get_stats() -> Dict[str, int]:
    with _connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
        action_needed = conn.execute("SELECT COUNT(*) FROM reports WHERE action_needed = 1").fetchone()[0]
        high_urgency = conn.execute("SELECT COUNT(*) FROM reports WHERE urgency = 'high'").fetchone()[0]
        frustrated_or_angry = conn.execute(
            "SELECT COUNT(*) FROM reports WHERE sentiment IN ('frustrated', 'angry')"
        ).fetchone()[0]

    return {
        "total": int(total),
        "action_needed": int(action_needed),
        "high_urgency": int(high_urgency),
        "frustrated_or_angry": int(frustrated_or_angry),
    }
