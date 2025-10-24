import streamlit as st
import json
import os
import pandas as pd
import subprocess
import webbrowser
import time

st.set_page_config(page_title="Multi-Agent Healthcare Dashboard", layout="wide")
st.title("🏥 Multi-Agent Healthcare System")

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6= st.tabs([
    "Health Monitoring", 
    "Fall Detection", 
    "Reminders", 
    "Emergency Alerts", 
    "Cognitive Chatbot",
    "Emotional Wellbeing"
])

# --- Helper to load JSON safely ---
def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        return []

# --- 1️⃣ Health Monitoring Tab ---
with tab1:
    st.header("💓 Health Monitoring")
    data = load_json("data/vitals_stream.json")
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.success("Health data loaded successfully.")
    else:
        st.warning("No health data found!")

# --- 2️⃣ Fall Detection Tab ---
with tab2:
    st.header("🤕 Fall Detection")
    data = load_json("data/fall_events.json")
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.success("Fall detection data loaded successfully.")
    else:
        st.warning("No fall data found!")

# --- 3️⃣ Reminders Tab ---
with tab3:
    st.header("🕑 Reminders")
    data = load_json("data/reminders.json")
    if data and "reminders" in data:
        df = pd.DataFrame(data["reminders"])
        st.dataframe(df)
        st.success("Reminders loaded successfully.")
    else:
        st.info("No reminders available.")


# --- 4️⃣ Emergency Alerts Tab ---
with tab4:
    st.header("🚨 Emergency Alerts")
    st.write("Alerts triggered by abnormal vitals or fall events.")
    data = load_json("data/escalation.json")
    if data:
        df = pd.DataFrame(data.get("alerts", []))
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No emergency alerts yet.")
    else:
        st.info("Emergency agent not triggered yet.")

# --- 5️⃣ Cognitive Chatbot Tab ---
with tab5:
    st.header("🧠 Cognitive Chatbot & Quiz")
    st.write("Click below to start or open the chatbot.")

    if st.button("▶️ Launch Chatbot"):
        try:
            subprocess.Popen(["python", "cognitive_health_agent/cog_bot.py"])
            time.sleep(2)
            webbrowser.open_new_tab("http://127.0.0.1:5001")
            st.success("Chatbot launched successfully!")
        except Exception as e:
            st.error(f"Error launching chatbot: {e}")

# --- 6️⃣ Emotional Wellbeing Agent Tab ---
with tab6:
    st.header("🧘‍♀️ Emotional Wellbeing Agent")
    st.write("Chat with an agent that understands your emotions and gives supportive wellbeing tips.")

    if st.button("💬 Launch Wellbeing Agent"):
        try:
            subprocess.Popen(["python", "emotional_wellbeing_agent/app.py"])
            time.sleep(2)
            webbrowser.open_new_tab("http://127.0.0.1:5000")  # use whatever port your agent runs on
            st.success("Emotional Wellbeing Agent launched successfully!")
        except Exception as e:
            st.error(f"Error launching wellbeing agent: {e}")
