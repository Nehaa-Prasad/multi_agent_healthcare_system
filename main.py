import os
import json
import threading
from flask import Flask, jsonify, render_template, redirect

# -----------------------------
# Agents Imports
# -----------------------------
from multi_agent_healthcare_system.data.reminder_agent import add_sample_reminders, get_all_reminders, check_reminders
from emergency_agent.emergency_agent import detect_emergency
from health_monitoring_agent.health_monitor_agent import monitor_health
from health_monitoring_agent.health_simulator import HealthDataSimulator
from fall_detection_agent.fall_detection_agent import monitor_falls
from fall_detection_agent.fall_simulator import FallDetectionSimulator

# -----------------------------
# Flask Dashboard Setup
# -----------------------------
template_dir = os.path.join(os.getcwd(), "dashboard", "templates")
app = Flask(__name__, template_folder=template_dir)

@app.route("/")
def home():
    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/get_vitals")
def get_vitals():
    try:
        with open("data/vitals_stream.json") as f:
            data = json.load(f)
        return jsonify(data[-10:])
    except:
        return jsonify([])

@app.route("/get_alerts")
def get_alerts():
    try:
        with open("data/escalation.json") as f:
            data = json.load(f)
        return jsonify(data.get("alerts", [])[-10:])
    except:
        return jsonify([])

@app.route("/get_reminders")
def get_reminders():
    try:
        reminders = get_all_reminders()
        due = check_reminders()
        return jsonify({"all": reminders, "due": due})
    except:
        return jsonify({"all": [], "due": []})

# -----------------------------
# Background Agents
# -----------------------------
def start_background_agents():
    # Start simulators
    threading.Thread(target=HealthDataSimulator().run_continuous_simulation,
                     kwargs={"duration_seconds": 3600}, daemon=True).start()
    threading.Thread(target=FallDetectionSimulator().run_continuous_simulation,
                     kwargs={"duration_seconds": 3600}, daemon=True).start()

    # Start monitoring agents
    threading.Thread(target=monitor_health, daemon=True).start()
    threading.Thread(target=monitor_falls, daemon=True).start()

# -----------------------------
# Main logic for reminders/emergencies
# -----------------------------
def main():
    add_sample_reminders()
    all_reminders = get_all_reminders()
    due_reminders = check_reminders()

    combined_data = {
        "health": {"critical_vitals": False},
        "fall": {"fall_detected": False},
        "cognitive": {"risk_flag": False},
        "emotion": {"stress_high": False},
        "reminders": due_reminders
    }

    emergency_alerts = detect_emergency(combined_data)
    print("All Reminders:", all_reminders)
    print("Emergency Alerts:", emergency_alerts)

# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    print("🚀 Starting Multi-Agent Healthcare System...")

    # Initialize reminders
    main()

    # Start background agents
    start_background_agents()

    # Run dashboard Flask app
    app.run(port=5000, debug=False, use_reloader=False)
