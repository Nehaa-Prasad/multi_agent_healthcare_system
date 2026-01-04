"""
emergency_agent.py
macOS SAFE VERSION

✔ Reads live fall data from data/fall_events.json
✔ Decides CRITICAL inside emergency agent
✔ Dumps CRITICAL + NORMAL data
✔ Dumps dummy NORMAL vitals every 20s if no CRITICAL
✔ Writes escalation.json to fall_detection_agent/data
"""

import json
import os
import time
from datetime import datetime

# -------------------------------------------------
# PATH SETUP
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAIN_DATA_DIR = os.path.join(BASE_DIR, "data")
FALL_EVENTS_FILE = os.path.join(MAIN_DATA_DIR, "fall_events.json")

FALL_AGENT_DIR = os.path.join(BASE_DIR, "fall_detection_agent", "data")
ESCALATION_FILE = os.path.join(FALL_AGENT_DIR, "escalation.json")

os.makedirs(FALL_AGENT_DIR, exist_ok=True)

# -------------------------------------------------
# SETTINGS
# -------------------------------------------------
FALL_CHECK_INTERVAL = 1        # seconds
DUMMY_VITAL_INTERVAL = 20      # seconds  ⬅️ CHANGED HERE

HIGH_MAG_THRESHOLD = 0.9
LOW_BPM_THRESHOLD = 40
HIGH_BPM_THRESHOLD = 180

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def load_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def ensure_list(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("events", [])
    return []

def append_escalation(record):
    data = load_json(ESCALATION_FILE)
    if not isinstance(data, list):
        data = []

    data.append(record)

    with open(ESCALATION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    print("\n🚨 Emergency Agent RUNNING")
    print("Reading from :", FALL_EVENTS_FILE)
    print("Writing to   :", ESCALATION_FILE)
    print("-" * 50)

    last_seen_falls = 0
    last_critical_time = 0

    while True:
        now = time.time()

        # ---------------- FALL DATA ----------------
        raw_falls = load_json(FALL_EVENTS_FILE)
        fall_events = ensure_list(raw_falls)

        if len(fall_events) > last_seen_falls:
            new_falls = fall_events[last_seen_falls:]

            for rec in new_falls:
                mag = rec.get("mag", 0)
                bpm = rec.get("bpm", 0)
                critical_flag = rec.get("critical", False)

                if (
                    critical_flag or
                    mag > HIGH_MAG_THRESHOLD or
                    bpm < LOW_BPM_THRESHOLD or
                    bpm > HIGH_BPM_THRESHOLD
                ):
                    severity = "CRITICAL"
                    last_critical_time = now
                else:
                    severity = "NORMAL"

                escalation = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "source": "fall_detection_agent",
                    "severity": severity,
                    "device_id": "esp32_01",
                    "data": {
                        "mag": mag,
                        "bpm": bpm,
                        "critical": critical_flag
                    }
                }

                append_escalation(escalation)
                print(f"🚨 FALL DUMPED → {severity}")

            last_seen_falls = len(fall_events)

        # ---------------- DUMMY VITAL DATA ----------------
        if (now - last_critical_time) >= DUMMY_VITAL_INTERVAL:
            dummy_vitals = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "vitals_stream",
                "severity": "NORMAL",
                "device_id": "dummy_device",
                "data": {
                    "heart_rate": 72,
                    "spo2": 98,
                    "status": "normal"
                }
            }

            append_escalation(dummy_vitals)
            last_critical_time = now
            print("🟢 DUMMY VITAL → NORMAL")

        time.sleep(FALL_CHECK_INTERVAL)

# -------------------------------------------------
# ENTRY
# -------------------------------------------------
if __name__ == "__main__":
    main()
