"""
emergency_agent.py
FINAL CLEAN ALERT-ONLY VERSION

✔ No dummy vitals
✔ No NORMAL spam
✔ Shows only WARNING or CRITICAL
✔ Uses fall agent critical flag
✔ Uses BPM thresholds
✔ Demo + paper ready
"""

import json
import os
import time
from datetime import datetime

# -------------------------------------------------
# PATH SETUP
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FALL_EVENTS_FILE = os.path.join(
    BASE_DIR,
    "fall_detection_agent",
    "data",
    "fall_events.json"
)

ESCALATION_FILE = os.path.join(
    BASE_DIR,
    "fall_detection_agent",
    "data",
    "escalation.json"
)

os.makedirs(os.path.dirname(ESCALATION_FILE), exist_ok=True)

# -------------------------------------------------
# SETTINGS
# -------------------------------------------------
CHECK_INTERVAL = 1

LOW_BPM = 40
HIGH_BPM = 180
EXTREME_BPM = 220

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
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
    print("\n🚨 Emergency Agent RUNNING (ALERT-ONLY MODE)")
    print("Reading :", FALL_EVENTS_FILE)
    print("Writing :", ESCALATION_FILE)
    print("-" * 50)

    last_event_hash = None

    while True:
        fall_events = load_json(FALL_EVENTS_FILE)
        latest = fall_events[-1] if fall_events else None

        if latest:
            event_hash = json.dumps(latest, sort_keys=True)

            if event_hash != last_event_hash:
                last_event_hash = event_hash

                magnitude = float(latest.get("magnitude", 0))
                bpm = float(latest.get("bpm", 0))
                critical_flag = bool(latest.get("critical", False))

                valid_bpm = LOW_BPM <= bpm <= 300

                # -------- DECISION LOGIC --------
                severity = None

                if critical_flag:
                    severity = "CRITICAL"
                elif valid_bpm and bpm >= EXTREME_BPM:
                    severity = "CRITICAL"
                elif valid_bpm and (bpm < LOW_BPM or bpm > HIGH_BPM):
                    severity = "WARNING"

                # -------- LOG ONLY IF ALERT --------
                if severity:
                    icon = "🚨" if severity == "CRITICAL" else "🟠"

                    escalation = {
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "source": "emergency_agent",
                        "severity": severity,
                        "device_id": "esp32_01",
                        "data": {
                            "magnitude": magnitude,
                            "bpm": bpm,
                            "critical_from_fall_agent": critical_flag
                        }
                    }

                    append_escalation(escalation)
                    print(f"{icon} EVENT → {severity} | mag={magnitude} bpm={bpm} critical={critical_flag}")

        time.sleep(CHECK_INTERVAL)

# -------------------------------------------------
# ENTRY
# -------------------------------------------------
if __name__ == "__main__":
    main()
