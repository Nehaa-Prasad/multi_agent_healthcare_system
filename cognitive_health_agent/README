🧠 Elderly Care Cognitive Chatbot

This project is a Flask-based web chatbot designed to help assess cognitive function in elderly individuals through interactive, speech-enabled conversations.
It dynamically asks questions across multiple cognitive domains such as orientation, attention, memory, and language, and generates a simple assessment summary with scoring.

🚀 Features

🗣️ Voice Input & Output – Uses browser speech recognition and text-to-speech.

🤖 Dynamic Question Flow – Randomized questions across multiple categories.

🧮 Auto Scoring – Simple scoring logic based on keyword matching.

📊 Assessment Summary – Displays and downloads results as a JSON file.

🧭 Categories:

Orientation

Attention

Memory

Language

🛠️ Tech Stack

Backend: Flask (Python)

Frontend: HTML, CSS, JavaScript

Speech API: Web Speech API (browser-based)

Data Storage: Session-based state management

📥 Installation & Setup

Clone this repository:

git clone https://github.com/your-username/elderly-care-cognitive-chatbot.git
cd elderly-care-cognitive-chatbot


Create a virtual environment & activate it:

python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate


Install dependencies:

pip install flask


Run the server:

python app.py


Open in browser:

http://127.0.0.1:5000

📝 How It Works

The chatbot asks the user cognitive questions one by one.

The user can answer by typing or using voice input.

Each answer is scored based on predefined keywords.

Once all questions are completed, a JSON file with the scores and summary is downloaded.

The summary indicates if the cognitive performance is within normal range or if follow-up is advised.

🧾 Example Output
{
  "scores": {
    "orientation": 2,
    "attention": 1,
    "memory": 2,
    "language": 1
  },
  "total": 6,
  "history": [
    "What is today's date?",
    "Can you spell the word 'WORLD' backwards?",
    "What did you do yesterday?",
    "Repeat this phrase: 'No ifs, ands, or buts.'"
  ],
  "summary_text": "Assessment Summary:\nTotal Score: 6\nScores by category:\n - orientation: 2\n - attention: 1\n - memory: 2\n - language: 1\nInterpretation: Normal cognitive performance."
}

⚠️ Disclaimer

This is a prototype designed for educational and research purposes.
It does not replace professional clinical assessment or diagnosis. Always consult a qualified healthcare provider for medical concerns.

🤝 Contributing

Contributions, suggestions, and improvements are welcome.
Feel free to open issues or submit pull requests!
