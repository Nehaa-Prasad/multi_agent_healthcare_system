# Arduino Ultrasonic Fall Detection System

## Overview
This document provides Arduino code to detect falls using ultrasonic sensors. The system monitors distance from floor to person and detects sudden drops that indicate falls.

## Hardware Required
- Arduino Uno/Nano
- HC-SR04 Ultrasonic Sensor (for distance measurement)
- MPU6050 Accelerometer/Gyroscope (optional - for additional motion detection)
- Buzzer/LED (for local alert)
- MicroSD Card Shield (optional - for data logging)

## Wiring Diagram

### HC-SR04 Ultrasonic Sensor
```
HC-SR04  →  Arduino
VCC      →  5V
GND      →  GND
Trig     →  Digital Pin 9
Echo     →  Digital Pin 10
```

### MPU6050 (Optional)
```
MPU6050  →  Arduino
VCC      →  5V
GND      →  GND
SCL      →  A5
SDA      →  A4
```

## Arduino Code

```cpp
/* 
 * Arduino Fall Detection System using Ultrasonic Sensor
 * Detects falls by monitoring distance changes and sudden drops
 * Sends data to serial port for Python processing
 */

// Ultrasonic Sensor Pins
#define TRIG_PIN 9
#define ECHO_PIN 10
#define BUZZER_PIN 8

// Thresholds (adjust based on testing)
#define FLOOR_DISTANCE 250    // Normal floor distance in cm
#define FALL_DROP_THRESHOLD 50  // Sudden drop indicating fall (cm)
#define FLOOR_THRESHOLD 20     // Distance to floor when fallen (cm)
#define SAMPLING_RATE 500     // Check every 500ms

// Variables
unsigned long lastCheck = 0;
unsigned int previousDistance = 0;
unsigned int currentDistance = 0;
bool fallDetected = false;

// MPU6050 (if connected)
#ifdef USE_MPU6050
#include <Wire.h>
#include <MPU6050.h>
MPU6050 mpu;
#endif

void setup() {
  Serial.begin(9600);
  
  // Ultrasonic pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Initialize MPU6050 if connected
  #ifdef USE_MPU6050
    Wire.begin();
    mpu.initialize();
    if (mpu.testConnection()) {
      Serial.println("MPU6050 connected");
    }
  #endif
  
  Serial.println("Fall Detection System Started");
  Serial.println("Monitoring for falls...");
  
  // Calibration: Get baseline floor distance
  calibrateFloor();
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Check for falls every SAMPLING_RATE milliseconds
  if (currentMillis - lastCheck >= SAMPLING_RATE) {
    lastCheck = currentMillis;
    
    currentDistance = measureDistance();
    
    // Detect fall patterns
    if (detectFall(currentDistance)) {
      triggerFallAlert();
    }
    
    // Send data to serial port (Python will read this)
    sendDataToSerial(currentDistance);
  }
}

// Measure distance using ultrasonic sensor
unsigned int measureDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH);
  unsigned int distance = (duration * 0.034) / 2; // Convert to cm
  
  return distance;
}

// Detect fall based on distance patterns
bool detectFall(unsigned int distance) {
  // Pattern 1: Sudden large drop (person falling)
  if (previousDistance > FLOOR_DISTANCE && 
      previousDistance - distance > FALL_DROP_THRESHOLD &&
      distance < FLOOR_DISTANCE) {
    return true;
  }
  
  // Pattern 2: Person on floor (below normal height)
  if (distance < FLOOR_THRESHOLD) {
    // Check if person is actually on the ground (not just crouched)
    if (distance < 10 && previousDistance > 30) {
      return true;
    }
  }
  
  previousDistance = distance;
  return false;
}

// Trigger fall alert
void triggerFallAlert() {
  if (!fallDetected) {
    fallDetected = true;
    
    // Visual/Audio alert
    for (int i = 0; i < 5; i++) {
      digitalWrite(BUZZER_PIN, HIGH);
      delay(200);
      digitalWrite(BUZZER_PIN, LOW);
      delay(200);
    }
    
    Serial.println("FALL_DETECTED: Person has fallen!");
    Serial.print("Distance: ");
    Serial.print(currentDistance);
    Serial.println(" cm");
    
    // Optional: Send coordinates (if using multiple sensors)
    sendFallCoordinates(currentDistance);
  }
}

// Send data to Python via Serial
void sendDataToSerial(unsigned int distance) {
  unsigned long timestamp = millis();
  
  #ifdef USE_MPU6050
    // Get accelerometer data
    int16_t ax, ay, az;
    mpu.getAcceleration(&ax, &ay, &az);
    
    // Calculate magnitude
    float magnitude = sqrt(ax*ax + ay*ay + az*az) / 16384.0; // Convert to g-force
    
    // Send JSON format for Python
    Serial.print("{\"timestamp\":");
    Serial.print(timestamp);
    Serial.print(",\"distance\":");
    Serial.print(distance);
    Serial.print(",\"x\":");
    Serial.print(ax / 16384.0);
    Serial.print(",\"y\":");
    Serial.print(ay / 16384.0);
    Serial.print(",\"z\":");
    Serial.print(az / 16384.0);
    Serial.print(",\"magnitude\":");
    Serial.print(magnitude);
    Serial.print(",\"fall_detected\":");
    Serial.print(fallDetected);
    Serial.println("}");
  #else
    // Send simple distance data
    Serial.print("{\"timestamp\":");
    Serial.print(timestamp);
    Serial.print(",\"distance\":");
    Serial.print(distance);
    Serial.print(",\"fall_detected\":");
    Serial.print(fallDetected);
    Serial.println("}");
  #endif
  
  // Reset fall flag after sending
  if (fallDetected) {
    delay(5000); // Wait 5 seconds before allowing new fall detection
    fallDetected = false;
  }
}

// Send fall coordinates (for multiple sensor setups)
void sendFallCoordinates(unsigned int distance) {
  Serial.print("FALL_COORDS:");
  Serial.print("{");
  Serial.print("\"x\":0,");
  Serial.print("\"y\":0,");
  Serial.print("\"z\":");
  Serial.print(distance);
  Serial.print(",\"magnitude\":");
  Serial.print((float)(FLOOR_DISTANCE - distance) / FLOOR_DISTANCE);
  Serial.print(",\"activity\":\"FALL_DETECTED\"");
  Serial.println("}");
}

// Calibrate floor distance on startup
void calibrateFloor() {
  Serial.println("Calibrating floor distance...");
  
  unsigned int totalDistance = 0;
  for (int i = 0; i < 10; i++) {
    totalDistance += measureDistance();
    delay(100);
  }
  
  unsigned int avgDistance = totalDistance / 10;
  
  if (avgDistance > 50 && avgDistance < 400) {
    Serial.print("Floor calibrated at: ");
    Serial.print(avgDistance);
    Serial.println(" cm");
    
    // Update threshold based on calibration
    unsigned int personHeight = avgDistance - 50; // Assume person is ~50cm shorter than ceiling
    FALL_DROP_THRESHOLD = personHeight * 0.6; // Fall if drops 60% of height
  } else {
    Serial.println("Calibration failed. Using defaults.");
  }
}

// Optional: Add button to reset fall detection
void checkResetButton() {
  // Add reset button logic here if needed
}
```

