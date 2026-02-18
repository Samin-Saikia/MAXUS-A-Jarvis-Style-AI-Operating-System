import speech_recognition as sr
from groq import Groq
import io
import os
from dotenv import load_dotenv
load_dotenv()
# Initialize Clients
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
recognizer = sr.Recognizer()

def transcribe_microphone():
    with sr.Microphone() as source:
        print("Listening... (Speak now)")
        # Adjust for ambient noise for better accuracy
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio_data = recognizer.listen(source)

    # Convert speech recognition audio to WAV format for Groq
    wav_data = audio_data.get_wav_data()
    
    # Create a file-like object from the byte data
    audio_file = io.BytesIO(wav_data)
    audio_file.name = "microphone.wav" # Name is necessary for API

    print("Transcribing...")
    try:
        # Create a translation of the audio file
        translation = client.audio.translations.create(
            file=("microphone.wav", audio_file),
            model="whisper-large-v3",
            prompt="Specify context or spelling",
            response_format="json",
            temperature=0.0
        )
        return translation.text
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    result = transcribe_microphone()