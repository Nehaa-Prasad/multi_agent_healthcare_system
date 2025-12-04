# ESP32 Fall Detection System using Accelerometer

## 🚀 Quick Start - What Files Do I Use?

**Confused about which file to use? Here's the simple answer:**

| File | What It Is | What To Do |
|------|-----------|-----------|
| `esp32_fall_detection_guide.md` | 📖 **Documentation** (this file) | **Read it** - explains how everything works |
| `esp32_reader.py` | 🐍 **Actual Python code** | **Run this!** - connects ESP32 to your system |

### **Simple Steps:**

1. **Read this file** (`.md`) to understand how it works
2. **Use `esp32_reader.py`** - it's already created and ready!
3. **Don't copy code** from the `.md` file - the real file is already there!

**👉 Just open `esp32_reader.py`, change the COM port, and run it!**

---

## Overview
This document provides ESP32 code to detect falls using an accelerometer (MPU6050). The system monitors acceleration patterns and detects sudden impacts or free-fall that indicate falls.

## Hardware Required
- ESP32 Development Board
- MPU6050 Accelerometer/Gyroscope Module
- Buzzer/LED (for local alert) - Optional
- Breadboard and jumper wires

## Wiring Diagram

### MPU6050 to ESP32
```
MPU6050  →  ESP32
VCC      →  3.3V
GND      →  GND
SCL      →  GPIO 22 (I2C Clock)
SDA      →  GPIO 21 (I2C Data)
```

### Buzzer (Optional)
```
Buzzer   →  ESP32
Positive →  GPIO 2
Negative →  GND
```

## ESP32 Code

