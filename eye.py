import base64
import os
import tkinter as tk
from tkinter import filedialog, simpledialog
from dotenv import load_dotenv
from groq import Groq

# Load environment variables (ensure GROQ_API_KEY is in .env)
load_dotenv()

def encode_image(image_path):
    """Encodes the image to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def eye():
    """
    Opens a file dialog to select an image, prompts for a question,
    and sends it to Groq's Vision model.
    """
    # 1. Setup GUI to hide the main tkinter window
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True) # Bring dialog to front

    # 2. Open File Manager to select image
    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp")]
    )

    if not file_path:
        print("No image selected.")
        return

    # 3. Prompt user for the question
    user_prompt = simpledialog.askstring("Input", "What is your question about this image?", initialvalue="What's in this image?")
    
    if not user_prompt:
        user_prompt = "What's in this image?" # Default

    print(f"Analyzing: {os.path.basename(file_path)}...")

    # 4. Get the base64 string
    base64_image = encode_image(file_path)

    # 5. Initialize Client and API Request
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            # Note: Used a valid vision-capable model, ensure this is correct for your access
            model="meta-llama/llama-4-maverick-17b-128e-instruct", 
        )
        print("\n--- Output ---\n")
        print(chat_completion.choices[0].message.content)
        print("\n--------------\n")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Run the function ---
if __name__ == "__main__":
    eye()
