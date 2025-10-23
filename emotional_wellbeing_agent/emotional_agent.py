from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
from datetime import datetime
import random, os

app = Flask(__name__)
app.secret_key = "offline_emotion_agent"
socketio = SocketIO(app)

# --- Rule-based emotion detection ---
EMOTION_PATTERNS = {
    "happy": ["happy","glad","joy","excited","good","great","fantastic","awesome","wonderful","amazing"],
    "sad": ["sad","down","unhappy","depressed","blue","not good","not great","terrible","bad","nothing","miserable"],
    "anxious": ["anxious","worried","nervous","stress","overwhelmed","stressed"],
    "angry": ["angry","mad","frustrated","annoyed","irritated"],
    "lonely": ["lonely","alone","isolated","neglected"],
}

# --- Points for scoring ---
EMOTION_POINTS = {
    "happy": 2,
    "neutral": 1,
    "sad": 0,
    "anxious": 0,
    "angry": 0,
    "lonely": 0,
    "unknown": 0
}

# --- Supportive messages ---
SUPPORTIVE_RESPONSES = {
    "happy": ["That’s wonderful! Can you share what made you feel happy?", "Love hearing your positivity!"],
    "sad": ["I’m sorry you feel sad. Talking helps, would you like to share more?", "It’s okay to feel down sometimes."],
    "anxious": ["Take a deep breath. Want to try a short calming exercise?", "You’re safe here. Let's relax together."],
    "angry": ["It’s okay to feel upset. Take a moment to breathe.", "Try counting to 10 slowly."],
    "lonely": ["You are not alone. Want ideas to connect with someone?", "It helps to reach out to a friend."],
    "neutral": ["Thanks for sharing. How has your day been?", "Got it. Would you like a tip to feel better?"],
    "unknown": ["I didn’t quite catch that. Can you describe your feelings more?"]
}

# --- Load RAG tips ---
KNOWLEDGE_FILE = "knowledge/wellbeing_tips.txt"
def load_knowledge():
    if not os.path.exists(KNOWLEDGE_FILE):
        return []
    with open(KNOWLEDGE_FILE,"r",encoding="utf-8",errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]
WELLBEING_TIPS = load_knowledge()

def classify_emotion(text):
    text = text.lower()
    for emo, keywords in EMOTION_PATTERNS.items():
        for word in keywords:
            if word in text:
                return emo
    if "not happy" in text or "not good" in text or "not great" in text:
        return "sad"
    return "neutral"

def get_rag_tip(emotion):
    tips = [t for t in WELLBEING_TIPS if f"[{emotion}]" in t.lower()]
    if tips:
        return random.choice(tips)
    return random.choice(WELLBEING_TIPS) if WELLBEING_TIPS else None

# --- Routes ---
@app.route("/")
def index():
    session["state"] = {"turns": [], "emotion_counts": {}, "started_at": datetime.utcnow().isoformat()+"Z"}
    return render_template("index.html")

# --- Real-time chat ---
@socketio.on("user_message")
def handle_message(data):
    user_text = data.get("message","").strip()
    if not user_text:
        emit("bot_message", {"reply":"Can you tell me how you're feeling?"})
        return

    emotion = classify_emotion(user_text)
    bot_reply = random.choice(SUPPORTIVE_RESPONSES.get(emotion,SUPPORTIVE_RESPONSES["unknown"]))
    tip = get_rag_tip(emotion)

    state = session.get("state", {"turns": [], "emotion_counts": {}})
    turn = {
        "timestamp": datetime.utcnow().isoformat()+"Z",
        "user": user_text,
        "emotion": emotion,
        "bot": bot_reply,
        "tip": tip
    }
    state["turns"].append(turn)
    state["emotion_counts"][emotion] = state["emotion_counts"].get(emotion,0)+1
    session["state"] = state

    emit("bot_message", {"reply": bot_reply, "suggestion": tip})

# --- Finish session ---
@socketio.on("finish_session")
def finish():
    s = session.get("state", {"turns": [], "emotion_counts": {}, "started_at": datetime.utcnow().isoformat()+"Z"})
    turns = s.get("turns", [])
    counts = s.get("emotion_counts", {})

    total_score = sum(EMOTION_POINTS.get(turn["emotion"],0) for turn in turns)
    max_score = len(turns)*2
    if max_score==0:
        interpretation="No data to evaluate."
    else:
        ratio = total_score/max_score
        if ratio>=0.75: interpretation="Mostly positive mood detected."
        elif ratio>=0.4: interpretation="Mixed or balanced mood detected."
        else: interpretation="More negative emotions detected — consider support or follow-up."

    summary = f"Session Summary:\nTotal turns: {len(turns)}\n"
    for emo,val in counts.items():
        summary+=f" - {emo}: {val}\n"
    summary+=f"Total Well-being Score: {total_score}/{max_score}\n"
    summary+=f"Interpretation: {interpretation}"

    result = {
        "started_at": s.get("started_at"),
        "ended_at": datetime.utcnow().isoformat()+"Z",
        "turns": turns,
        "emotion_counts": counts,
        "total_score": total_score,
        "max_score": max_score,
        "interpretation": interpretation,
        "summary_text": summary
    }

    session.pop("state", None)
    emit("session_finished", result)

if __name__=="__main__":
    socketio.run(app, debug=True)