```cpp
/* 
 * ESP32 Fall Detection System using MPU6050 Accelerometer
 * Detects falls by monitoring acceleration patterns and sudden impacts
 * Sends data to serial port for Python processing
 * Compatible with ESP32 DevKit
 */

#include <Wire.h>
#include <WiFi.h>

// MPU6050 I2C Address
#define MPU6050_ADDR 0x68

// MPU6050 Register Addresses
#define MPU6050_ACCEL_XOUT_H 0x3B
#define MPU6050_PWR_MGMT_1   0x6B
#define MPU6050_SMPLRT_DIV   0x19
#define MPU6050_CONFIG       0x1A
#define MPU6050_GYRO_CONFIG  0x1B
#define MPU6050_ACCEL_CONFIG 0x1C

// Buzzer Pin (Optional)
#define BUZZER_PIN 2

// Fall Detection Thresholds
#define FALL_THRESHOLD 2.5      // g-force above this indicates potential fall
#define IMPACT_THRESHOLD 3.0    // g-force above this indicates impact
#define FREE_FALL_THRESHOLD 0.3 // g-force below this indicates free fall
#define SAMPLING_RATE 100       // Check every 100ms

// Variables
unsigned long lastCheck = 0;
float accelX, accelY, accelZ;
float gyroX, gyroY, gyroZ;
float magnitude;
bool fallDetected = false;
unsigned long fallTime = 0;

// Moving average for smoothing
float accelX_avg = 0, accelY_avg = 0, accelZ_avg = 0;
const int AVG_SIZE = 5;
float accelX_buffer[AVG_SIZE] = {0};
float accelY_buffer[AVG_SIZE] = {0};
float accelZ_buffer[AVG_SIZE] = {0};
int buffer_index = 0;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  
  // Initialize buzzer pin
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  
  // Initialize MPU6050
  initMPU6050();
  
  Serial.println("ESP32 Fall Detection System Started");
  Serial.println("Monitoring for falls...");
  delay(1000);
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Read accelerometer data every SAMPLING_RATE milliseconds
  if (currentMillis - lastCheck >= SAMPLING_RATE) {
    lastCheck = currentMillis;
    
    // Read MPU6050 data
    readMPU6050();
    
    // Calculate magnitude
    magnitude = sqrt(accelX * accelX + accelY * accelY + accelZ * accelZ);
    
    // Detect fall patterns
    if (detectFall()) {
      triggerFallAlert();
    }
    
    // Send data to serial port (Python will read this)
    sendDataToSerial();
    
    // Reset fall flag after 5 seconds
    if (fallDetected && (currentMillis - fallTime > 5000)) {
      fallDetected = false;
    }
  }
}

// Initialize MPU6050
void initMPU6050() {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_PWR_MGMT_1);
  Wire.write(0x00); // Wake up MPU6050
  Wire.endTransmission();
  
  // Configure accelerometer range (±2g)
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_ACCEL_CONFIG);
  Wire.write(0x00); // ±2g range
  Wire.endTransmission();
  
  // Configure sample rate (1kHz)
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_SMPLRT_DIV);
  Wire.write(0x07); // 1kHz sample rate
  Wire.endTransmission();
  
  // Configure DLPF (Digital Low Pass Filter)
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_CONFIG);
  Wire.write(0x06); // 5Hz DLPF
  Wire.endTransmission();
  
  delay(100);
  Serial.println("MPU6050 initialized");
}

// Read MPU6050 accelerometer and gyroscope data
void readMPU6050() {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_ACCEL_XOUT_H);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU6050_ADDR, 14, true);
  
  // Read accelerometer data (16-bit values)
  int16_t accelX_raw = (Wire.read() << 8 | Wire.read());
  int16_t accelY_raw = (Wire.read() << 8 | Wire.read());
  int16_t accelZ_raw = (Wire.read() << 8 | Wire.read());
  Wire.read(); // Skip temperature
  int16_t gyroX_raw = (Wire.read() << 8 | Wire.read());
  int16_t gyroY_raw = (Wire.read() << 8 | Wire.read());
  int16_t gyroZ_raw = (Wire.read() << 8 | Wire.read());
  
  // Convert to g-force (for ±2g range: divide by 16384)
  accelX = accelX_raw / 16384.0;
  accelY = accelY_raw / 16384.0;
  accelZ = accelZ_raw / 16384.0;
  
  // Convert gyro to degrees per second (for ±250°/s range: divide by 131)
  gyroX = gyroX_raw / 131.0;
  gyroY = gyroY_raw / 131.0;
  gyroZ = gyroZ_raw / 131.0;
  
  // Apply moving average filter for smoothing
  accelX_buffer[buffer_index] = accelX;
  accelY_buffer[buffer_index] = accelY;
  accelZ_buffer[buffer_index] = accelZ;
  buffer_index = (buffer_index + 1) % AVG_SIZE;
  
  // Calculate average
  accelX_avg = 0;
  accelY_avg = 0;
  accelZ_avg = 0;
  for (int i = 0; i < AVG_SIZE; i++) {
    accelX_avg += accelX_buffer[i];
    accelY_avg += accelY_buffer[i];
    accelZ_avg += accelZ_buffer[i];
  }
  accelX_avg /= AVG_SIZE;
  accelY_avg /= AVG_SIZE;
  accelZ_avg /= AVG_SIZE;
  
  // Use smoothed values
  accelX = accelX_avg;
  accelY = accelY_avg;
  accelZ = accelZ_avg;
}

// Detect fall based on acceleration patterns
bool detectFall() {
  // Pattern 1: High impact (sudden stop after fall)
  if (magnitude > IMPACT_THRESHOLD) {
    return true;
  }
  
  // Pattern 2: Free fall detection (low acceleration in all axes)
  if (abs(accelX) < FREE_FALL_THRESHOLD && 
      abs(accelY) < FREE_FALL_THRESHOLD && 
      abs(accelZ) < FREE_FALL_THRESHOLD) {
    return true;
  }
  
  // Pattern 3: Sudden change in acceleration (fall threshold)
  if (magnitude > FALL_THRESHOLD) {
    // Check if this is a sudden spike (not just normal movement)
    static float prev_magnitude = 0;
    float change = abs(magnitude - prev_magnitude);
    prev_magnitude = magnitude;
    
    if (change > 1.5) { // Sudden change > 1.5g
      return true;
    }
  }
  
  return false;
}

// Trigger fall alert
void triggerFallAlert() {
  if (!fallDetected) {
    fallDetected = true;
    fallTime = millis();
    
    // Visual/Audio alert
    for (int i = 0; i < 3; i++) {
      digitalWrite(BUZZER_PIN, HIGH);
      delay(200);
      digitalWrite(BUZZER_PIN, LOW);
      delay(200);
    }
    
    Serial.println("FALL_DETECTED: Person has fallen!");
  }
}

// Send data to Python via Serial
void sendDataToSerial() {
  unsigned long timestamp = millis();
  
  // Determine activity type
  String activity = "NORMAL";
  String alert_level = "NONE";
  
  if (magnitude > IMPACT_THRESHOLD) {
    activity = "FALL_IMPACT";
    alert_level = "HIGH";
  } else if (magnitude > FALL_THRESHOLD) {
    activity = "FALL_DROP";
    alert_level = "MEDIUM";
  } else if (magnitude < FREE_FALL_THRESHOLD) {
    activity = "FREE_FALL";
    alert_level = "HIGH";
  }
  
  // Send JSON format for Python
  Serial.print("{");
  Serial.print("\"timestamp\":");
  Serial.print(timestamp);
  Serial.print(",\"x\":");
  Serial.print(accelX, 3);
  Serial.print(",\"y\":");
  Serial.print(accelY, 3);
  Serial.print(",\"z\":");
  Serial.print(accelZ, 3);
  Serial.print(",\"magnitude\":");
  Serial.print(magnitude, 3);
  Serial.print(",\"activity\":\"");
  Serial.print(activity);
  Serial.print("\",\"fall_detected\":");
  Serial.print(fallDetected ? "true" : "false");
  Serial.print(",\"alert_level\":\"");
  Serial.print(alert_level);
  Serial.print("\",\"device_id\":\"esp32_fall_sensor_001\"");
  Serial.println("}");
}

// Optional: WiFi connection for remote monitoring
void connectWiFi(const char* ssid, const char* password) {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.print("WiFi connected. IP: ");
  Serial.println(WiFi.localIP());
}
```

