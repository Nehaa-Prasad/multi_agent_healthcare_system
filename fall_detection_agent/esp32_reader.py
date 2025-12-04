#!/usr/bin/env python3
"""
ESP32 Fall Detection Integration Script
Reads accelerometer data from ESP32 and saves to fall_events.json
This connects ESP32 hardware to your fall detection agent system
"""

import serial
import json
import time
import os
from datetime import datetime

# ESP32 connection (change COM port to match your ESP32)
# Windows: COM3, COM4, etc.
# Mac/Linux: /dev/ttyUSB0, /dev/ttyACM0, etc.
ESP32_PORT = 'COM3'  # ⚠️ CHANGE THIS to your ESP32 port
BAUD_RATE = 115200

# File paths
FALL_EVENTS_FILE = "../data/fall_events.json"

def connect_to_esp32():
    """Connect to ESP32 via serial port"""
    try:
        arduino = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for ESP32 to initialize
        print(f"✅ Connected to ESP32 on {ESP32_PORT}")
        return arduino
    except serial.SerialException as e:
        print(f"❌ Error connecting to ESP32: {e}")
        print(f"   Make sure ESP32 is connected to {ESP32_PORT}")
        print("   Check Device Manager (Windows) or ls /dev/tty* (Mac/Linux)")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def read_esp32_data(arduino):
    """Read data from ESP32 serial port"""
    try:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').strip()
            if line.startswith('{'):
                return json.loads(line)
    except json.JSONDecodeError:
        # Skip invalid JSON lines
        pass
    except UnicodeDecodeError:
        # Skip lines that can't be decoded
        pass
    except Exception as e:
        print(f"⚠️ Error reading data: {e}")
    return None

def save_to_fall_events(data):
    """Save ESP32 data to fall_events.json"""
    # Ensure data directory exists
    os.makedirs("../data", exist_ok=True)
    
    # Load existing data
    if os.path.exists(FALL_EVENTS_FILE):
        try:
            with open(FALL_EVENTS_FILE, 'r') as f:
                all_data = json.load(f)
        except json.JSONDecodeError:
            all_data = []
    else:
        all_data = []
    
    # Add ISO timestamp (if not already present)
    if 'timestamp' not in data or not isinstance(data['timestamp'], str):
        data['timestamp'] = datetime.now().isoformat()
    
    # Ensure device_id is set
    if 'device_id' not in data:
        data['device_id'] = 'esp32_fall_sensor_001'
    
    # Add new data
    all_data.append(data)
    
    # Keep only last 1000 records to prevent file from getting too large
    if len(all_data) > 1000:
        all_data = all_data[-1000:]
        print("⚠️ File size limit reached. Keeping last 1000 records.")
    
    # Save back
    try:
        with open(FALL_EVENTS_FILE, 'w') as f:
            json.dump(all_data, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ Error saving data: {e}")
        return False

def main():
    print("=" * 60)
    print("ESP32 Fall Detection Integration")
    print("=" * 60)
    print(f"Port: {ESP32_PORT}")
    print(f"Baud Rate: {BAUD_RATE}")
    print(f"Output File: {FALL_EVENTS_FILE}")
    print("=" * 60)
    print()
    
    # Connect to ESP32
    arduino = connect_to_esp32()
    if not arduino:
        print("\n❌ Failed to connect. Exiting.")
        print("\nTroubleshooting:")
        print("1. Check ESP32 is connected via USB")
        print("2. Find correct COM port in Device Manager")
        print("3. Update ESP32_PORT in this script")
        return
    
    print("📊 Reading from ESP32...")
    print("Press Ctrl+C to stop")
    print()
    
    record_count = 0
    fall_count = 0
    
    try:
        while True:
            data = read_esp32_data(arduino)
            
            if data:
                record_count += 1
                
                # Save to fall_events.json
                if save_to_fall_events(data):
                    # Print status
                    magnitude = data.get('magnitude', 0)
                    activity = data.get('activity', 'UNKNOWN')
                    fall_detected = data.get('fall_detected', False)
                    
                    if fall_detected:
                        fall_count += 1
                        print(f"🚨 FALL ALERT #{fall_count}: {activity} - Magnitude: {magnitude:.2f}g")
                    else:
                        print(f"✅ Record #{record_count}: Magnitude={magnitude:.2f}g, Activity={activity}")
            
            time.sleep(0.1)  # Small delay to prevent CPU overload
            
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Stopping...")
        arduino.close()
        print(f"✅ Disconnected from ESP32")
        print(f"📊 Total records saved: {record_count}")
        print(f"🚨 Total falls detected: {fall_count}")
        print(f"📁 Data saved to: {FALL_EVENTS_FILE}")
        print("=" * 60)
        print("\n💡 Next step: Run fall_detection_agent.py to process the data!")

if __name__ == "__main__":
    main()
