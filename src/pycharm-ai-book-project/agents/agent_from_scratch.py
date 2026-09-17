import asyncio
from openai import AsyncOpenAI
from typing import Dict, Any, Callable

class AsyncCustomAgent:

    """Async version compatible with async LLM wrappers and tools"""
    def __init__(self, name: str, capabilities: Dict[str, Callable]):
        self.name = name
        self.capabilities = capabilities
        self.state = {
            "goals": [],
            "knowledge": {},
            "history": []
        }
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        # Async client for non-blocking operations
        return AsyncOpenAI(
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            request_timeout=30
        )
    
    async def think(self, observation: str) -> str:
        """Core reasoning loop (async version)"""
        thinking_prompt = f"""
        Agent: {self.name}
        Current observation: {observation}
        Current goals: {self.state['goals']}
        Recent history: {self._get_recent_history()}
         Based on this information:
        1. What is the current situation?
        2. What progress has been made toward goals?
        3. What should be the next action?
         Provide your reasoning and recommended action.
        """
         # Async LLM call
        response = await self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": thinking_prompt}]
        )
        return response.choices[0].message.content

    async def act(self, action_description: str) -> Dict[str, Any]:
        """Execute action using available capabilities"""
        # Async capability identification
        capability_name = await self._identify_capability(action_description)

        if capability_name not in self.capabilities:
            return {
                "success": False,
                "error": f"No capability for: {action_description}"
            }
         # Extract parameters
        parameters = await self._extract_parameters(action_description, capability_name)
         # Execute capability (check if async)
        try:
            capability = self.capabilities[capability_name]
            if asyncio.inspect.iscoroutinefunction(capability):
                result = await capability(**parameters)
            else:
                # Run sync function in executor
                result = await asyncio.get_event_loop().run_in_executor(
                    None, capability, **parameters
                )
            await self._update_history(action_description, result)

            return {"success": True, "result": result}
        
        except Exception as e:
            return {"success": False, "error": str(e)}