from reminder_agent.reminder_agent import add_sample_reminders, get_all_reminders, check_reminders
from emergency_agent.emergency_agent import detect_emergency

def main():
    # 1️⃣ Add sample reminders to the database
    add_sample_reminders()  # <--- put it here

    # 2️⃣ Fetch reminders for dashboard and emergency agent
    all_reminders = get_all_reminders()
    due_reminders = check_reminders()

    # 3️⃣ Placeholder data from other agents
    health_data = {"critical_vitals": False}  
    fall_data = {"fall_detected": False}      
    cognitive_data = {"risk_flag": False}     
    emotion_data = {"stress_high": False}     

    # 4️⃣ Combine data for emergency agent
    combined_data = {
        "health": health_data,
        "fall": fall_data,
        "cognitive": cognitive_data,
        "emotion": emotion_data,
        "reminders": due_reminders
    }

    # 5️⃣ Check emergencies
    emergency_alerts = detect_emergency(combined_data)

    # 6️⃣ Print outputs
    print("All Reminders:", all_reminders)
    print("Emergency Alerts:", emergency_alerts)

if __name__ == "__main__":
    main()
