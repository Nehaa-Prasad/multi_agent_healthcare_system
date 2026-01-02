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

st.set_page_config(page_title="Multi-Agent Healthcare Dashboard", layout="wide")

DATA_PATH = Path("data/fall_events.json")
PYTHON = "python3"   # macOS uses python3


# -------------------------------------
# SAFE JSON LOADER
# -------------------------------------
def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except:
        return []


# -------------------------------------
# FALL EVENT LOADER (NDJSON SAFE)
# -------------------------------------
def load_events():
    if not DATA_PATH.exists():
        return []

    try:
        raw = DATA_PATH.read_text().strip()
        if not raw:
            return []

        return json.loads(raw)

    except json.JSONDecodeError:
        # Try NDJSON fallback
        items = []
        with open(DATA_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except:
                    continue
        return items
    except:
        return []


# -------------------------------------
# SAFE PROCESS RUNNER
# -------------------------------------
def safe_run(relative_path):
    """
    Launch python scripts safely with absolute paths.
    This prevents macOS + VS Code path errors.
    """
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

    data = load_json("data/vitals_stream.json")
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.success("Health data loaded successfully.")
    else:
        st.warning("No health data found.")


# -------------------------------------
# 2️⃣ FALL DETECTION
# -------------------------------------
with tab2:
    st.header("🤕 Fall Detection")

    data = load_events()
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.success("Fall detection data loaded successfully.")
    else:
        st.warning("No fall data found.")


# -------------------------------------
# 3️⃣ REMINDERS
# -------------------------------------
with tab3:
    st.header("🕑 Reminders")

    data = load_json("data/reminders.json")
    if data and "reminders" in data:
        df = pd.DataFrame(data["reminders"])
        st.dataframe(df)
        st.success("Reminders loaded successfully.")
    else:
        st.info("No reminders available.")


# -------------------------------------
# 4️⃣ EMERGENCY ALERTS
# -------------------------------------
with tab4:
    st.header("🚨 Emergency Alerts")

    data = load_json("data/escalation.json")
    alerts = data.get("alerts", []) if data else []

    if alerts:
        df = pd.DataFrame(alerts)
        st.dataframe(df)
    else:
        st.info("No emergency alerts yet.")


# -------------------------------------
# 5️⃣ COGNITIVE CHATBOT TAB — FIXED
# -------------------------------------
with tab5:
    st.header("🧠 Cognitive Chatbot & Quiz")
    st.write("Click below to start or open the chatbot.")

    if st.button("▶️ Launch Chatbot"):
        try:
            safe_run("cognitive_health_agent/cog_bot.py")
            time.sleep(1)
            webbrowser.open_new_tab("http://127.0.0.1:5001")
            st.success("Chatbot launched in a new terminal!")
        except Exception as e:
            st.error(f"Error launching chatbot: {e}")


# -------------------------------------
# 6️⃣ WELLBEING AGENT TAB — FIXED
# -------------------------------------
with tab6:
    st.header("🧘‍♀️ Emotional Wellbeing Agent")
    st.write("Chat with an emotional health support agent.")

    if st.button("💬 Launch Wellbeing Agent"):
        try:
            safe_run("emotional_wellbeing_agent/app.py")
            time.sleep(2)
            webbrowser.open_new_tab("http://127.0.0.1:5000")
            st.success("Wellbeing Agent launched successfully!")
        except Exception as e:
            st.error(f"Error launching wellbeing agent: {e}")
