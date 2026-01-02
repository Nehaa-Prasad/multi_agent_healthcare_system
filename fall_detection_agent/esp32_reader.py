#!/usr/bin/env python3
"""
esp32_writer_full.py

Serial JSON saver for ESP32:
 - IMU / fall records -> data/readings.ndjson & data/fall_events.json
 - Pulse / vitals     -> data/vitals_stream.json (single JSON array, trimmed)

Behavior:
 - If an incoming JSON object contains both vitals and IMU keys, it is saved into BOTH files.
"""

import serial
import serial.tools.list_ports
import json
import time
import os
from datetime import datetime

# ---------------- CONFIG ----------------
ESP32_PORT = "/dev/cu.SLAB_USBtoUART"               # set to "/dev/cu.SLAB_USBtoUART" to force, else None to auto-detect
BAUD_RATE = 115200
DATA_DIR = "data"

# FALL / IMU files
FALL_NDJSON = os.path.join(DATA_DIR, "readings.ndjson")
FALL_JSON_ARR = os.path.join(DATA_DIR, "fall_events.json")

# VITALS file (pulse)
VITALS_JSON = os.path.join(DATA_DIR, "vitals_stream.json")

MAX_RECORDS = 1000
SERIAL_TIMEOUT = 1  # seconds

# Ensure base data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- utility functions ----------------
def find_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None
    prefer_keys = ("SLAB", "CP210", "CH340", "FTDI", "USB")
    for p in ports:
        name = (p.device or "").upper()
        desc = (p.description or "").upper()
        if any(k in name or k in desc for k in prefer_keys):
            return p.device
    return ports[0].device

def open_serial(port):
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=SERIAL_TIMEOUT)
        time.sleep(2)
        print(f"✅ Serial open: {port} @ {BAUD_RATE}")
        return ser
    except Exception as e:
        print("❌ Failed to open serial:", e)
        return None

def append_ndjson(path, obj):
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"❌ NDJSON append error ({path}):", e)

