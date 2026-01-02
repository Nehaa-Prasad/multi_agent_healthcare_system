# ESP32 Fall Detection System using Accelerometer

## 🚀 Quick Start - What Files Do I Use?

**Confused about which file to use? Here's the simple answer:**

| File | What It Is | What To Do |
|------|-----------|-----------|
| `esp32_fall_detection_guide.md` | 📖 **Documentation** (this file) | **Read it** - explains fall + integration |
| `esp32_pulse_guide.md` | 📖 Pulse sensor doc | **Read it** - heart-rate setup |
| `esp32_reader.py` | 🐍 **Actual Python code** | **Run this!** - connects ESP32 fall sensor |
| `pulse_reader.py` | 🐍 **Python code** | **Run this!** - connects ESP32 pulse sensor |

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

// esp32_combined_fixed.ino
#include <Wire.h>
#include <math.h>

// ---------------- MPU6050 DEFINITIONS ----------------
#define MPU6050_ADDR          0x68
#define MPU6050_ACCEL_XOUT_H  0x3B
#define MPU6050_PWR_MGMT_1    0x6B
#define MPU6050_SMPLRT_DIV    0x19
#define MPU6050_CONFIG        0x1A
#define MPU6050_ACCEL_CONFIG  0x1C

// ---------------- PIN DEFINITIONS ----------------
#define SDA_PIN     21
#define SCL_PIN     22
#define BUZZER_PIN  2
#define PULSE_PIN   34   // ADC input only (ESP32)

// ---------------- TIMINGS ----------------
const unsigned long MPU_SAMPLE_MS = 3000;
const unsigned long BPM_WINDOW_MS = 10000;
const unsigned long MPU_RETRY_MS  = 5000;

// ---------------- FALL THRESHOLDS ----------------
const float FALL_THRESHOLD       = 2.5;
const float IMPACT_THRESHOLD     = 3.0;
const float FREE_FALL_THRESHOLD  = 0.3;

// ---------------- MOVING AVERAGE ----------------
const int AVG_SIZE = 5;
float ax_buf[AVG_SIZE] = {0}, ay_buf[AVG_SIZE] = {0}, az_buf[AVG_SIZE] = {0};
int buf_idx = 0;

// ---------------- GLOBAL STATE ----------------
float accelX = 0, accelY = 0, accelZ = 0;
float magnitude = 0;
bool fallDetected = false;
bool mpuPresent = false;

unsigned long lastMpuSample = 0;
unsigned long lastMpuTry = 0;

// ---------------- PULSE SENSOR ----------------
unsigned long lastSample = 0;
unsigned long bpmWindowStart = 0;
int beatCount = 0;
bool beatInProgress = false;
int rawSignal = 0;

const unsigned long SAMPLE_MS = 10;
const int THRESHOLD_HIGH = 520;
const int THRESHOLD_LOW  = 500;

// ---------------- FUNCTION DECLARATIONS ----------------
void setupMPU();
bool readMPU();
bool detectFall();
void triggerFallAlert();
void sendJSONtoSerial(float bpm);

// ================== SETUP ==================
void setup() {
  Serial.begin(115200);

  // IMPORTANT FIX: Explicit I2C pins
  Wire.begin(SDA_PIN, SCL_PIN);
  delay(100);

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);

  bpmWindowStart = millis();

  setupMPU();

  Serial.println("ESP32 combined sensor started");
}

// ================== LOOP ==================
void loop() {
  unsigned long now = millis();

  // ----- MPU SAMPLE -----
  if (now - lastMpuSample >= MPU_SAMPLE_MS) {
    lastMpuSample = now;

    if (!mpuPresent) {
      if (now - lastMpuTry >= MPU_RETRY_MS) {
        lastMpuTry = now;
        setupMPU();
      }
      magnitude = 0;
    } else {
      if (!readMPU()) {
        mpuPresent = false;
        magnitude = 0;
      } else {
        magnitude = sqrt(accelX*accelX + accelY*accelY + accelZ*accelZ);
        if (detectFall()) triggerFallAlert();
      }
    }
  }

  // ----- PULSE SENSOR SAMPLE -----
  if (now - lastSample >= SAMPLE_MS) {
    lastSample = now;
    rawSignal = analogRead(PULSE_PIN);

    if (!beatInProgress && rawSignal > THRESHOLD_HIGH) {
      beatInProgress = true;
      beatCount++;
    } else if (beatInProgress && rawSignal < THRESHOLD_LOW) {
      beatInProgress = false;
    }
  }

  // ----- BPM CALCULATION -----
  if (now - bpmWindowStart >= BPM_WINDOW_MS) {
    float bpm = (beatCount * 60000.0) / (now - bpmWindowStart);
    sendJSONtoSerial(bpm);
    beatCount = 0;
    bpmWindowStart = now;
  }

  delay(1);
}

