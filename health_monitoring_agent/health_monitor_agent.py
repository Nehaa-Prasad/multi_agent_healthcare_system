import json
import time
import os
from datetime import datetime

# ---------- CONFIG ----------
VITALS_PATH = "../data/vitals_stream.json"
ESCALATION_PATH = "../data/escalation.json"

# Safe threshold values for basic health monitoring
THRESHOLDS = {
    "heart_rate": (60, 100),          # bpm
    "bp_systolic": (90, 120),         # mmHg
    "bp_diastolic": (60, 80),         # mmHg
    "oxygen_saturation": (94, 100),   # %
    "temperature": (36.0, 37.5)       # °C
}

# ---------- HELPER FUNCTIONS ----------

def load_json(file_path):
    """Safely load JSON file and handle empty/invalid data."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_alert(alert):
    """Append a new alert to escalation.json."""
    data = {"alerts": []}
    
    # Create file if not exists
    if os.path.exists(ESCALATION_PATH):
        try:
            with open(ESCALATION_PATH, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {"alerts": []}

    data["alerts"].append(alert)

    with open(ESCALATION_PATH, "w") as f:
        json.dump(data, f, indent=4)

def check_vitals(vitals):
    """Check each vital against its threshold and create alerts."""
    alerts = []
    for key, (low, high) in THRESHOLDS.items():
        value = vitals.get(key)
        if value is None:
            continue
        if not (low <= value <= high):
            alerts.append({
                "type": "health",
                "parameter": key,
                "value": value,
                "message": f"Abnormal {key}: {value}",
                "time": datetime.now().isoformat()
            })
    return alerts


# ---------- MAIN AGENT LOOP ----------

def monitor_health():
    print("Health Monitor Agent started...")
    print("Monitoring vitals from:", VITALS_PATH)
    print("Alerts will be saved to:", ESCALATION_PATH)
    print("=" * 50)
    
    seen_records = 0  # To track progress

    while True:
        vitals_data = load_json(VITALS_PATH)

        # Skip if no new data
        if len(vitals_data) <= seen_records:
            time.sleep(2)
            continue

        # Process only new records
        new_records = vitals_data[seen_records:]
        seen_records = len(vitals_data)

        for vitals in new_records:
            print(f"Checking vitals: HR={vitals.get('heart_rate')}, BP={vitals.get('bp_systolic')}/{vitals.get('bp_diastolic')}, O2={vitals.get('oxygen_saturation')}%")
            
            alerts = check_vitals(vitals)
            for alert in alerts:
                print(f"ALERT: {alert['message']} at {alert['time']}")
                save_alert(alert)
            
            if not alerts:
                print("All vitals within normal range")

        time.sleep(2)  # check every 2 seconds


if __name__ == "__main__":
    monitor_health()
