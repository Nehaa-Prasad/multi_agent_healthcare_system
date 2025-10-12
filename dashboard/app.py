import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ----- PAGE CONFIG -----
st.set_page_config(page_title="Multi-Agent Healthcare System", layout="wide")

# ----- HEADER -----
st.title("🏥 Multi-Agent Healthcare Dashboard")
st.markdown("A centralized view of all healthcare agents — Reminders, Emergency, and more.")

# ----- SIDEBAR -----
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Reminders", "Emergency Alerts", "Settings"])


# ----- FUNCTION: FETCH REMINDERS -----
def get_reminders_from_db():
    try:
        conn = sqlite3.connect("reminder_agent/reminder_db.sqlite")
        df = pd.read_sql_query("SELECT * FROM reminders", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error fetching reminders: {e}")
        return pd.DataFrame(columns=["id", "title", "details", "time"])


# ----- HOME PAGE -----
if page == "Home":
    st.subheader("Overview")
    st.info("This dashboard displays real-time data from multiple healthcare agents.")
    st.write("👈 Use the sidebar to navigate between agents.")

# ----- REMINDER PAGE -----
elif page == "Reminders":
    st.subheader("💊 Active Reminders")

    reminders_df = get_reminders_from_db()

    if reminders_df.empty:
        st.warning("No reminders found in the database.")
    else:
        reminders_df['time'] = pd.to_datetime(reminders_df['time'])
        reminders_df = reminders_df.sort_values(by='time')
        st.table(reminders_df[["title", "details", "time"]])

    # ---- Add New Reminder Section ----
    st.markdown("---")
    st.subheader("➕ Add a New Reminder")

    title = st.text_input("Reminder Title")
    details = st.text_input("Details")
    time = st.text_input("Time (YYYY-MM-DD HH:MM)")

    if st.button("Add Reminder"):
        try:
            conn = sqlite3.connect("reminder_agent/reminder_db.sqlite")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reminders (title, details, time) VALUES (?, ?, ?)",
                (title, details, time)
            )
            conn.commit()
            conn.close()
            st.success("✅ Reminder added successfully!")
        except Exception as e:
            st.error(f"Error adding reminder: {e}")

# ----- EMERGENCY ALERTS PAGE -----
elif page == "Emergency Alerts":
    st.subheader("🚨 Emergency Alerts")

    # Dummy data — later connect to emergency agent output
    alerts = [
        {"Type": "High BP", "Patient": "John Doe", "Time": "2025-10-11 20:40"},
        {"Type": "Low Sugar", "Patient": "Jane Doe", "Time": "2025-10-11 21:15"}
    ]
    st.write(pd.DataFrame(alerts))

# ----- SETTINGS PAGE -----
elif page == "Settings":
    st.subheader("⚙️ System Settings")
    st.write("Future features: toggle notifications, alert preferences, and more.")