// ================== MPU FUNCTIONS ==================

void setupMPU() {
  Wire.beginTransmission(MPU6050_ADDR);
  if (Wire.endTransmission() != 0) {
    Serial.println("MPU6050 not found on bus (setup).");
    mpuPresent = false;
    return;
  }

  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_PWR_MGMT_1);
  Wire.write(0x00);
  Wire.endTransmission();

  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_ACCEL_CONFIG);
  Wire.write(0x00);
  Wire.endTransmission();

  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_SMPLRT_DIV);
  Wire.write(0x07);
  Wire.endTransmission();

  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_CONFIG);
  Wire.write(0x06);
  Wire.endTransmission();

  for (int i = 0; i < AVG_SIZE; i++) {
    ax_buf[i] = ay_buf[i] = az_buf[i] = 0;
  }
  buf_idx = 0;

  mpuPresent = true;
  Serial.println("MPU6050 initialized");
}

bool readMPU() {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(MPU6050_ACCEL_XOUT_H);
  if (Wire.endTransmission(false) != 0) return false;

  Wire.requestFrom(MPU6050_ADDR, 14, true);
  if (Wire.available() < 14) return false;

  int16_t ax = (Wire.read() << 8) | Wire.read();
  int16_t ay = (Wire.read() << 8) | Wire.read();
  int16_t az = (Wire.read() << 8) | Wire.read();
  Wire.read(); Wire.read(); // temp
  Wire.read(); Wire.read(); // gyro x
  Wire.read(); Wire.read(); // gyro y
  Wire.read(); Wire.read(); // gyro z

  float rawAx = ax / 16384.0;
  float rawAy = ay / 16384.0;
  float rawAz = az / 16384.0;

  ax_buf[buf_idx] = rawAx;
  ay_buf[buf_idx] = rawAy;
  az_buf[buf_idx] = rawAz;
  buf_idx = (buf_idx + 1) % AVG_SIZE;

  float sx = 0, sy = 0, sz = 0;
  for (int i = 0; i < AVG_SIZE; i++) {
    sx += ax_buf[i];
    sy += ay_buf[i];
    sz += az_buf[i];
  }

  accelX = sx / AVG_SIZE;
  accelY = sy / AVG_SIZE;
  accelZ = sz / AVG_SIZE;

  return true;
}

bool detectFall() {
  if (magnitude > IMPACT_THRESHOLD) return true;

  if (fabs(accelX) < FREE_FALL_THRESHOLD &&
      fabs(accelY) < FREE_FALL_THRESHOLD &&
      fabs(accelZ) < FREE_FALL_THRESHOLD) return true;

  static float prevMag = 0;
  float diff = fabs(magnitude - prevMag);
  prevMag = magnitude;

  if (magnitude > FALL_THRESHOLD && diff > 1.5) return true;

  return false;
}

void triggerFallAlert() {
  if (fallDetected) return;

  fallDetected = true;
  for (int i = 0; i < 3; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(150);
    digitalWrite(BUZZER_PIN, LOW);
    delay(150);
  }
  Serial.println("FALL_DETECTED");
}

// ================== SERIAL JSON ==================

void sendJSONtoSerial(float bpm) {
  Serial.print("{\"timestamp\":"); Serial.print(millis());
  Serial.print(",\"x\":"); Serial.print(accelX, 3);
  Serial.print(",\"y\":"); Serial.print(accelY, 3);
  Serial.print(",\"z\":"); Serial.print(accelZ, 3);
  Serial.print(",\"magnitude\":"); Serial.print(magnitude, 3);
  Serial.print(",\"fall_detected\":"); Serial.print(fallDetected ? "true" : "false");
  Serial.print(",\"bpm\":"); Serial.print(bpm, 1);
  Serial.print(",\"pulse_raw\":"); Serial.print(rawSignal);
  Serial.println("}");
}


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