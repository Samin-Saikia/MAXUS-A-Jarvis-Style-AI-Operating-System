import os
import pygame
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def tts(input):
    # Initialize OpenAI client (connected to Groq)
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

    # File path for saved audio
    speech_file_path = "audio.wav"

    # Text to convert to speech
    text = input

    # Generate speech
    response = client.audio.speech.create(
        model="canopylabs/orpheus-v1-english",
        voice="troy",
        input=text,
        response_format="wav"
    )

    # Save audio file
    # Assuming 'response' is the openai response object
    with open("audio.wav", "wb") as f:
        f.write(response.content)


    # Play audio using built-in Windows audio system


    pygame.mixer.init()
    pygame.mixer.music.load('audio.wav')
    pygame.mixer.music.play()

    # Wait for the music to finish
    while pygame.mixer.music.get_busy():
        time.sleep(1) # Check every second
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()