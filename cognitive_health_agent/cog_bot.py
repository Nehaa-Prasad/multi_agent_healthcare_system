from flask import Flask, render_template_string, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = "secret123"

# Sample dynamic questions
QUESTION_BANK = {
    "orientation": [
        "What is today's date?",
        "What day of the week is it?",
        "What city are you in right now?"
    ],
    "attention": [
        "Count backwards from 20 to 1.",
        "Can you spell the word 'WORLD' backwards?",
        "Subtract 7 from 100, then subtract 7 again."
    ],
    "memory": [
        "I'm going to say three words: apple, table, penny. Please repeat them.",
        "Can you tell me what you had for breakfast?",
        "What did you do yesterday?"
    ],
    "language": [
        "Name as many animals as you can in 30 seconds.",
        "Repeat this phrase: 'No ifs, ands, or buts.'",
        "What do you call the thing you use to cut paper?"
    ]
}

# Simple scoring rules
def score_answer(category, question, answer):
    if not answer:
        return 0
    answer = answer.lower()
    if category == "orientation":
        return 1 if any(word in answer for word in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday",
                                                   "january","february","march","april","may","june","july","august",
                                                   "september","october","november","december"]) else 0
    if category == "attention":
        return 1 if "19" in answer or "dlrow" in answer or "93" in answer else 0
    if category == "memory":
        return 1 if any(word in answer for word in ["apple","table","penny","breakfast","yesterday"]) else 0
    if category == "language":
        return 1 if any(word in answer for word in ["dog","cat","lion","tiger","no ifs","scissors"]) else 0
    return 0

@app.route("/")
def index():
    session["state"] = {"asked": [], "scores": {}}
    first_cat = random.choice(list(QUESTION_BANK.keys()))
    first_q = random.choice(QUESTION_BANK[first_cat])
    session["state"]["asked"].append(first_q)
    session["state"]["last_category"] = first_cat
    session["state"]["last_question"] = first_q
    return render_template_string(INDEX_HTML, first_question=first_q)


@app.route("/chat", methods=["POST"])
def chat():
    user_text = request.json.get("message", "")
    state = session.get("state", {"asked": [], "scores": {}})

    # Score last question
    if state.get("last_category") and state.get("last_question"):
        cat = state["last_category"]
        q = state["last_question"]
        sc = score_answer(cat, q, user_text)
        state["scores"].setdefault(cat, 0)
        state["scores"][cat] += sc

    # Pick a new question
    remaining = {cat: [q for q in qs if q not in state["asked"]] 
                 for cat, qs in QUESTION_BANK.items()}
    nonempty = [cat for cat, qs in remaining.items() if qs]
    if not nonempty:
        session["state"] = state
        return jsonify({"reply": "Assessment complete! Click Finish to download JSON.", "done": True})

    cat = random.choice(nonempty)
    q = random.choice(remaining[cat])
    state["asked"].append(q)
    state["last_category"] = cat
    state["last_question"] = q
    session["state"] = state

    return jsonify({"reply": q, "done": False})

@app.route("/finish")
def finish():
    state = session.get("state", {})
    scores = state.get("scores", {})
    total_score = sum(scores.values())
    history = state.get("asked", [])

    # Small textual summary
    summary_text = f"Assessment Summary:\nTotal Score: {total_score}\nScores by category:\n"
    for cat, sc in scores.items():
        summary_text += f" - {cat}: {sc}\n"
    if total_score >= 6:
        summary_text += "Interpretation: Normal cognitive performance."
    else:
        summary_text += "Interpretation: Possible impairment — consider clinical follow-up."

    result = {
        "scores": scores,
        "total": total_score,
        "history": history,
        "summary_text": summary_text
    }

    return jsonify(result)

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Elderly Care Cognitive Chatbot</title>
  <style>
    body { font-family: Arial, sans-serif; }
    #chat { border: 1px solid #aaa; padding: 10px; height: 300px; overflow-y: scroll; margin-bottom: 10px; }
    .user { color: blue; margin: 5px 0; }
    .bot { color: green; margin: 5px 0; }
  </style>
</head>
<body>
  <h2>Elderly Care Cognitive Chatbot</h2>
  <div id="chat"></div>
  <input id="entry" placeholder="Type your answer..." />
  <button id="send">Send</button>
  <button id="mic">🎤 Speak</button>
  <button id="finish">Finish & Get JSON</button>

  <script>
    async function send(msg){
      append(msg, "user");
      const res = await fetch("/chat", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: msg})
      });
      const data = await res.json();
      append(data.reply, "bot");
      if (data.done) {
        document.getElementById("send").disabled = true;
        document.getElementById("mic").disabled = true;
      }
    }

    function append(text, who){
      const chat = document.getElementById("chat");
      const el = document.createElement("div");
      el.className = who;
      el.textContent = text;
      chat.appendChild(el);
      chat.scrollTop = chat.scrollHeight;
      if (who === "bot") speak(text);
    }

    document.getElementById("send").onclick = function(){
      const v = document.getElementById("entry").value;
      if(v.trim()) send(v);
      document.getElementById("entry").value = "";
    };

    document.getElementById("finish").onclick = async function(){
      const res = await fetch("/finish");
      const data = await res.json();

      // Display summary in chat
      append(data.summary_text, "bot");

      // Download JSON automatically
      const blob = new Blob([JSON.stringify(data, null, 2)], {type: "application/json"});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "assessment_result.json";
      a.click();
    };

    // --- Voice Input ---
    let recognition;
    if ("webkitSpeechRecognition" in window) {
      recognition = new webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = "en-US";

      recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        console.log("Heard:", text);
        document.getElementById("entry").value = text;
        document.getElementById("send").click();
      };

      recognition.onerror = function(event) {
        console.error("Speech recognition error:", event.error);
      };
    }

    document.getElementById("mic").onclick = function(){
      if (recognition) recognition.start();
    };

    // --- Voice Output ---
    function speak(text) {
      if ("speechSynthesis" in window) {
        speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(text);
        utter.rate = 1;
        utter.pitch = 1;
        utter.lang = "en-US";
        speechSynthesis.speak(utter);
      } else {
        console.error("TTS not supported.");
      }
    }
        // --- Auto-start first question if provided ---
    window.onload = function() {
      const firstQ = "{{ first_question|safe }}";
      if (firstQ) {
        append("👋 Hello! Let's begin your assessment.", "bot");
        append(firstQ, "bot");
      }
    };

  </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)

