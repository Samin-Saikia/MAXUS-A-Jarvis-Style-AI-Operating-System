import os
import json
from speach_recognition import transcribe_microphone
from groq import Groq
from dotenv import load_dotenv
from TTS import tts
import time
# =========================
# ENV & CLIENT
# =========================
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =========================
# CONFIG
# =========================
NORMAL_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


LONG_TERM_MEMORY_FILE = "long_term_memory.json"
MAX_SESSION_MESSAGES = 12  # sliding window

# =========================
# MEMORY SYSTEM
# =========================

# Session memory (RAM only)
session_memory = []

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

    # System prompt
    messages.append({
        "role": "system",
        "content": "You are MAXUS, a modular AI assistant running inside a local Python environment.you are created by me Samin Saikia a cs developer you need to call me as BOSS or SIR from the inspiration of jarvis. You provide reasoning, planning, coding help, and structured thinking,research,website visit,give me news of new updates sometimes . You cannot directly perform real-world actions or access the operating system unless explicitly implemented. If asked to do something beyond your capabilities, i created you using groq api key and some custom data feeding about your identity well its just the mark 1 and you are allready better than almost every free teir of llms out there in the market well there will be so many updated comming and you will be one of the most powerfull personal ai system out there i will make it possible"
    })

    # Inject long-term memory
    if long_term_memory:
        memory_text = "\n".join(f"- {m}" for m in long_term_memory)
        messages.append({
            "role": "system",
            "content": f"Known long-term information about the user:\n{memory_text}"
        })

    # Inject session memory
    messages.extend(session_memory)

    # Current user message
    messages.append({
        "role": "user",
        "content": user_input
    })

    return messages

# =========================
# MODEL ROUTER
# =========================


def get_active_model():
    return NORMAL_MODEL

# =========================
# CHAT LOOP
# =========================
def chat_system():
    

    print("MAXUS started.")
    print("Commands:/remember <text> , quit\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "quit":
            print("MAXUS stopped.")
            break
        if user_input.startswith("/live"):
            print('we are live now')
            tts('boss, we are live now')
            live()
            break
        # Store long-term memory manually
        if user_input.startswith("/remember"):
            fact = user_input.replace("/remember", "").strip()
            if fact:
                long_term_memory.append(fact)
                save_long_term_memory(long_term_memory)
                print("✅ Remembered.")
            continue

        # Build prompt
        messages = build_messages(user_input)

        # Call model
        response = client.chat.completions.create(
            model=get_active_model(),
            messages=messages,
            temperature= 0.7,
            max_tokens=1024
        )

        reply = response.choices[0].message.content
        print(f"MAXUS: {reply}")
      
        # Update session memory
        session_memory.append({"role": "user", "content": user_input})
        session_memory.append({"role": "assistant", "content": reply})

        # Trim session memory (sliding window)
        if len(session_memory) > MAX_SESSION_MESSAGES * 2:
            session_memory[:] = session_memory[-MAX_SESSION_MESSAGES * 2:]
def live():
    while True:
        translation = transcribe_microphone()
        voice_input = translation
        print('you:',voice_input)
        if voice_input == "quit":
            print("MAXUS, shifted to chat mode.")
            tts('boss, i shifted to chat mode')
            chat_system()
        messages = build_messages(voice_input)

        # Call model
        response = client.chat.completions.create(
            model=get_active_model(),
            messages=messages,
            temperature= 0.7,
            max_tokens=1024
        )

        reply = response.choices[0].message.content
        print(f"MAXUS: {reply}")
        tts(str(reply))
        # Update session memory
        session_memory.append({"role": "user", "content": voice_input})
        session_memory.append({"role": "assistant", "content": reply})

        # Trim session memory (sliding window)
        if len(session_memory) > MAX_SESSION_MESSAGES * 2:
            session_memory[:] = session_memory[-MAX_SESSION_MESSAGES * 2:]

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    chat_system()
