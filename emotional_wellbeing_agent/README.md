Emotional Well-being Agent

A real-time, offline chatbot designed to support emotional well-being through conversational check-ins. The agent detects emotions, provides supportive responses, and gives personalized tips. All interactions are stored and exported as a JSON summary with scoring.

Features

Real-time chat using Flask-SocketIO

Voice input via microphone (speech-to-text)

Voice output (text-to-speech) for bot responses

Emotion detection (happy, sad, anxious, angry, lonely, neutral)

Supportive responses tailored to detected emotions

RAG-based tips loaded from a knowledge base file

JSON session output with scores, turn history, and summary

Offline operation (no API keys required)

Installation

Clone the repository:

git clone <repo-url>
cd emotional_agent


Create a virtual environment and activate:

python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows


Install dependencies:

pip install flask flask-socketio


Create the knowledge file:

mkdir knowledge
echo "[happy] Take a moment to appreciate something positive today." > knowledge/wellbeing_tips.txt
echo "[sad] Try writing down your feelings to relieve stress." >> knowledge/wellbeing_tips.txt

Usage

Run the Flask-SocketIO app:

python app.py


Open the browser at:

http://localhost:5000


Use the chatbot:

Type messages or click the 🎤 button to speak.

Listen as the bot responds via text-to-speech.

Click Finish & Get JSON to download the session summary.

Output

The session JSON includes:

{
  "started_at": "2025-10-14T09:30:00Z",
  "ended_at": "2025-10-14T09:40:00Z",
  "turns": [
    {
      "timestamp": "2025-10-14T09:31:00Z",
      "user": "I feel sad today",
      "emotion": "sad",
      "bot": "I’m sorry you feel sad. Talking helps, would you like to share more?",
      "tip": "Try writing down your feelings to relieve stress."
    }
  ],
  "emotion_counts": {"sad":1},
  "total_score": 0,
  "max_score": 2,
  "interpretation": "More negative emotions detected — consider support or follow-up.",
  "summary_text": "Session Summary: ..."
}

Customization

Add more emotion keywords in EMOTION_PATTERNS for better detection.

Update SUPPORTIVE_RESPONSES for richer conversational replies.

Expand knowledge/wellbeing_tips.txt with more RAG-based tips.

Dependencies

Python 3.8+

Flask

Flask-SocketIO

Modern browser with Web Speech API support

License

MIT License – free to use, modify, and share.
