import streamlit as st
import json
import os
import pandas as pd
import subprocess
import webbrowser
import time
from pathlib import Path

# -------------------------------------
# GLOBAL SETTINGS
# -------------------------------------

st.set_page_config(
    page_title="Multi-Agent Healthcare Dashboard",
    layout="wide"
)

PYTHON = "python3"   # macOS uses python3

# -------------------------------------
# DATA LOCATION (CHANGED)
# -------------------------------------

BASE_DATA_DIR = Path("fall_detection_agent/data")

FALL_EVENTS_PATH = BASE_DATA_DIR / "fall_events.json"
VITALS_PATH = BASE_DATA_DIR / "vitals_stream.json"
REMINDERS_PATH = BASE_DATA_DIR / "reminders.json"
ESCALATION_PATH = BASE_DATA_DIR / "escalation.json"

# -------------------------------------
# FORCE GOOGLE CHROME (macOS)
# -------------------------------------
def open_in_chrome(url):
    try:
        chrome_cmd = "open -a 'Google Chrome' %s"
        webbrowser.get(chrome_cmd).open(url)
    except Exception:
        webbrowser.open(url)

# -------------------------------------
# SAFE JSON LOADER
# -------------------------------------
def load_json(filepath):
    try:
        if not filepath.exists():
            return []
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception:
        return []

# -------------------------------------
# FALL EVENT LOADER (JSON / NDJSON SAFE)
# -------------------------------------
def load_fall_events():
    if not FALL_EVENTS_PATH.exists():
        return []

    try:
        raw = FALL_EVENTS_PATH.read_text().strip()
        if not raw:
            return []
        return json.loads(raw)

    except json.JSONDecodeError:
        events = []
        with open(FALL_EVENTS_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except:
                    continue
        return events
    except:
        return []

# -------------------------------------
# SAFE PROCESS RUNNER
# -------------------------------------
def safe_run(relative_path):
    full_path = str(Path(relative_path).resolve())
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {full_path}")
    return subprocess.Popen([PYTHON, full_path])

# -------------------------------------
# DASHBOARD UI
# -------------------------------------

st.title("🏥 Multi-Agent Healthcare System")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Health Monitoring",
    "Fall Detection",
    "Reminders",
    "Emergency Alerts",
    "Cognitive Chatbot",
    "Emotional Wellbeing"
])

# -------------------------------------
# 1️⃣ HEALTH MONITORING
# -------------------------------------
with tab1:
    st.header("💓 Health Monitoring")

    vitals = load_json(VITALS_PATH)
    if vitals:
        df = pd.DataFrame(vitals)
        st.dataframe(df, use_container_width=True)
        st.success("Health data loaded successfully.")
    else:
        st.warning("No health data found.")

# -------------------------------------
# 2️⃣ FALL DETECTION
# -------------------------------------
with tab2:
    st.header("🤕 Fall Detection")

    fall_events = load_fall_events()
    if fall_events:
        df = pd.DataFrame(fall_events)
        st.dataframe(df, use_container_width=True)
        st.success("Fall detection data loaded successfully.")
    else:
        st.warning("No fall data found.")

# -------------------------------------
# 3️⃣ REMINDERS
# -------------------------------------
with tab3:
    st.header("🕑 Reminders")

    reminders_data = load_json(REMINDERS_PATH)
    if isinstance(reminders_data, dict) and "reminders" in reminders_data:
        df = pd.DataFrame(reminders_data["reminders"])
        st.dataframe(df, use_container_width=True)
        st.success("Reminders loaded successfully.")
    else:
        st.info("No reminders available.")

# -------------------------------------
# 4️⃣ EMERGENCY ALERTS
# -------------------------------------
with tab4:
    st.header("🚨 Emergency Alerts")

    escalation_data = load_json(ESCALATION_PATH)
    alerts = escalation_data if isinstance(escalation_data, list) else []

    if alerts:
        df = pd.DataFrame(alerts)
        df = df.iloc[::-1]
        st.dataframe(df, use_container_width=True)
        st.success("Emergency alerts loaded successfully.")
    else:
        st.info("No emergency alerts yet.")

# -------------------------------------
# 5️⃣ COGNITIVE CHATBOT
# -------------------------------------
with tab5:
    st.header("🧠 Cognitive Chatbot & Quiz")

    if st.button("▶️ Launch Chatbot"):
        try:
            safe_run("cognitive_health_agent/cog_bot.py")
            time.sleep(1)
            open_in_chrome("http://127.0.0.1:5001")
            st.success("Chatbot launched in Google Chrome!")
        except Exception as e:
            st.error(f"Error launching chatbot: {e}")

# -------------------------------------
# 6️⃣ EMOTIONAL WELLBEING AGENT
# -------------------------------------
with tab6:
    st.header("🧘‍♀️ Emotional Wellbeing Agent")

    if st.button("💬 Launch Wellbeing Agent"):
        try:
            safe_run("emotional_wellbeing_agent/app.py")
            time.sleep(2)
            open_in_chrome("http://127.0.0.1:5000")
            st.success("Wellbeing Agent launched in Google Chrome!")
        except Exception as e:
            st.error(f"Error launching wellbeing agent: {e}")
