import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Load your API key ---
# Make sure your .env file has GEMINI_API_KEY
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("GEMINI_API_KEY not found in .env file.")
else:
    genai.configure(api_key=api_key)

    print("--- Finding models that support 'generateContent' ---")

    try:
        # Loop through all available models
        for m in genai.list_models():
            # Check if the model supports the 'generateContent' method
            if 'generateContent' in m.supported_generation_methods:
                print(f"Model name: {m.name}")

    except Exception as e:
        print(f"An error occurred: {e}")

print("--- Done ---")