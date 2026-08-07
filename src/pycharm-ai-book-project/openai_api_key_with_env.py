import os

from dotenv import load_dotenv

 # Load environment variables from .env file
load_dotenv()

 # Access keys safely
openai_key = os.getenv("OPENAI_API_KEY")

if not openai_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

 # Never log API keys
print(f"OpenAI key loaded: {'*' * 8}{openai_key[-4:]}")  # Show only last 4 chars