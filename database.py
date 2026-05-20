import sqlite3
import os
from config import DATABASE_FILE

def get_conn():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll_number TEXT,
            leetcode_username TEXT UNIQUE,
            added_at TEXT,
            active INTEGER DEFAULT 1
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS fetch_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            rating REAL,
            global_rank INTEGER,
            contests_attended INTEGER,
            top_pct REAL,
            success INTEGER,
            fetched_at TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)
    conn.commit()
    conn.close()

def add_student(name, roll_number, leetcode_username):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO students (name, roll_number, leetcode_username, added_at, active) VALUES (?, ?, ?, datetime('now'), 1)",
            (name, roll_number, leetcode_username)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def add_students_batch(students):
    new_count = 0
    dup_count = 0
    conn = get_conn()
    for s in students:
        try:
            conn.execute(
                "INSERT INTO students (name, roll_number, leetcode_username, added_at, active) VALUES (?, ?, ?, datetime('now'), 1)",
                (s["name"], s["roll_number"], s["leetcode_username"])
            )
            new_count += 1
        except sqlite3.IntegrityError:
            dup_count += 1
    conn.commit()
    conn.close()
    return new_count, dup_count

def get_active_students():
    conn = get_conn()
    rows = conn.execute("SELECT id, name, roll_number, leetcode_username FROM students WHERE active = 1 ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_students():
    conn = get_conn()
    rows = conn.execute("SELECT id, name, roll_number, leetcode_username, added_at, active FROM students ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_student(leetcode_username):
    conn = get_conn()
    cur = conn.execute("DELETE FROM students WHERE leetcode_username = ?", (leetcode_username,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted

def deactivate_student(leetcode_username):
    conn = get_conn()
    cur = conn.execute("UPDATE students SET active = 0 WHERE leetcode_username = ?", (leetcode_username,))
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated

def save_fetch_result(student_id, rating, global_rank, contests_attended, top_pct, success):
    conn = get_conn()
    conn.execute(
        "INSERT INTO fetch_history (student_id, rating, global_rank, contests_attended, top_pct, success, fetched_at) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))",
        (student_id, rating, global_rank, contests_attended, top_pct, 1 if success else 0)
    )
    conn.commit()
    conn.close()

def get_latest_results():
    conn = get_conn()
    rows = conn.execute("""
        SELECT s.name, s.roll_number, s.leetcode_username, f.rating, f.global_rank, f.contests_attended, f.top_pct, f.success, f.fetched_at
        FROM fetch_history f
        JOIN students s ON f.student_id = s.id
        WHERE f.fetched_at = (SELECT MAX(fetched_at) FROM fetch_history)
        ORDER BY f.rating DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_student_count():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    active = conn.execute("SELECT COUNT(*) FROM students WHERE active = 1").fetchone()[0]
    conn.close()
    return total, active

def get_stats():
    conn = get_conn()
    row = conn.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
            AVG(CASE WHEN success = 1 AND rating > 0 THEN rating END) as avg_rating,
            MAX(CASE WHEN success = 1 THEN rating END) as top_rating
        FROM fetch_history
        WHERE fetched_at = (SELECT MAX(fetched_at) FROM fetch_history)
    """).fetchone()
    conn.close()
    return dict(row) if row else {}

def get_last_fetch_time():
    conn = get_conn()
    row = conn.execute("SELECT MAX(fetched_at) FROM fetch_history").fetchone()
    conn.close()
    return row[0] if row and row[0] else None