## Python Integration Code

Create a Python script to read from Arduino and integrate with your fall detection system:

```python
import serial
import json
import time
import os

# Arduino connection
arduino = serial.Serial('COM3', 9600)  # Change COM3 to your port
time.sleep(2)  # Wait for Arduino to initialize

def read_arduino_data():
    """Read data from Arduino serial port"""
    try:
        line = arduino.readline().decode('utf-8').strip()
        if line.startswith('{'):
            return json.loads(line)
    except:
        pass
    return None

def save_to_fall_events(data):
    """Save Arduino data to fall_events.json"""
    filepath = "../data/fall_events.json"
    
    # Load existing data
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            all_data = json.load(f)
    else:
        all_data = []
    
    # Add new data
    all_data.append(data)
    
    # Save back
    with open(filepath, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"Data saved: {data}")

def main():
    print("Arduino Fall Detection Integration Started")
    print("Reading from Arduino...")
    
    while True:
        data = read_arduino_data()
        
        if data:
            # Add timestamp
            from datetime import datetime
            data['timestamp'] = datetime.now().isoformat()
            data['device_id'] = 'arduino_fall_sensor_001'
            
            # Save to your fall_events.json
            save_to_fall_events(data)
            
            # Check if fall detected
            if data.get('fall_detected'):
                print(f"FALL ALERT: {data}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()
```

## Setup Instructions

1. **Upload Arduino Code:**
   - Open Arduino IDE
   - Connect Arduino to computer
   - Upload the code above
   - Open Serial Monitor (9600 baud) to see data

2. **Install Python Dependencies:**
```bash
pip install pyserial
```

3. **Find Arduino Port:**
   - Windows: `COM3` or `COM4`
   - Mac/Linux: `/dev/ttyUSB0` or `/dev/ttyACM0`

4. **Run Python Integration:**
```bash
python arduino_reader.py
```

## Adjusting Thresholds

Customize these values based on your setup:

```cpp
#define FLOOR_DISTANCE 250        // Normal standing height (cm)
#define FALL_DROP_THRESHOLD 50    // Sudden drop threshold (cm)
#define FLOOR_THRESHOLD 20        // Distance when fallen (cm)
#define SAMPLING_RATE 500         // Check frequency (ms)
```

## Testing

1. **Normal Movement:** Walk around - should not trigger alerts
2. **Crouch:** Kneel down slowly - should not trigger alert
3. **Simulated Fall:** Crouch quickly then lie down - should trigger alert
4. **Lying Down:** Stay on floor - should trigger alert

## Integration with Your System

The Arduino data will automatically be added to `data/fall_events.json`, which your fall detection agent will process!

## Troubleshooting

- **No distance readings:** Check wiring and sensor orientation
- **False alerts:** Adjust `FALL_DROP_THRESHOLD` higher
- **Missed falls:** Lower `FLOOR_THRESHOLD` value
- **Serial errors:** Check baud rate matches (9600)

## Next Steps

1. Upload code to Arduino
2. Test with serial monitor
3. Run Python integration script
4. Verify data appears in `fall_events.json`
5. Your fall detection agent will process the data automatically!
