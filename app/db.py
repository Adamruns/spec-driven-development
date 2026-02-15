"""SQLite database operations for the Test Case Manager API."""

import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional


DB_PATH = os.environ.get("APP_DB_PATH", "test_cases.db")


def get_connection() -> sqlite3.Connection:
    """Create and return a database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the test_cases table if it does not exist."""
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                steps TEXT NOT NULL,
                expected_result TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                tags TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def _now() -> str:
    """Return the current UTC timestamp as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a sqlite3.Row to a dictionary, parsing tags back to a list."""
    d = dict(row)
    d["tags"] = json.loads(d["tags"]) if d["tags"] else []
    return d


def create_test_case(data: dict) -> dict:
    """Insert a new test case and return the created record."""
    now = _now()
    tags_str = json.dumps(data.get("tags", []))
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO test_cases (title, description, steps, expected_result, priority, status, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["title"],
                data["description"],
                data["steps"],
                data["expected_result"],
                data["priority"],
                data["status"],
                tags_str,
                now,
                now,
            ),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM test_cases WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def get_test_cases(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
) -> list[dict]:
    """Return all test cases, optionally filtered by status, priority, and/or tag."""
    query = "SELECT * FROM test_cases WHERE 1=1"
    params: list = []

    if status is not None:
        query += " AND status = ?"
        params.append(status)
    if priority is not None:
        query += " AND priority = ?"
        params.append(priority)
    if tag is not None:
        # Match tag in JSON array
        query += " AND tags LIKE ?"
        params.append(f'%"{tag}"%')

    query += " ORDER BY id"

    conn = get_connection()
    try:
        rows = conn.execute(query, params).fetchall()
        return [_row_to_dict(row) for row in rows]
    finally:
        conn.close()


def get_test_case_by_id(test_case_id: int) -> Optional[dict]:
    """Return a single test case by ID, or None if not found."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM test_cases WHERE id = ?", (test_case_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


def update_test_case(test_case_id: int, data: dict) -> Optional[dict]:
    """Update a test case by ID. Returns the updated record, or None if not found."""
    existing = get_test_case_by_id(test_case_id)
    if existing is None:
        return None

    now = _now()
    # Merge: use provided values or fall back to existing
    title = data.get("title", existing["title"])
    description = data.get("description", existing["description"])
    steps = data.get("steps", existing["steps"])
    expected_result = data.get("expected_result", existing["expected_result"])
    priority = data.get("priority", existing["priority"])
    status = data.get("status", existing["status"])
    tags = data.get("tags", existing["tags"])
    tags_str = json.dumps(tags) if isinstance(tags, list) else tags

    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE test_cases
            SET title = ?, description = ?, steps = ?, expected_result = ?,
                priority = ?, status = ?, tags = ?, updated_at = ?
            WHERE id = ?
            """,
            (title, description, steps, expected_result, priority, status, tags_str, now, test_case_id),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM test_cases WHERE id = ?", (test_case_id,)
        ).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def delete_test_case(test_case_id: int) -> bool:
    """Delete a test case by ID. Returns True if deleted, False if not found."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM test_cases WHERE id = ?", (test_case_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
