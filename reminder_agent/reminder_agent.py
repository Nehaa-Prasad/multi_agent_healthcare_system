#!/usr/bin/env python3
# reminder_agent.py
"""
Reminder agent using SQLite.

Usage:
  - python3 reminder_agent.py         # add sample reminders and run one check
  - python3 reminder_agent.py loop    # run continuous checking (every 30s)
"""

import sqlite3
from datetime import datetime, timedelta
import time
import os

DB_PATH = "reminder_db.sqlite"
TIME_FORMAT = "%Y-%m-%d %H:%M"   # store times truncated to minute


class ReminderDB:
    def __init__(self, db_path=DB_PATH):
        first_create = not os.path.exists(db_path)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._ensure_table()
        if first_create:
            print(f"Created new DB at {db_path}")

    def _ensure_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    time TEXT NOT NULL
                )
            ''')

    def add_reminder(self, title: str, description: str, time_str: str) -> int:
        """Add a reminder. time_str must be in TIME_FORMAT (YYYY-MM-DD HH:MM). Returns inserted id."""
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO reminders (title, description, time) VALUES (?, ?, ?)",
                (title, description, time_str)
            )
            return cur.lastrowid

    def get_all_reminders(self):
        cur = self.conn.execute("SELECT * FROM reminders ORDER BY time ASC")
        return [dict(r) for r in cur.fetchall()]

    def get_due_at_minute(self, dt_minute: datetime):
        """Return reminders scheduled exactly at dt_minute (rounded to minute)."""
        tstr = dt_minute.strftime(TIME_FORMAT)
        cur = self.conn.execute("SELECT * FROM reminders WHERE time = ?", (tstr,))
        return [dict(r) for r in cur.fetchall()]

    def get_due_up_to(self, dt_up_to: datetime):
        """Return reminders scheduled at or before dt_up_to (inclusive). Useful to catch missed reminders."""
        tstr = dt_up_to.strftime(TIME_FORMAT)
        cur = self.conn.execute("SELECT * FROM reminders WHERE time <= ? ORDER BY time ASC", (tstr,))
        return [dict(r) for r in cur.fetchall()]

    def delete_reminder(self, reminder_id: int):
        with self.conn:
            self.conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))

    def close(self):
        try:
            self.conn.close()
        except:
            pass


# Convenience functions using the ReminderDB class
def add_reminder(db: ReminderDB, title: str, description: str, dt: datetime):
    """Helper: dt is a datetime; it will be rounded/truncated to minute."""
    tstr = dt.strftime(TIME_FORMAT)
    rid = db.add_reminder(title, description, tstr)
    print(f"Added reminder id={rid} title='{title}' at {tstr}")
    return rid

def check_reminders(db: ReminderDB):
    """
    Check reminders due now (rounded to the current minute).
    Returns list of due reminders.
    This function also returns reminders scheduled earlier (<= now), so it can catch missed ones.
    """
    now = datetime.now()
    # truncate seconds to minute
    now_minute = now.replace(second=0, microsecond=0)
    due = db.get_due_up_to(now_minute)
    if not due:
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] No reminders due (up to minute {now_minute.strftime(TIME_FORMAT)})")
        return []
    # Print them
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {len(due)} reminder(s) due (<= {now_minute.strftime(TIME_FORMAT)}):")
    for r in due:
        print(f" - id={r['id']} | {r['title']} at {r['time']}: {r.get('description','')}")
    return due

def add_sample_reminders(db: ReminderDB):
    now = datetime.now()
    add_reminder(db, "Take Medicine", "Paracetamol 500mg", now + timedelta(minutes=1))
    add_reminder(db, "Drink Water", "250ml water", now + timedelta(minutes=2))
    add_reminder(db, "Evening Walk", "15 min walk", now + timedelta(minutes=3))
    print("Sample reminders added.")


# CLI behavior
if __name__ == "__main__":
    import sys

    db = ReminderDB(DB_PATH)

    # If run with no args: add sample reminders (for quick testing), list all, and check once
    if len(sys.argv) == 1:
        print("Adding sample reminders for quick testing...")
        add_sample_reminders(db)
        print("\nAll reminders in DB:")
        for r in db.get_all_reminders():
            print(r)
        print("\nRunning one-time check for due reminders:")
        check_reminders(db)
        db.close()
        sys.exit(0)

    # If 'loop' arg passed: run continuous checking loop
    if len(sys.argv) > 1 and sys.argv[1].lower() == "loop":
        print("Starting continuous reminder checker (press Ctrl+C to stop)...")
        try:
            while True:
                check_reminders(db)
                # sleep until the start of next 30-second boundary to be responsive
                time.sleep(30)
        except KeyboardInterrupt:
            print("Stopping loop.")
        finally:
            db.close()
            sys.exit(0)

    # If add args passed: simple CLI to add a reminder
    # Usage: python3 reminder_agent.py add "Title" "Desc" "YYYY-MM-DD HH:MM"
    if len(sys.argv) >= 2 and sys.argv[1].lower() == "add":
        if len(sys.argv) < 5:
            print("Usage: python3 reminder_agent.py add \"Title\" \"Description\" \"YYYY-MM-DD HH:MM\"")
            db.close()
            sys.exit(1)
        title = sys.argv[2]
        desc = sys.argv[3]
        timestr = sys.argv[4]
        # validate timestr
        try:
            dt = datetime.strptime(timestr, TIME_FORMAT)
        except Exception as e:
            print("Time format invalid. Use YYYY-MM-DD HH:MM")
            db.close()
            sys.exit(1)
        add_reminder(db, title, desc, dt)
        db.close()
        sys.exit(0)

    # default behavior: show help
    print("Usage examples:")
    print("  python3 reminder_agent.py             # add samples + run one check")
    print("  python3 reminder_agent.py loop        # continuous checking")
    print("  python3 reminder_agent.py add \"Title\" \"Desc\" \"YYYY-MM-DD HH:MM\"")
    db.close()
