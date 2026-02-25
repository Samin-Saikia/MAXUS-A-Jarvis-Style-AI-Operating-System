import os
import base64
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
@app.route("/vision", methods=["POST"])
def vision():
    try:
        if "image" not in request.files:
            return jsonify({"reply": "No image received."})

        image = request.files["image"]
        user_prompt = request.form.get("prompt", "Describe this image.")

        image_bytes = image.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        # Build normal memory messages FIRST (system + long term + session)
        messages = []

        messages.append({
            "role": "system",
            "content": "You are MAXUS, a modular AI assistant created by me Samin Saikia a passionate cs developer created you using groq api key of scout 17b model you are created inspired from jarvis in iron man. Call me user BOSS or SIR. you help me with structured reasoning and coding help, recearch ,websearch, image processing and output based on it ,i can send image to you via the ui image icon and you can resonce via a api key call and some random talk."
        })

        if long_term_memory:
            memory_text = "\n".join(f"- {m}" for m in long_term_memory)
            messages.append({
                "role": "system",
                "content": f"Known long-term information:\n{memory_text}"
            })

        messages.extend(session_memory)

        # Now append vision message
        vision_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }

        messages.append(vision_message)

        completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )

        reply = completion.choices[0].message.content

        # ✅ Save to SAME session memory
        session_memory.append(vision_message)
        session_memory.append({"role": "assistant", "content": reply})

        # Trim session memory (same logic as chat)
        if len(session_memory) > MAX_SESSION_MESSAGES * 2:
            session_memory[:] = session_memory[-MAX_SESSION_MESSAGES * 2:]

        return jsonify({"reply": reply})

    except Exception as e:
        print("VISION ERROR:", e)
        return jsonify({"reply": "Vision backend error occurred."}), 500
# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)