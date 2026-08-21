import asyncio
from typing import Dict, Any

class AsyncMultiAgentSystem:
    """Asynchronous multi-agent system for better scalability"""

    def __init__(self):
        self.agents = {
            "researcher": ResearchAgent(),
            "analyst": AnalysisAgent(),
            "writer": WritingAgent(),
            "reviewer": ReviewAgent()
        }
        self.message_queues = {name: asyncio.Queue() for name in self.agents}


    async def collaborate_on_task(self, task):
        assignments = self.assign_subtasks(task)
         # Create tasks for each agent
        tasks = []
        for agent_name, subtask in assignments.items():
            task = asyncio.create_task(
                self.agent_work_async(agent_name, subtask)
            )
            tasks.append(task)
         # Wait for all agents to complete
        results = await asyncio.gather(*tasks)

         # Combine results
        return self.integrate_results(dict(zip(assignments.keys(), results)))

    
    async def agent_work_async(self, agent_name, subtask):
        """Async version of agent work"""
        agent = self.agents[agent_name]
        while not agent.is_complete(subtask):
            # Non-blocking message check
            try:
                message = await asyncio.wait_for(
                    self.message_queues[agent_name].get(),
                    timeout=0.1
                )
                agent.process_messages([message])
            except asyncio.TimeoutError:
                pass
            # Do work
            result = agent.work_on(subtask)
             # Share findings if available
            if agent.has_sharable_findings():
                await self.broadcast_findings_async(agent_name, result)

        return agent.get_final_result()