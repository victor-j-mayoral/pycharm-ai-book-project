import hashlib
from datetime import datetime, timedelta

class SmartLLMCache:

    def __init__(self, ttl_hours=24):
        self.cache = {}
        self.ttl = timedelta(hours=ttl_hours)
        self.hit_count = 0
        self.miss_count = 0


    def _generate_key(self, prompt, model, temperature):
        """Create cache key from request parameters"""
        # Include parameters that affect output
        key_string = f"{model}:{temperature}:{prompt.strip().lower()}"

        return hashlib.md5(key_string.encode()).hexdigest()

    
    async def get_or_generate(self, prompt, model, temperature, generator_func):
        key = self._generate_key(prompt, model, temperature)
         # Check cache
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() < entry["expires"]:
                self.hit_count += 1
                return entry["response"]
         # Generate new response
        self.miss_count += 1
        response = await generator_func(prompt, model, temperature)
         # Cache response
        self.cache[key] = {
           "response": response,
            "expires": datetime.now() + self.ttl,
            "created": datetime.now()
        }

        return response

    
    def get_stats(self):
        total = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total if total > 0 else 0
        
        return {
            "hit_rate": hit_rate,
            "cache_size": len(self.cache),
            "savings": self.hit_count * 0.002  # Assuming $0.002 per call
        }
    