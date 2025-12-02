import os
from dotenv import load_dotenv

def load_api_key(api_type='gemini'):
    """Loads an API key from the .env file."""
    load_dotenv()
    if api_type.lower() == 'gemini':
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")
        return key

    # Default to OpenAI
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    return key

def load_base_url():
    """Loads the base URL for the application under test."""
    load_dotenv()
    url = os.getenv("BASE_URL")
    if not url:
        raise ValueError("BASE_URL not found in .env file.")
    return url
