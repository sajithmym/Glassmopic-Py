"""SQLite persistence layer for Glassmopic Todo App."""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glassmopic_todos.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            description TEXT    DEFAULT '',
            priority    TEXT    DEFAULT 'Medium' CHECK(priority IN ('Low','Medium','High','Critical')),
            category    TEXT    DEFAULT 'General',
            due_date    TEXT    DEFAULT '',
            completed   INTEGER DEFAULT 0,
            sort_order  INTEGER DEFAULT 0,
            created_at  TEXT    NOT NULL,
            updated_at  TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_todo(title: str, description: str = "", priority: str = "Medium",
             category: str = "General", due_date: str = "") -> int:
    now = datetime.now().isoformat()
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO todos (title, description, priority, category, due_date, completed, sort_order, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, 0, (SELECT COALESCE(MAX(sort_order),0)+1 FROM todos), ?, ?)",
        (title, description, priority, category, due_date, now, now)
    )
    todo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return todo_id


def update_todo(todo_id: int, **kwargs) -> None:
    allowed = {"title", "description", "priority", "category", "due_date", "completed", "sort_order"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    fields["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [todo_id]
    conn = get_connection()
    conn.execute(f"UPDATE todos SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()


def delete_todo(todo_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()


def get_all_todos(filter_status: Optional[str] = None, search: str = "",
                  category: str = "", priority: str = "") -> List[dict]:
    conn = get_connection()
    query = "SELECT * FROM todos WHERE 1=1"
    params: list = []

    if filter_status == "completed":
        query += " AND completed = 1"
    elif filter_status == "active":
        query += " AND completed = 0"

    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    if priority and priority != "All":
        query += " AND priority = ?"
        params.append(priority)

    query += " ORDER BY completed ASC, sort_order ASC, created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_categories() -> List[str]:
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT category FROM todos ORDER BY category").fetchall()
    conn.close()
    return [r["category"] for r in rows]


def get_statistics() -> dict:
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) as c FROM todos").fetchone()["c"]
    completed = conn.execute("SELECT COUNT(*) as c FROM todos WHERE completed=1").fetchone()["c"]
    conn.close()
    return {"total": total, "completed": completed, "active": total - completed}


def swap_order(id_a: int, id_b: int) -> None:
    conn = get_connection()
    row_a = conn.execute("SELECT sort_order FROM todos WHERE id=?", (id_a,)).fetchone()
    row_b = conn.execute("SELECT sort_order FROM todos WHERE id=?", (id_b,)).fetchone()
    if row_a and row_b:
        conn.execute("UPDATE todos SET sort_order=? WHERE id=?", (row_b["sort_order"], id_a))
        conn.execute("UPDATE todos SET sort_order=? WHERE id=?", (row_a["sort_order"], id_b))
        conn.commit()
    conn.close()