## Python Integration Code

> **📝 IMPORTANT:** The code below is just an **example** to show you how it works. 
> 
> **✅ ACTUAL FILE TO USE:** We already created `esp32_reader.py` for you! 
> 
> **👉 Just use that file - you don't need to copy this code!**

**Example code (for reference only):**

```python
import serial
import json
import time
import os
from datetime import datetime

# ESP32 connection (change COM port to match your ESP32)
# Windows: COM3, COM4, etc.
# Mac/Linux: /dev/ttyUSB0, /dev/ttyACM0, etc.
ESP32_PORT = 'COM3'  # Change this to your ESP32 port
BAUD_RATE = 115200

# Connect to ESP32
try:
    arduino = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for ESP32 to initialize
    print(f"Connected to ESP32 on {ESP32_PORT}")
except Exception as e:
    print(f"Error connecting to ESP32: {e}")
    exit(1)

def read_esp32_data():
    """Read data from ESP32 serial port"""
    try:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').strip()
            if line.startswith('{'):
                return json.loads(line)
    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"Error reading data: {e}")
    return None

def save_to_fall_events(data):
    """Save ESP32 data to fall_events.json"""
    filepath = "../data/fall_events.json"
    
    # Load existing data
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            all_data = json.load(f)
    else:
        all_data = []
    
    # Add timestamp
    data['timestamp'] = datetime.now().isoformat()
    
    # Add new data
    all_data.append(data)
    
    # Keep only last 1000 records to prevent file from getting too large
    if len(all_data) > 1000:
        all_data = all_data[-1000:]
    
    # Save back
    with open(filepath, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    return data

def main():
    print("ESP32 Fall Detection Integration Started")
    print("Reading from ESP32...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            data = read_esp32_data()
            
            if data:
                # Save to your fall_events.json
                saved_data = save_to_fall_events(data)
                
                # Print status
                if saved_data.get('fall_detected'):
                    print(f"🚨 FALL ALERT: {saved_data['activity']} - Magnitude: {saved_data['magnitude']:.2f}g")
                else:
                    print(f"✅ Normal: Magnitude={saved_data['magnitude']:.2f}g, Activity={saved_data['activity']}")
            
            time.sleep(0.1)  # Small delay
            
    except KeyboardInterrupt:
        print("\nStopping...")
        arduino.close()
        print("Disconnected from ESP32")

if __name__ == "__main__":
    main()
```

