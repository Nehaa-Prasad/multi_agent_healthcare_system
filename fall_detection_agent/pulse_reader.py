#!/usr/bin/env python3
"""
ESP32 Pulse Sensor Reader
Reads BPM from ESP32 (pulse sensor) and saves to data/vitals_stream.json
"""

import serial
import json
import time
import os
from datetime import datetime

ESP32_PORT = "COM3"  # CHANGE to your ESP32 port
BAUD = 115200
OUTFILE = "../data/vitals_stream.json"  # health agent reads this


def main():
    print("=" * 60)
    print("ESP32 Pulse Reader")
    print("=" * 60)
    print(f"Port: {ESP32_PORT}")
    print(f"Baud: {BAUD}")
    print(f"Output: {OUTFILE}")
    print("=" * 60)

    try:
        ser = serial.Serial(ESP32_PORT, BAUD, timeout=1)
        time.sleep(2)
        print(f"✅ Connected to {ESP32_PORT}")
    except Exception as e:
        print(f"❌ Could not open {ESP32_PORT}: {e}")
        return

    record_count = 0
    try:
        while True:
            line = ser.readline().decode(errors="ignore").strip()
            if not line.startswith("{"):
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            data["timestamp"] = datetime.now().isoformat()
            data["device_id"] = data.get("device_id", "esp32_pulse_001")

            os.makedirs("../data", exist_ok=True)
            try:
                with open(OUTFILE, "r") as f:
                    all_data = json.load(f)
            except Exception:
                all_data = []

            all_data.append(data)
            if len(all_data) > 1000:
                all_data = all_data[-1000:]

            with open(OUTFILE, "w") as f:
                json.dump(all_data, f, indent=2)

            record_count += 1
            print(f"#{record_count} BPM={data.get('bpm')} raw={data.get('raw')}")

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        ser.close()
        print(f"Saved to {OUTFILE}")


if __name__ == "__main__":
    main()