def load_json_array(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        # corrupted or empty file
        print(f"⚠️ Could not load JSON array ({path}): {e}")
        return []

def write_json_array(path, arr):
    try:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(arr, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
        print(f"💾 Wrote {len(arr)} records -> {path}")
    except Exception as e:
        print(f"❌ write_json_array error ({path}):", e)

# ---------------- save functions ----------------
def save_fall_record(obj):
    try:
        # Optionally create a shallow copy if you want to strip vitals from fall records:
        # fall_obj = {k:v for k,v in obj.items() if k not in ("bpm","heart_rate","pulse","pulse_raw")}
        # use fall_obj below instead of obj if you want to store without vitals fields.
        obj.setdefault("device_id", "esp32_fall_sensor_001")
        obj.setdefault("timestamp", datetime.utcnow().isoformat() + "Z")
        obj["_received_at"] = datetime.utcnow().isoformat() + "Z"

        append_ndjson(FALL_NDJSON, obj)

        arr = load_json_array(FALL_JSON_ARR)
        arr.append(obj)
        if len(arr) > MAX_RECORDS:
            arr = arr[-MAX_RECORDS:]
        write_json_array(FALL_JSON_ARR, arr)
    except Exception as e:
        print("❌ save_fall_record failed:", e)

def save_vitals_record(obj):
    try:
        obj.setdefault("device_id", "esp32_pulse_001")
        obj.setdefault("timestamp", datetime.utcnow().isoformat() + "Z")
        obj["_received_at"] = datetime.utcnow().isoformat() + "Z"

        # Load existing vitals array
        if os.path.exists(VITALS_JSON):
            try:
                with open(VITALS_JSON, "r", encoding="utf-8") as f:
                    arr = json.load(f)
            except Exception:
                arr = []
        else:
            arr = []

        arr.append(obj)
        if len(arr) > MAX_RECORDS:
            arr = arr[-MAX_RECORDS:]

        tmp = VITALS_JSON + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(arr, f, indent=2, ensure_ascii=False)
        os.replace(tmp, VITALS_JSON)
        print(f"💾 Pulse saved -> {VITALS_JSON} (bpm={obj.get('bpm') or obj.get('heart_rate')})")
    except Exception as e:
        print("❌ save_vitals_record failed:", e)

# ---------------- improved classify_and_save ----------------
def classify_and_save(obj):
    """
    Save to:
      - BOTH if object contains vitals + imu
      - VITALS only if only vitals present
      - FALL only if only imu present
      - fallback to FALL
    """
    has_vitals = any(k in obj for k in ("bpm", "pulse", "pulse_raw", "heart_rate"))
    has_imu = ("magnitude" in obj) or (all(k in obj for k in ("x", "y", "z")))

    if has_vitals and has_imu:
        # Save both. If you prefer fall record without bpm, uncomment the creation of fall_obj below.
        try:
            save_vitals_record(obj)
        except Exception as e:
            print("❌ save_vitals_record error (both):", e)
        try:
            # Optionally remove vitals fields from fall copy:
            # fall_obj = {k:v for k,v in obj.items() if k not in ('bpm','pulse','pulse_raw','heart_rate')}
            # save_fall_record(fall_obj)
            save_fall_record(obj)
        except Exception as e:
            print("❌ save_fall_record error (both):", e)
        return "both"

    if has_vitals:
        try:
            save_vitals_record(obj)
        except Exception as e:
            print("❌ save_vitals_record error:", e)
        return "vitals"

    if has_imu:
        try:
            save_fall_record(obj)
        except Exception as e:
            print("❌ save_fall_record error:", e)
        return "fall"

    # fallback default — save to fall to avoid losing data
    try:
        save_fall_record(obj)
    except Exception as e:
        print("❌ save_fall_record error (fallback):", e)
    return "fall"

# ---------------- parse helper ----------------
def try_parse_json_line(line):
    try:
        return json.loads(line)
    except Exception:
        return None

# ---------------- main loop ----------------
def main():
    port = ESP32_PORT or find_port()
    if not port:
        print("No serial ports found. Set ESP32_PORT to the device path and retry.")
        return

    ser = open_serial(port)
    if not ser:
        return

    print("Paths used:")
    print(" - FALL NDJSON:", os.path.abspath(FALL_NDJSON))
    print(" - FALL JSON :", os.path.abspath(FALL_JSON_ARR))
    print(" - VITALS JSON:", os.path.abspath(VITALS_JSON))
    print("Listening for JSON lines... Press Ctrl+C to stop.\n")

    total = 0
    fall_count = 0
    vitals_count = 0
    both_count = 0

    try:
        while True:
            try:
                raw = ser.readline()
            except Exception as e:
                print("Serial read error:", e)
                try:
                    ser.close()
                except:
                    pass
                time.sleep(2)
                ser = open_serial(port)
                if not ser:
                    time.sleep(5)
                    continue
                else:
                    continue

            if not raw:
                time.sleep(0.02)
                continue

            try:
                line = raw.decode("utf-8", errors="ignore").strip()
            except Exception:
                continue

            if not line:
                continue

            if not line.startswith("{"):
                # skip non-json lines (optionally print)
                # print("DBG:", line)
                continue

            obj = try_parse_json_line(line)
            if not obj:
                print("⚠️ Received invalid JSON:", line)
                continue

            total += 1
            kind = classify_and_save(obj)
            if kind == "fall":
                fall_count += 1
                mag = obj.get("magnitude")
                print(f"#{total} -> FALL ({fall_count}) mag={mag}")
            elif kind == "vitals":
                vitals_count += 1
                bpm = obj.get("bpm") or obj.get("heart_rate")
                print(f"#{total} -> VITALS ({vitals_count}) bpm={bpm}")
            else:  # both
                both_count += 1
                mag = obj.get("magnitude")
                bpm = obj.get("bpm") or obj.get("heart_rate")
                print(f"#{total} -> BOTH ({both_count}) mag={mag} bpm={bpm}")

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        try:
            ser.close()
        except:
            pass
        print(f"Processed: {total} records (fall={fall_count}, vitals={vitals_count}, both={both_count})")
        print("Files written:")
        print(" -", os.path.abspath(FALL_JSON_ARR))
        print(" -", os.path.abspath(FALL_NDJSON))
        print(" -", os.path.abspath(VITALS_JSON))

if __name__ == "__main__":
    main()