---

## 🎯 **What To Do With The Python Code? (Simple Explanation)**

### **Think of it like this:**

1. **📖 The Markdown File (`.md`)** = Like a **recipe book**
   - Shows you examples
   - Explains how things work
   - You **read** it, but don't run it

2. **🐍 The Python File (`esp32_reader.py`)** = Like the **actual cooking**
   - This is the **real file** you run
   - It's already created for you!
   - You **run** this file

### **What You Actually Need To Do:**

**Step 1:** Open `esp32_reader.py` (the real file, not the markdown!)

**Step 2:** Find this line:
```python
ESP32_PORT = 'COM3'  # ⚠️ CHANGE THIS to your ESP32 port
```

**Step 3:** Change `'COM3'` to your ESP32's port (like `'COM4'` or `'COM5'`)

**Step 4:** Save the file

**Step 5:** Run it:
```bash
python esp32_reader.py
```

### **That's It! 🎉**

You **don't need to copy** the code from the markdown file. The actual working file (`esp32_reader.py`) is already ready to use!

---

## Setup Instructions

### 1. Install ESP32 Board Support in Arduino IDE

1. Open Arduino IDE
2. Go to **File → Preferences**
3. Add this URL to **Additional Board Manager URLs**:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Go to **Tools → Board → Boards Manager**
5. Search for "ESP32" and install "esp32 by Espressif Systems"
6. Select **Tools → Board → ESP32 Dev Module**

### 2. Install Required Libraries

In Arduino IDE, go to **Sketch → Include Library → Manage Libraries** and install:
- **Wire** (usually built-in)
- **WiFi** (usually built-in)

### 3. Upload Code to ESP32

1. Connect ESP32 to computer via USB
2. Select correct COM port: **Tools → Port → COM3** (or your port)
3. Click **Upload**
4. Open **Serial Monitor** (115200 baud) to see data

### 4. Install Python Dependencies

```bash
pip install pyserial
```

### 5. Find ESP32 Port

**Windows:**
- Device Manager → Ports (COM & LPT) → Look for "USB Serial Port" or "CP210x"
- Usually COM3, COM4, etc.

**Mac/Linux:**
```bash
ls /dev/tty.* | grep usb
# or
ls /dev/ttyACM*
```

### 6. Run Python Integration

```bash
# Edit ESP32_PORT in the Python script first!
python esp32_reader.py
```

## Adjusting Thresholds

Customize these values in the ESP32 code based on your testing:

```cpp
#define FALL_THRESHOLD 2.5      // g-force above this indicates potential fall
#define IMPACT_THRESHOLD 3.0    // g-force above this indicates impact
#define FREE_FALL_THRESHOLD 0.3 // g-force below this indicates free fall
#define SAMPLING_RATE 100       // Check every 100ms
```

## Testing

1. **Normal Movement:** Walk around - should show "NORMAL" activity
2. **Shake Test:** Shake the sensor - should detect high magnitude
3. **Drop Test:** Drop the sensor (carefully!) - should trigger FALL_IMPACT
4. **Free Fall:** Let sensor fall freely - should detect FREE_FALL

## Complete Integration Flow

### How ESP32 Data Reaches Your Agent

Here's the complete data flow from ESP32 to your fall detection agent:

```
ESP32 (Hardware)
    ↓
    Sends JSON data via Serial (USB)
    ↓
Python Script (esp32_reader.py)
    ↓
    Reads serial data
    Adds timestamp
    ↓
data/fall_events.json
    ↓
    File is updated with new data
    ↓
Fall Detection Agent (fall_detection_agent.py)
    ↓
    Reads fall_events.json every 2 seconds
    Checks for new records
    Processes accelerometer data
    Detects falls based on thresholds
    ↓
data/escalation.json
    ↓
    Alerts are saved here
    ↓
Main System / Dashboard
    ↓
    Reads escalation.json
    Displays alerts to caregivers
```

### Step-by-Step Integration

