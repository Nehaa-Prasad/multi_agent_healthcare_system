# reminder_agent.py
import sqlite3
from datetime import datetime, timedelta

# ---- DATABASE SETUP ----
conn = sqlite3.connect("reminder_db.sqlite")
c = conn.cursor()

# Create table if not exists
c.execute('''
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        time TEXT
    )
''')
conn.commit()

# ---- FUNCTIONS ----

def add_reminder(title, description, time_str):
    """Add a reminder to the database"""
    c.execute("INSERT INTO reminders (title, description, time) VALUES (?, ?, ?)",
              (title, description, time_str))
    conn.commit()
    return f"Reminder '{title}' added at {time_str}"

def get_all_reminders():
    """Fetch all reminders"""
    c.execute("SELECT * FROM reminders")
    return c.fetchall()

def check_reminders():
    """Check for reminders that are due now (or in next minute)"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("SELECT * FROM reminders WHERE time = ?", (now,))
    due = c.fetchall()
    for r in due:
        print(f"Reminder: {r[1]} - {r[2]}")
    return due

def add_sample_reminders():
    from datetime import datetime, timedelta
    add_reminder("Take Medicine", "Paracetamol 500mg", (datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M"))
    add_reminder("Drink Water", "250ml water", (datetime.now() + timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M"))
    add_reminder("Evening Walk", "15 min walk", (datetime.now() + timedelta(minutes=3)).strftime("%Y-%m-%d %H:%M"))

if __name__ == "__main__":
    add_sample_reminders()
    print("All Reminders:", get_all_reminders())
    check_reminders()
