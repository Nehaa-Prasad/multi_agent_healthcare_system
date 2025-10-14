import json
import time
import os
from datetime import datetime

# ---------- CONFIG ----------
FALL_EVENTS_PATH = "../data/fall_events.json"
ESCALATION_PATH = "../data/escalation.json"

# Fall detection thresholds
FALL_THRESHOLD = 2.5  # g-force above this indicates potential fall
IMPACT_THRESHOLD = 3.0  # g-force above this indicates impact

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

def check_fall_events(accelerometer_data):
    """Check accelerometer data for fall events and create alerts."""
    alerts = []
    
    # Check for high magnitude (potential fall)
    magnitude = accelerometer_data.get('magnitude', 0)
    activity = accelerometer_data.get('activity', '')
    
    if magnitude > FALL_THRESHOLD:
        if activity in ['FALL_IMPACT', 'FALL_DROP']:
            alerts.append({
                "type": "fall",
                "parameter": "magnitude",
                "value": magnitude,
                "message": f"Fall detected! Magnitude: {magnitude:.2f}g, Activity: {activity}",
                "time": datetime.now().isoformat(),
                "severity": "HIGH" if magnitude > IMPACT_THRESHOLD else "MEDIUM"
            })
    
    # Check for inactivity (no movement for extended periods)
    # This would require tracking time since last movement
    # For now, we'll focus on immediate fall detection
    
    return alerts


# ---------- MAIN AGENT LOOP ----------

def monitor_falls():
    print("Fall Detection Agent started...")
    print("Monitoring accelerometer data from:", FALL_EVENTS_PATH)
    print("Alerts will be saved to:", ESCALATION_PATH)
    print("=" * 50)
    
    seen_records = 0  # To track progress

    while True:
        fall_data = load_json(FALL_EVENTS_PATH)

        # Skip if no new data
        if len(fall_data) <= seen_records:
            time.sleep(2)
            continue

        # Process only new records
        new_records = fall_data[seen_records:]
        seen_records = len(fall_data)

        for accelerometer in new_records:
            print(f"Checking movement: X={accelerometer.get('x')}, Y={accelerometer.get('y')}, Z={accelerometer.get('z')}, Mag={accelerometer.get('magnitude')}, Activity={accelerometer.get('activity')}")
            
            alerts = check_fall_events(accelerometer)
            for alert in alerts:
                print(f"FALL ALERT: {alert['message']} at {alert['time']}")
                save_alert(alert)
            
            if not alerts:
                print("Normal movement detected")

        time.sleep(2)  # check every 2 seconds


if __name__ == "__main__":
    monitor_falls()