#### Step 1: ESP32 Sends Data
ESP32 continuously sends JSON data via Serial:
```json
{"timestamp":12345,"x":0.123,"y":-0.456,"z":1.234,"magnitude":1.345,"activity":"NORMAL","fall_detected":false,"alert_level":"NONE","device_id":"esp32_fall_sensor_001"}
```

#### Step 2: Python Script Receives & Saves
The Python script (`esp32_reader.py`) runs continuously:
- Reads data from ESP32 serial port
- Adds ISO timestamp
- Saves to `data/fall_events.json`

**File location:** `data/fall_events.json`
```json
[
  {
    "timestamp": "2025-10-14T13:24:40.047170",
    "x": 0.123,
    "y": -0.456,
    "z": 1.234,
    "magnitude": 1.345,
    "activity": "NORMAL",
    "fall_detected": false,
    "alert_level": "NONE",
    "device_id": "esp32_fall_sensor_001"
  },
  {
    "timestamp": "2025-10-14T13:24:40.547170",
    "x": -3.2,
    "y": 2.8,
    "z": 4.1,
    "magnitude": 5.8,
    "activity": "FALL_IMPACT",
    "fall_detected": true,
    "alert_level": "HIGH",
    "device_id": "esp32_fall_sensor_001"
  }
]
```

#### Step 3: Fall Detection Agent Processes Data
Your `fall_detection_agent.py` runs continuously:
- Reads `data/fall_events.json` every 2 seconds
- Checks for new records (tracks how many it has seen)
- For each new record:
  - Extracts `magnitude` and `activity`
  - Checks if `magnitude > 2.5g` (FALL_THRESHOLD)
  - Checks if `activity` is `FALL_IMPACT` or `FALL_DROP`
  - Creates alert if fall detected

**Agent Code Logic:**
```python
# Agent reads fall_events.json
fall_data = load_json("../data/fall_events.json")

# Processes new records
for accelerometer in new_records:
    magnitude = accelerometer.get('magnitude', 0)
    activity = accelerometer.get('activity', '')
    
    # Check for fall
    if magnitude > FALL_THRESHOLD:
        if activity in ['FALL_IMPACT', 'FALL_DROP']:
            # Create alert
            alert = {
                "type": "fall",
                "parameter": "magnitude",
                "value": magnitude,
                "message": f"Fall detected! Magnitude: {magnitude:.2f}g, Activity: {activity}",
                "time": datetime.now().isoformat(),
                "severity": "HIGH" if magnitude > IMPACT_THRESHOLD else "MEDIUM"
            }
            save_alert(alert)  # Saves to escalation.json
```

#### Step 4: Alerts Saved to Escalation File
When a fall is detected, alert is saved to `data/escalation.json`:

**File location:** `data/escalation.json`
```json
{
  "alerts": [
    {
      "type": "fall",
      "parameter": "magnitude",
      "value": 5.8,
      "message": "Fall detected! Magnitude: 5.80g, Activity: FALL_IMPACT",
      "time": "2025-10-14T13:24:41.123456",
      "severity": "HIGH"
    }
  ]
}
```

