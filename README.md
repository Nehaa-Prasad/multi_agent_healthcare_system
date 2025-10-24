# 🩺 Multi-Agent Healthcare System  

A **smart multi-agent healthcare monitoring system** designed to assist users with **health tracking, fall detection, reminders, cognitive health, and emotional wellbeing** — all integrated into an interactive **Streamlit dashboard**.

---

## 🚀 Getting Started  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/<your-username>/multi_agent_healthcare_system.git
cd multi_agent_healthcare_system
```

### 2️⃣ Create and Activate a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate   # for Windows
# or
source venv/bin/activate  # for macOS/Linux
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ⚙️ Project Structure
```
multi_agent_healthcare_system/
│
├── cognitive_health_agent
│
├── emergency_agent
│
├── emotional_wellbeing_agent
│
├── fall_detection_agent
│
├── health_monitoring_agent
│
├── reminder_agent
│
├── data/
│   ├── escalation.json
│   ├── fall_events.json
│   ├── reminders.json
│   └── vitals_stream.json
│
├── main.py
├── streamlit_dashboard.py
├── reminder_db.sqlite
├── requirements.txt
└── README.md
```

---

## 🧠 Features

### ❤️ Health Monitoring
The Health Monitoring Agent continuously tracks a user’s vital signs such as heart rate, blood pressure, oxygen level, and temperature.
It helps in:
-Logging real-time health data into vitals_stream.json.
-Detecting abnormalities in the readings and alerting other agents when something goes out of range.
-Displaying health trends and summaries on the dashboard for easy visualization and analysis.

### 🤕 Fall Detection
The Fall Detection Agent identifies potential falls or sudden drops in user movement patterns.
It:
-Monitors incoming motion or activity data.
-Detects abnormal acceleration or inactivity that indicates a fall.
-Automatically records the event in fall_events.json.
-Sends an alert to the Emergency Agent for immediate attention or notification.

### 🧩 Cognitive Health Bot
The Cognitive Health Agent (or Cognitive Bot) is an interactive chatbot that helps users with reminders, health tips, and mood-supportive responses.
It:
-Analyzes user input using simple NLP models.
-Provides daily health tips, medicine reminders, and positive reinforcement.
-Saves user interaction data for further emotion or behavior analysis.
-Acts as the “thinking” component that connects emotional, reminder, and health agents together for smooth coordination.

### 🕑 Reminders
Displays a list of health reminders such as:
-Taking medicines
-Checking blood pressure
-Drinking water
All reminder data is loaded from data/reminders.json and displayed neatly in the Streamlit dashboard.

### 🚨 Emergency Alerts
Handles emergency cases like falls or sudden health warnings.
The system can log, display, or trigger alerts through the emergency agent.

### 💬 Emotional Wellbeing
The emotional wellbeing agent analyzes user input text and classifies emotions (e.g., happy, sad, anxious).
It provides supportive replies and helpful tips to improve mental health.

### 📊 Dashboard Overview
The Streamlit dashboard provides:
-Tabs for Vitals, Emotional Wellbeing, Emergency, and Reminders
-Data visualization using pandas, matplotlib, and plotly
-Real-time updates and simple UI for users and healthcare agents

---

## ▶️ How to Run the Project
Run the main dashboard (no need to start agents separately):
streamlit run streamlit_dashboard.py
Once started, open the link shown in the terminal (usually http://localhost:8501).

---

## 🧩 Tech Stack
- **Frontend/UI: Streamlit**
- **Backend: Flask**
- **Database: SQLite**
- **Language: Python**
- **Visualization: Matplotlib, Plotly**
- **AI/NLP: NLTK, TextBlob**

---

## ⚠️ Disclaimer
This project is for educational and research purposes only.
It is not intended for clinical or emergency medical use.
