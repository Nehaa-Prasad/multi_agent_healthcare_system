# emergency_agent.py

# Placeholder imports – replace with actual imports when available
# from health_monitoring_agent.health_agent import get_health_data
# from fall_detection_agent.fall_agent import check_fall
# from cognitive_health_agent.cognitive_agent import check_cognitive_risk
# from emotional_wellbeing_agent.emotion_agent import check_emotion_risk
# from reminder_agent.reminder_agent import get_due_reminders

def detect_emergency(data):
    """
    data = {
        "health": {...},
        "fall": {...},
        "cognitive": {...},
        "emotion": {...},
        "reminders": {...}   # optional
    }
    Returns: alerts as dict/json
    """
    alerts = []

    # Example logic for emergency
    if data["health"].get("critical_vitals"):
        alerts.append("Critical health alert!")

    if data["fall"].get("fall_detected"):
        alerts.append("Fall detected!")

    if data["cognitive"].get("risk_flag"):
        alerts.append("Cognitive risk alert!")

    if data["emotion"].get("stress_high"):
        alerts.append("High stress alert!")

    # Optional: missed reminders
    due_reminders = data.get("reminders", [])
    for rem in due_reminders:
        alerts.append(f"Missed reminder: {rem['title']}")

    return {"alerts": alerts}


if __name__ == "__main__":
    # Sample test data
    sample_data = {
        "health": {"critical_vitals": True},
        "fall": {"fall_detected": False},
        "cognitive": {"risk_flag": False},
        "emotion": {"stress_high": True},
        "reminders": [{"title": "Take Medicine"}]
    }

    result = detect_emergency(sample_data)
    print(result)