#### Step 5: Main System / Dashboard Reads Alerts
Other parts of your system (Person C's dashboard, emergency agent) read `escalation.json` to:
- Display alerts to caregivers
- Trigger emergency responses
- Show in real-time dashboard

### How to Run the Complete System

#### Terminal 1: ESP32 Python Reader
```bash
cd fall_detection_agent
python esp32_reader.py
```
**What it does:**
- Connects to ESP32 via serial
- Reads accelerometer data
- Saves to `data/fall_events.json`
- Prints status to console

#### Terminal 2: Fall Detection Agent
```bash
cd fall_detection_agent
python fall_detection_agent.py
```
**What it does:**
- Reads `data/fall_events.json` every 2 seconds
- Processes new accelerometer data
- Detects falls
- Saves alerts to `data/escalation.json`
- Prints alerts to console

### Example Output Flow

**ESP32 Console:**
```
ESP32 Fall Detection System Started
Monitoring for falls...
{"timestamp":12345,"x":0.123,"y":-0.456,"z":1.234,"magnitude":1.345,"activity":"NORMAL","fall_detected":false,"alert_level":"NONE","device_id":"esp32_fall_sensor_001"}
{"timestamp":12350,"x":-3.2,"y":2.8,"z":4.1,"magnitude":5.8,"activity":"FALL_IMPACT","fall_detected":true,"alert_level":"HIGH","device_id":"esp32_fall_sensor_001"}
FALL_DETECTED: Person has fallen!
```

**Python Reader Console:**
```
Connected to ESP32 on COM3
ESP32 Fall Detection Integration Started
Reading from ESP32...
✅ Normal: Magnitude=1.35g, Activity=NORMAL
🚨 FALL ALERT: FALL_IMPACT - Magnitude: 5.80g
```

**Fall Detection Agent Console:**
```
Fall Detection Agent started...
Monitoring accelerometer data from: ../data/fall_events.json
Alerts will be saved to: ../data/escalation.json
==================================================
Checking movement: X=0.123, Y=-0.456, Z=1.234, Mag=1.345, Activity=NORMAL
Normal movement detected
Checking movement: X=-3.200, Y=2.800, Z=4.100, Mag=5.800, Activity=FALL_IMPACT
FALL ALERT: Fall detected! Magnitude: 5.80g, Activity: FALL_IMPACT at 2025-10-14T13:24:41.123456
```

### File Structure

```
multi_agent_healthcare_system/
├── data/
│   ├── fall_events.json          ← ESP32 data saved here (by Python script)
│   └── escalation.json           ← Alerts saved here (by fall_detection_agent.py)
├── fall_detection_agent/
│   ├── esp32_reader.py           ← Reads ESP32, saves to fall_events.json
│   ├── fall_detection_agent.py   ← Reads fall_events.json, creates alerts
│   └── arduino_ultrasonic_fall_detection.md
```

### Key Points

1. **ESP32 → Python Script → fall_events.json**
   - ESP32 sends data via Serial
   - Python script receives and saves to JSON file

2. **fall_events.json → Fall Detection Agent**
   - Agent reads this file every 2 seconds
   - Processes new records only (tracks what it has seen)

3. **Agent → escalation.json**
   - When fall detected, creates alert
   - Saves alert to escalation.json

4. **escalation.json → Main System**
   - Dashboard reads this file
   - Emergency agent reads this file
   - Alerts displayed to caregivers

### Testing the Integration

1. **Upload ESP32 code** and open Serial Monitor
2. **Run Python reader:** `python esp32_reader.py`
3. **Run fall detection agent:** `python fall_detection_agent.py`
4. **Shake/drop ESP32** to trigger fall detection
5. **Check files:**
   - `data/fall_events.json` - Should have ESP32 data
   - `data/escalation.json` - Should have alerts if fall detected

### Troubleshooting Integration

- **No data in fall_events.json:** Check Python script is running and ESP32 is connected
- **Agent not detecting falls:** Check thresholds match ESP32 output
- **No alerts in escalation.json:** Check agent is running and processing data
- **Data format mismatch:** Ensure ESP32 JSON matches what agent expects

## Integration with Your System

The ESP32 data flows automatically through this pipeline:
1. ESP32 hardware → Serial output
2. Python script → `data/fall_events.json`
3. Fall detection agent → Processes and creates alerts
4. Alerts → `data/escalation.json`
5. Main system → Reads alerts for dashboard/emergency response

## Troubleshooting

- **No data from ESP32:** Check COM port, baud rate (115200), and wiring
- **False alerts:** Increase `FALL_THRESHOLD` value
- **Missed falls:** Decrease `FALL_THRESHOLD` value
- **MPU6050 not detected:** Check I2C wiring (SDA/SCL) and 3.3V power
- **Serial errors:** Ensure baud rate matches (115200)

## ESP32 Advantages

- ✅ Built-in WiFi (can send data wirelessly)
- ✅ More processing power than Arduino
- ✅ Lower power consumption
- ✅ Better for IoT applications
- ✅ Can run multiple tasks simultaneously

## Next Steps

1. Upload code to ESP32
2. Test with Serial Monitor
3. Run Python integration script
4. Verify data appears in `fall_events.json`
5. Your fall detection agent will process the data automatically!