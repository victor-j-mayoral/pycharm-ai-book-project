from google import genai
import os
from dotenv import load_dotenv
from google.api_core.exceptions import GoogleAPIError # for robust handling

# Load environment variables from .env file
load_dotenv()

# Access keys safely
gemini_key = os.getenv("GEMINI_GOOGLE_API_KEY")

 # 1. Auth - pick up your key from an env var (recommended)
#    export GEMINI_API_KEY="your‑api‑key"
client = genai.Client(api_key=gemini_key) # SDK auto‑reads GEMINI_API_KEY
try:
    response = client.models.generate_content(
        model="gemini-3.6-flash",                     # pick an available Gemini model
        contents="Explain what an API is."            # note the plural parameter name
    )
    print(response.text)                   # each part already concatenated
except GoogleAPIError as err:
    print(f"Gemini API error ({err.code}): {err.message}")