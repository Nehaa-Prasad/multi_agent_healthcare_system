"""
emergency_agent.py
macOS SAFE VERSION

✔ Dumps NEW data every 3 seconds
✔ No duplicate dumping
✔ Writes escalation.json cleanly
"""

import json
import os
import time
from datetime import datetime

# ===== PATH SETUP (MAC SAFE) =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

FALL_EVENTS_FILE = os.path.join(DATA_DIR, "fall_events.json")
VITALS_FILE = os.path.join(DATA_DIR, "vitals_stream.json")
ESCALATION_FILE = os.path.join(DATA_DIR, "escalation.json")

DUMP_INTERVAL = 3   # ⏱️ 3 seconds

os.makedirs(DATA_DIR, exist_ok=True)

# ===== HELPERS =====
def load_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ escalation.json updated ({len(data)} records)")

# ===== MAIN =====
def main():
    print("\n🚨 Emergency Agent running (3s dump interval)")
    print("Project root:", BASE_DIR)
    print("Data dir    :", DATA_DIR)
    print("-" * 50)

    escalations = load_json(ESCALATION_FILE)

    last_fall_idx = 0
    last_vitals_idx = 0

    while True:
        fall_events = load_json(FALL_EVENTS_FILE)
        vitals_events = load_json(VITALS_FILE)

        # ---- NEW FALL RECORDS ----
        if len(fall_events) > last_fall_idx:
            new_falls = fall_events[last_fall_idx:]
            for rec in new_falls:
                escalations.append({
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "source": "fall_events",
                    "device_id": rec.get("device_id", "unknown"),
                    "data": rec
                })
                print("🟡 dumped new FALL record")

            last_fall_idx = len(fall_events)

        # ---- NEW VITAL RECORDS ----
        if len(vitals_events) > last_vitals_idx:
            new_vitals = vitals_events[last_vitals_idx:]
            for rec in new_vitals:
                escalations.append({
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "source": "vitals_stream",
                    "device_id": rec.get("device_id", "unknown"),
                    "data": rec
                })
                print("🟡 dumped new VITAL record")

            last_vitals_idx = len(vitals_events)

        write_json(ESCALATION_FILE, escalations)
        time.sleep(DUMP_INTERVAL)

# ===== ENTRY =====
if __name__ == "__main__":
    main()
