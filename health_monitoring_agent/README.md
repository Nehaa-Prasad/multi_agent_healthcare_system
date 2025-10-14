# Health Monitoring Agent

## Overview
Monitors vital signs data and creates alerts when values exceed safe thresholds.

## How to Run

### 1. Generate Health Data
```bash
cd health_monitoring_agent
python health_simulator.py
```
Choose option:
- 1 = Single reading
- 2 = 10-second simulation  
- 3 = 1-minute simulation

### 2. Run Health Monitor Agent
```bash
python health_monitor_agent.py
```

## What It Does
- Reads data from `../data/vitals_stream.json`
- Checks vitals against safe ranges:
  - Heart Rate: 60-100 BPM
  - Blood Pressure: 90-120/60-80 mmHg
  - Oxygen Saturation: 94-100%
  - Temperature: 36.0-37.5°C
- Creates alerts for abnormal values
- Saves alerts to `../data/escalation.json`

## Output
- Console: Shows vitals being checked and alerts
- File: `../data/escalation.json` contains all alerts

## Example Alert
```json
{
  "type": "health",
  "parameter": "heart_rate", 
  "value": 120,
  "message": "Abnormal heart_rate: 120",
  "time": "2025-10-14T11:05:32.456Z"
}
```
