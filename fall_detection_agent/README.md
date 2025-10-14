# Fall Detection Agent

## Overview
Monitors accelerometer data and detects falls based on movement patterns and impact forces.

## How to Run

### 1. Generate Fall Data
```bash
cd fall_detection_agent
python fall_simulator.py
```
Choose option:
- 1 = Single normal reading
- 2 = Single fall reading (guaranteed alert)
- 3 = Single walking reading
- 4 = Single inactive reading
- 5 = 10-second simulation
- 6 = 1-minute simulation

### 2. Run Fall Detection Agent
```bash
python fall_detection_agent.py
```

## What It Does
- Reads data from `../data/fall_events.json`
- Detects falls when:
  - Magnitude > 2.5g (fall threshold)
  - Activity = FALL_IMPACT or FALL_DROP
- Creates alerts for detected falls
- Saves alerts to `../data/escalation.json`

## Output
- Console: Shows movement data being checked and fall alerts
- File: `../data/escalation.json` contains all alerts

## Example Alert
```json
{
  "type": "fall",
  "parameter": "magnitude",
  "value": 5.37,
  "message": "Fall detected! Magnitude: 5.37g, Activity: FALL_IMPACT",
  "time": "2025-10-14T11:05:32.456Z",
  "severity": "HIGH"
}
```
