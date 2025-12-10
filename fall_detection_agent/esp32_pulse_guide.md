# ESP32 Pulse Sensor (Heart Rate) Guide

## What this is
- ESP32 + pulse sensor (PulseSensor / KY-039 style) → sends BPM over Serial in JSON.
- Python reader saves BPM into `data/vitals_stream.json`.
- Your `health_monitor_agent.py` can alert on low/high BPM.

## Wiring (Pulse Sensor → ESP32)
```
Pulse VCC     → 3.3V
Pulse GND     → GND
Pulse Signal  → GPIO 34  (ADC input)
```

## ESP32 Code (copy/paste into Arduino IDE)
```cpp
/*
 * ESP32 Pulse Sensor Reader
 * Reads pulse on analog pin and outputs BPM via Serial in JSON
 */

const int PULSE_PIN = 34;      // Analog pin for pulse sensor
const int SAMPLE_RATE = 10;    // ms between samples (100 Hz)
const int WINDOW_MS = 10000;   // Rolling window for BPM (10 seconds)

// Peak detection thresholds (tune for your sensor)
const int THRESHOLD_HIGH = 520;  // Adjust based on your sensor/noise
const int THRESHOLD_LOW  = 500;  // Hysteresis to avoid double-counting

unsigned long lastSample = 0;
unsigned long windowStart = 0;
int signalValue = 0;
bool beatInProgress = false;
int beatCount = 0;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);       // 0-4095
  analogSetAttenuation(ADC_11db); // Wider voltage range
  windowStart = millis();
  Serial.println("ESP32 Pulse Sensor Started");
}

void loop() {
  unsigned long now = millis();

  // Sample at fixed rate
  if (now - lastSample >= SAMPLE_RATE) {
    lastSample = now;
    signalValue = analogRead(PULSE_PIN);

    // Simple peak detection
    if (!beatInProgress && signalValue > THRESHOLD_HIGH) {
      beatInProgress = true;
      beatCount++;
    }
    if (beatInProgress && signalValue < THRESHOLD_LOW) {
      beatInProgress = false;
    }
  }

  // Compute BPM every WINDOW_MS
  if (now - windowStart >= WINDOW_MS) {
    float bpm = (beatCount * 60000.0) / (now - windowStart);

    // Output JSON line for Python
    Serial.print("{\"timestamp\":");
    Serial.print(now);
    Serial.print(",\"bpm\":");
    Serial.print(bpm, 1);
    Serial.print(",\"raw\":");
    Serial.print(signalValue);
    Serial.println(",\"device_id\":\"esp32_pulse_001\"}");

    // Reset window
    beatCount = 0;
    windowStart = now;
  }
}
```

## Upload steps (Arduino IDE)
1) Install ESP32 boards (Boards Manager URL: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`)
2) Board: **ESP32 Dev Module**
3) Port: your ESP32 COM port
4) Paste code above → Upload
5) Serial Monitor @ 115200 → you should see JSON with `bpm`

## Python Reader (saves BPM to vitals_stream.json)
Create `pulse_reader.py` in `fall_detection_agent/`:

```python
import serial, json, time, os
from datetime import datetime

ESP32_PORT = "COM3"   # CHANGE to your port
BAUD = 115200
OUTFILE = "../data/vitals_stream.json"  # health agent reads this

ser = serial.Serial(ESP32_PORT, BAUD, timeout=1)
time.sleep(2)
print(f"Connected to {ESP32_PORT}")

while True:
    try:
        line = ser.readline().decode().strip()
        if not line.startswith("{"):
            continue
        data = json.loads(line)
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

        print(f"BPM={data.get('bpm')}")
    except KeyboardInterrupt:
        break
    except Exception:
        pass
```

Run it:
```bash
cd fall_detection_agent
python pulse_reader.py
```
This writes BPM records into `data/vitals_stream.json`.

## How it connects to your agent
- Pulse reader → `data/vitals_stream.json`
- `health_monitor_agent.py` already reads this file.
- If you want alerts on pulse, add a BPM check there (e.g., alert if BPM < 50 or > 120).

## Quick checklist
- Wire pulse sensor to ESP32 (signal → GPIO 34).
- Upload the ESP32 code above.
- Change COM port in `pulse_reader.py`, run it.
- Run `health_monitor_agent.py` to consume the BPM data.


