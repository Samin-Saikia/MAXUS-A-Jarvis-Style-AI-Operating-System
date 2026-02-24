import os
import json
from flask import Flask, request, jsonify, render_template
from groq import Groq
from dotenv import load_dotenv

# =========================
# INIT
# =========================
load_dotenv()
app = Flask(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

NORMAL_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

LONG_TERM_MEMORY_FILE = "long_term_memory.json"
MAX_SESSION_MESSAGES = 12

session_memory = []

# =========================
# MEMORY
# =========================
def load_long_term_memory():
    if not os.path.exists(LONG_TERM_MEMORY_FILE):
        return []
    with open(LONG_TERM_MEMORY_FILE, "r") as f:
        return json.load(f)

def save_long_term_memory(memory):
    with open(LONG_TERM_MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

long_term_memory = load_long_term_memory()

# =========================
# PROMPT BUILDER
# =========================
def build_messages(user_input):
    messages = []

    messages.append({
        "role": "system",
        "content": "You are MAXUS, a modular AI assistant created by me Samin Saikia a passionate cs developer created you using groq api key of scout 17b model you are created inspired from jarvis in iron man. Call me user BOSS or SIR. you help me with structured reasoning and coding help, recearch ,websearch and some random talk."
    })

    if long_term_memory:
        memory_text = "\n".join(f"- {m}" for m in long_term_memory)
        messages.append({
            "role": "system",
            "content": f"Known long-term information:\n{memory_text}"
        })

    messages.extend(session_memory)

    messages.append({
        "role": "user",
        "content": user_input
    })

    return messages

@app.route("/")
def home():
    return render_template("index.html")
# =========================
# CHAT ROUTE
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_input = data.get("message")

        if not user_input:
            return jsonify({"reply": "No message received."})

        messages = build_messages(user_input)

        response = client.chat.completions.create(
            model=NORMAL_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )

        reply = response.choices[0].message.content

        # update session memory
        session_memory.append({"role": "user", "content": user_input})
        session_memory.append({"role": "assistant", "content": reply})

        if len(session_memory) > MAX_SESSION_MESSAGES * 2:
            session_memory[:] = session_memory[-MAX_SESSION_MESSAGES * 2:]

        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "Backend error occurred."}), 500
# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)