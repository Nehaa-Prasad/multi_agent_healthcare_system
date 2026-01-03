from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
from datetime import datetime
import random, os

# -----------------------------
# APP SETUP (MAC SAFE)
# -----------------------------
app = Flask(__name__)
app.secret_key = "offline_emotion_agent"

# IMPORTANT: async_mode must be set explicitly for macOS
socketio = SocketIO(
    app,
    async_mode="threading",   # <-- KEY FIX
    cors_allowed_origins="*",
    manage_session=True
)

# -----------------------------
# RULE-BASED EMOTION DETECTION
# -----------------------------
EMOTION_PATTERNS = {
    "happy": ["happy","glad","joy","excited","good","great","fantastic","awesome","wonderful","amazing"],
    "sad": ["sad","down","unhappy","depressed","blue","terrible","bad","miserable"],
    "anxious": ["anxious","worried","nervous","stress","overwhelmed","stressed"],
    "angry": ["angry","mad","frustrated","annoyed","irritated"],
    "lonely": ["lonely","alone","isolated","neglected"],
}

EMOTION_POINTS = {
    "happy": 2,
    "neutral": 1,
    "sad": 0,
    "anxious": 0,
    "angry": 0,
    "lonely": 0,
    "unknown": 0
}

SUPPORTIVE_RESPONSES = {
    "happy": ["That’s wonderful! What made you feel happy today?"],
    "sad": ["I’m sorry you feel sad. Want to talk about it?"],
    "anxious": ["Take a deep breath. You’re safe here."],
    "angry": ["It’s okay to feel angry. Let’s pause for a moment."],
    "lonely": ["You’re not alone. I’m here with you."],
    "neutral": ["Thanks for sharing. How has your day been?"],
    "unknown": ["Could you tell me a bit more about how you feel?"]
}

# -----------------------------
# LOAD KNOWLEDGE BASE
# -----------------------------
KNOWLEDGE_FILE = "knowledge/wellbeing_tips.txt"

def load_knowledge():
    if not os.path.exists(KNOWLEDGE_FILE):
        return []
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

WELLBEING_TIPS = load_knowledge()

# -----------------------------
# CORE LOGIC
# -----------------------------
def classify_emotion(text):
    text = text.lower()
    for emo, keywords in EMOTION_PATTERNS.items():
        for word in keywords:
            if word in text:
                return emo
    return "neutral"

def get_rag_tip(emotion):
    tips = [t for t in WELLBEING_TIPS if f"[{emotion}]" in t.lower()]
    return random.choice(tips) if tips else None

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def index():
    session["state"] = {
        "turns": [],
        "emotion_counts": {},
        "started_at": datetime.utcnow().isoformat() + "Z"
    }
    return render_template("index.html")

# -----------------------------
# SOCKET EVENTS
# -----------------------------
@socketio.on("user_message")
def handle_message(data):
    user_text = data.get("message", "").strip()
    if not user_text:
        emit("bot_message", {"reply": "Can you tell me how you're feeling?"})
        return

    emotion = classify_emotion(user_text)
    bot_reply = random.choice(SUPPORTIVE_RESPONSES.get(emotion))
    tip = get_rag_tip(emotion)

    state = session.get("state", {"turns": [], "emotion_counts": {}})
    state["turns"].append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user": user_text,
        "emotion": emotion,
        "bot": bot_reply,
        "tip": tip
    })
    state["emotion_counts"][emotion] = state["emotion_counts"].get(emotion, 0) + 1
    session["state"] = state

    emit("bot_message", {"reply": bot_reply, "suggestion": tip})

@socketio.on("finish_session")
def finish_session():
    s = session.get("state", {})
    turns = s.get("turns", [])
    counts = s.get("emotion_counts", {})

    total_score = sum(EMOTION_POINTS.get(t["emotion"], 0) for t in turns)
    max_score = len(turns) * 2

    interpretation = (
        "Mostly positive mood detected." if max_score and total_score / max_score >= 0.75
        else "Mixed emotional state detected." if max_score and total_score / max_score >= 0.4
        else "More negative emotions detected." if turns
        else "No data to evaluate."
    )

    emit("session_finished", {
        "turns": turns,
        "emotion_counts": counts,
        "total_score": total_score,
        "max_score": max_score,
        "interpretation": interpretation
    })

    session.pop("state", None)

# -----------------------------
# ENTRY POINT (MAC SAFE)
# -----------------------------
if __name__ == "__main__":
    socketio.run(
        app,
        host="localhost",        # IMPORTANT
        port=5000,               # FIXED PORT
        debug=False,
        use_reloader=False,      # VERY IMPORTANT FOR MAC
        allow_unsafe_werkzeug=True
    )

