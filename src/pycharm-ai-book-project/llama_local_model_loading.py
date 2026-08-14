# Local model deployment example
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

def load_local_model(model_name="meta-llama/Llama-2-7b-chat-hf"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",  # Automatically use GPU if available
        load_in_8bit=True   # Reduce memory usage
    )
    return model, tokenizer