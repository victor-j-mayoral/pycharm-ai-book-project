import redis
import json
import hashlib

class RedisLLMCache:

    def __init__(self, redis_url, ttl_hours=24):
        self.redis = redis.from_url(redis_url)
        self.ttl_seconds = ttl_hours * 3600

    async def get_or_generate(self, prompt, generator_func):
        key = f"llm:{hashlib.md5(prompt.encode()).hexdigest()}"
         # Try cache first
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
         # Generate and cache
        response = await generator_func(prompt)
        self.redis.setex(key, self.ttl_seconds, json.dumps(response))

        return response
    