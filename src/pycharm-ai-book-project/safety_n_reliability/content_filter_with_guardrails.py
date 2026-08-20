from typing import List, Dict, Callable
from dataclasses import dataclass

@dataclass
class GuardResult:
    """Result from a guard check"""
    passed: bool
    constraint: str = ""
    alternative_response: str = ""

class LLMGuardrails:
    def __init__(self):
        self.pre_guards = []   # Check before LLM call
        self.post_guards = []  # Check after LLM call

    def add_pre_guard(self, guard: Callable):
        self.pre_guards.append(guard)

    def add_post_guard(self, guard: Callable):
        self.post_guards.append(guard)

    async def safe_generate(self, prompt, llm, **kwargs):
        # Pre-generation guards
        for guard in self.pre_guards:
            result = guard(prompt)
            if not result.passed:
                return result.alternative_response
            
        # Generate response
        response = await llm.generate(prompt, **kwargs)

        # Post-generation guards
        for guard in self.post_guards:
            result = guard(response, prompt)
            if not result.passed:
                # Retry with constraints
                constrained_prompt = f"{prompt}\n\nPlease ensure: {result.constraint}"
                response = await llm.generate(constrained_prompt, **kwargs)

        return response

# Example guards
def length_guard(response, prompt):
    """Ensure response isn't too long"""
    if len(response) > 2000:
        return GuardResult(
            passed=False,
            constraint="Keep response under 2000 characters"
        )
    
    return GuardResult(passed=True)


def factuality_guard(response, prompt):
    """Check for unsupported claims"""
    unsafe_phrases = [
        "studies show", "research proves", "scientists say",
        "doctors recommend", "experts agree"
    ]
    if any(phrase in response.lower() for phrase in unsafe_phrases):
        return GuardResult(
            passed=False,
            constraint="Avoid unsupported claims. Be specific about sources."
        )
    
    return GuardResult(passed=True)


def instruction_adherence_guard(response, prompt):
    """Ensure response follows instructions"""
    if "json" in prompt.lower() and not response.strip().startswith("{"):

        return GuardResult(
            passed=False,
            constraint="Response must be valid JSON format"
        )
    
    return GuardResult(passed=True)
