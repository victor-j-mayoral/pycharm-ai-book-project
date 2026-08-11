
import os
from dotenv import load_dotenv
from huggingface_hub import login

from transformers import AutoTokenizer

# Load environment variables from .env file
load_dotenv()

login(token=os.getenv("HUGGINGFACE_TOKEN"))

# Ollama's tokenizer for LlaMa models
encoder = AutoTokenizer.from_pretrained("NousResearch/Llama-2-7b-hf")

 # Tokenize text
text = "Hello, world! AI is amazing."
tokens = encoder.encode(text)

print(f"Text: {text}")
print(f"Tokens: {tokens}")
print(f"Token count: {len(tokens)}")

 # Decode back to text
decoded = encoder.decode(tokens)
print(f"Decoded: {decoded}")