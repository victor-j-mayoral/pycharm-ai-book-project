import time

from ollama import ChatResponse, ResponseError as OllamaRateLimitError

from openai import RateLimitError as OpenAIRateLimitError
from anthropic import RateLimitError as AnthropicRateLimitError


 # Custom exceptions for unified handling
class AIError(Exception):
    """Base class for AI-related errors"""
    pass

class RateLimitError(AIError):
    """Too many requests"""
    pass
class TokenLimitError(AIError):
    """Request too long"""
    pass
class ContentFilterError(AIError):
    """Content blocked by safety filter"""
    pass



def call_ai_api(prompt, provider="ollama"):
    """Wrapper that translates provider-specific errors to our custom ones"""
    try:
        if provider == "ollama":
            # Ollama specific call
            response = ChatResponse.chat(
                model="llama2",
                messages=[{"role": "user", "content": prompt}]
            )

        return response['message']['content']
    
    except OllamaRateLimitError as e:
        if e.status_code == 429:
            raise RateLimitError("Ollama rate limit hit")
    
    except Exception as e:
        if "maximum context length" in str(e):
            raise TokenLimitError("Token limit exceeded")
        elif "content_filter" in str(e):
            raise ContentFilterError("Content filtered")
        raise  # Re-raise unknown errors

def call_ai_with_retry(prompt, max_retries=3):
    """Call AI API with intelligent retry logic"""
    for attempt in range(max_retries):
        try:
            # Try to call the API
            response = call_ai_api(prompt)
            return response
        
        except OllamaRateLimitError as e:
            if e.status_code == 429:
                # Rate limited - wait and retry
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    print(f"Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print("Max retries reached. Please try later.")
                    raise

        except TokenLimitError:
            # Prompt too long - try to shorten
            print("Prompt too long. Shortening...")
            prompt = prompt[:1000] + "..."  # Truncate
            # Don't count this as a retry
            attempt -= 1

        except ContentFilterError:
            # Content blocked - don't retry
            print("Content blocked by safety filter.")
            return "I can't process this request due to content restrictions."
        
        except Exception as e:
            # Unknown error - log and retry
            print(f"Unexpected error: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                raise