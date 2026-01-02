#!/usr/bin/env python3
"""
esp32_writer_full.py

Serial JSON saver for ESP32:
 - IMU / fall records -> data/readings.ndjson & data/fall_events.json
 - Pulse / vitals     -> data/vitals_stream.json

Adds emergency / critical tagging so Emergency Agent can react.
"""

import serial
import serial.tools.list_ports
import json
import time
import os
from datetime import datetime

# ---------------- CONFIG ----------------
ESP32_PORT = "/dev/cu.SLAB_USBtoUART"   # set None to auto-detect
BAUD_RATE = 115200
DATA_DIR = "data"

FALL_NDJSON = os.path.join(DATA_DIR, "readings.ndjson")
FALL_JSON_ARR = os.path.join(DATA_DIR, "fall_events.json")
VITALS_JSON = os.path.join(DATA_DIR, "vitals_stream.json")

MAX_RECORDS = 1000
SERIAL_TIMEOUT = 1

# -------- CRITICAL THRESHOLDS (IMPORTANT) --------
CRITICAL_BPM_HIGH = 120
CRITICAL_BPM_LOW  = 45
CRITICAL_IMPACT   = 3.0

os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- utility ----------------
def find_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None
    prefer = ("SLAB", "CP210", "CH340", "FTDI", "USB")
    for p in ports:
        if any(k in (p.device + p.description).upper() for k in prefer):
            return p.device
    return ports[0].device

def open_serial(port):
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=SERIAL_TIMEOUT)
        time.sleep(2)
        print(f"✅ Serial open: {port}")
        return ser
    except Exception as e:
        print("❌ Serial open failed:", e)
        return None

def append_ndjson(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def load_json_array(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def write_json_array(path, arr):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(arr, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

# ---------------- SAVE FUNCTIONS ----------------
def save_fall_record(obj):
    obj.setdefault("device_id", "esp32_fall_sensor_001")
    obj.setdefault("timestamp", datetime.utcnow().isoformat() + "Z")
    obj["_received_at"] = datetime.utcnow().isoformat() + "Z"

    append_ndjson(FALL_NDJSON, obj)

    arr = load_json_array(FALL_JSON_ARR)
    arr.append(obj)
    if len(arr) > MAX_RECORDS:
        arr = arr[-MAX_RECORDS:]
    write_json_array(FALL_JSON_ARR, arr)

def save_vitals_record(obj):
    obj.setdefault("device_id", "esp32_pulse_001")
    obj.setdefault("timestamp", datetime.utcnow().isoformat() + "Z")
    obj["_received_at"] = datetime.utcnow().isoformat() + "Z"

    arr = load_json_array(VITALS_JSON)
    arr.append(obj)
    if len(arr) > MAX_RECORDS:
        arr = arr[-MAX_RECORDS:]
    write_json_array(VITALS_JSON, arr)

# ---------------- EMERGENCY CLASSIFICATION ----------------
def classify_and_save(obj):
    has_vitals = any(k in obj for k in ("bpm", "pulse", "pulse_raw", "heart_rate"))
    has_imu = ("magnitude" in obj) or all(k in obj for k in ("x", "y", "z"))

    # ---- CRITICAL DETECTION ----
    critical = False
    reasons = []

    bpm = obj.get("bpm") or obj.get("heart_rate")
    mag = obj.get("magnitude")

    try:
        if bpm is not None:
            bpm = float(bpm)
            if bpm > CRITICAL_BPM_HIGH or bpm < CRITICAL_BPM_LOW:
                critical = True
                reasons.append("ABNORMAL_HEART_RATE")
    except:
        pass

    try:
        if mag is not None:
            mag = float(mag)
            if mag >= CRITICAL_IMPACT:
                critical = True
                reasons.append("FALL_IMPACT")
    except:
        pass

    # ---- ATTACH EMERGENCY METADATA ----
    obj["is_critical"] = critical
    obj["critical_reasons"] = reasons
    obj["event_type"] = "EMERGENCY" if critical else "NORMAL"

    # ---- SAVE ROUTING ----
    if has_vitals and has_imu:
        save_vitals_record(obj)
        save_fall_record(obj)
        return "both"

    if has_vitals:
        save_vitals_record(obj)
        return "vitals"

    if has_imu:
        save_fall_record(obj)
        return "fall"

    save_fall_record(obj)
    return "fall"

# ---------------- JSON PARSER ----------------
def try_parse_json_line(line):
    try:
        return json.loads(line)
    except:
        return None

# ---------------- MAIN LOOP ----------------
def main():
    port = ESP32_PORT or find_port()
    if not port:
        print("❌ No serial port found")
        return

    ser = open_serial(port)
    if not ser:
        return

    print("Listening for ESP32 JSON...\n")

    total = fall = vitals = both = 0

    try:
        while True:
            raw = ser.readline()
            if not raw:
                continue

            line = raw.decode("utf-8", errors="ignore").strip()
            if not line.startswith("{"):
                continue

            obj = try_parse_json_line(line)
            if not obj:
                continue

            total += 1
            kind = classify_and_save(obj)

            if kind == "fall":
                fall += 1
                print(f"#{total} FALL | mag={obj.get('magnitude')} | critical={obj['is_critical']}")
            elif kind == "vitals":
                vitals += 1
                print(f"#{total} VITALS | bpm={obj.get('bpm')} | critical={obj['is_critical']}")
            else:
                both += 1
                print(f"#{total} BOTH | mag={obj.get('magnitude')} bpm={obj.get('bpm')} | critical={obj['is_critical']}")

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        ser.close()
        print(f"\nProcessed {total} records (fall={fall}, vitals={vitals}, both={both})")

if __name__ == "__main__":
    main()
