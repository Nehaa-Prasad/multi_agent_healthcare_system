# 🩺 Multi-Agent Healthcare System (Windows + IoT Setup)

A **smart multi-agent healthcare monitoring system** designed to assist users with **health tracking, fall detection, reminders, cognitive health, and emotional wellbeing**, integrated with **ESP32 IoT sensors** and visualized through an interactive **Streamlit dashboard**.

---

## 🚀 System Overview

This project consists of:
- **ESP32 IoT device** sending real-time sensor data
- **Python backend** to read serial data and process events
- **Multi-agent architecture** for healthcare monitoring
- **Streamlit dashboard** for real-time visualization

⚠️ When running with IoT, **TWO TERMINALS MUST RUN SIMULTANEOUSLY** in VS Code.

---

## 🧰 Prerequisites (Windows Only)

### 1️⃣ Install Python
1. Download: https://www.python.org/downloads/windows/
2. During installation:
   - ✅ Check **Add Python to PATH**
3. Verify:
```bash
python --version
```

---

### 2️⃣ Install Git
Download and install:
https://git-scm.com/download/win

Verify:
```bash
git --version
```

---

### 3️⃣ Install VS Code
Download:
https://code.visualstudio.com/

Install these extensions:
- Python
- PlatformIO IDE

---

### 4️⃣ Install ESP32 USB Driver
Install according to ESP32 chip:
- CP210x: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
- CH340: https://www.wch.cn/downloads/CH341SER_EXE.html

🔁 Restart system after installation.

---

## 📥 Clone the Repository

```bash
git clone https://github.com/<your-username>/multi_agent_healthcare_system.git
cd multi_agent_healthcare_system
```

---

## 🐍 Virtual Environment Setup

```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in terminal.

---

## 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

If needed:
```bash
pip install streamlit flask flask-socketio pyserial pandas matplotlib plotly nltk textblob
```

---

## ⚙️ Project Structure

```
multi_agent_healthcare_system/
│
├── cognitive_health_agent
├── emergency_agent
├── emotional_wellbeing_agent
├── fall_detection_agent
├── health_monitoring_agent
├── reminder_agent
│
├── data/
│   ├── escalation.json
│   ├── fall_events.json
│   ├── reminders.json
│   └── vitals_stream.json
│
├── serial_reader.py
├── main.py
├── streamlit_dashboard.py
├── reminder_db.sqlite
├── requirements.txt
└── README.md
```

---

## 🔌 ESP32 IoT Setup

### 1️⃣ Upload Code to ESP32
1. Open ESP32 project in VS Code (PlatformIO)
2. Connect ESP32 via USB
3. Upload code
4. Open Serial Monitor
5. Confirm data is printing continuously

---

### 2️⃣ Identify COM Port
1. Open **Device Manager**
2. Go to **Ports (COM & LPT)**
3. Note port (example: `COM3`)

---

### 3️⃣ Update COM Port in Python
In `serial_reader.py`:
```python
SERIAL_PORT = "COM3"
BAUD_RATE = 9600
```

(Change COM number if required)

---

## ▶️ How to Run the Project (IMPORTANT)

⚠️ **TWO TERMINALS MUST BE OPEN IN VS CODE**

---

## 🟢 TERMINAL 1 – Backend / Agents

```bash
venv\Scripts\activate
python main.py
```

This handles:
- Multi-agent logic
- Fall detection
- Emergency escalation
- Health data processing

⚠️ Do NOT close this terminal.

---

## 🟢 TERMINAL 2 – IoT Serial Reader

```bash
venv\Scripts\activate
python serial_reader.py
```

Expected output:
```text
Connected to ESP32 on COM3
Sensor data received...
```

⚠️ This terminal reads live ESP32 data.

---

## 🟢 TERMINAL 3 – Streamlit Dashboard

(You may open this in Terminal 1 after backend starts, or a new terminal)

```bash
venv\Scripts\activate
streamlit run streamlit_dashboard.py
```

Open browser:
```
http://localhost:8501
```

---

## 📊 Dashboard Features

### ❤️ Health Monitoring
- Tracks vitals like heart rate, SpO₂, temperature
- Stores data in `vitals_stream.json`
- Detects abnormal readings

### 🤕 Fall Detection
- Detects sudden motion changes
- Logs events in `fall_events.json`
- Triggers emergency alerts

### 🧠 Cognitive Health Bot
- NLP-based chatbot
- Health tips, reminders, emotional support
- Connects multiple agents

### 🕑 Reminders
- Medicine and health reminders
- Loaded from `data/reminders.json`

### 🚨 Emergency Alerts
- Handles fall or health emergencies
- Logs escalation events

### 💬 Emotional Wellbeing
- Detects emotions (happy, sad, anxious)
- Provides supportive responses

---

## ❗ Common Errors & Fixes

### ❌ serial not found
```bash
pip install pyserial
```

---

### ❌ COM Port Access Denied
- Close Arduino IDE / PlatformIO Serial Monitor
- Only ONE program can use COM port

---

### ❌ Old Data Showing
- Ensure **serial_reader.py is running**
- Restart both terminals
- Refresh browser

---

## ⛔ Stop the Project

Press:
```text
CTRL + C
```
in **all running terminals**

---

## 🧩 Tech Stack

- **Frontend:** Streamlit
- **Backend:** Flask
- **IoT:** ESP32
- **Language:** Python
- **Database:** SQLite
- **Visualization:** Matplotlib, Plotly
- **AI/NLP:** NLTK, TextBlob

---

## ⚠️ Disclaimer

This project is for **educational and research purposes only**.  
It is **not intended for real-world medical or emergency use**.

---

## ✅ FINAL CHECKLIST

✔ ESP32 connected  
✔ Terminal 1: Backend running  
✔ Terminal 2: Serial reader running  
✔ Terminal 3: Streamlit dashboard running  
✔ Live data visible  
