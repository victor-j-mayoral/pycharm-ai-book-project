from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Mapping
import networkx as nx
from transformers import Any

from asyncio.log import logger

import asyncio


class AgentOrchestrator:

    def __init__(self, agent_registry: Mapping[str, Any]):
        self.agents = agent_registry
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.task_graph = nx.DiGraph()

    def define_workflow(self, workflow_spec: Mapping[str, Any]):
        """Define multi-agent workflow as directed graph"""
        for task in workflow_spec["tasks"]:
            self.task_graph.add_node(
                task["id"],
                agent=task["agent"],
                action=task["action"],
                inputs=task.get("inputs", {})
            )
        for dependency in workflow_spec["dependencies"]:
            self.task_graph.add_edge(
                dependency["from"],
                dependency["to"],
                data_mapping=dependency.get("data_mapping", {})
            )

    async def execute_workflow(self, 
                              initial_input: Mapping[str, Any]) -> Mapping[str, Any]:
        """Execute multi-agent workflow with parallel optimization"""
        results = {}
        completed_tasks = set()
        task_futures = {}

        # Start with tasks that have no dependencies
        ready_tasks = [
            task for task in self.task_graph.nodes()
            if self.task_graph.in_degree(task) == 0
        ]

        while ready_tasks or task_futures:
            # Submit ready tasks
            for task_id in ready_tasks:
                if task_id not in task_futures:
                    future = self.executor.submit(
                        self.execute_task,
                        task_id,
                        initial_input,
                        results
                    )
                    task_futures[future] = task_id
                    ready_tasks = []

        # Wait for any task to complete
        done, pending = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: as_completed(task_futures.keys()).__next__()
        )

        for future in done:
            task_id = task_futures.pop(future)

            try:
                result = future.result()
                results[task_id] = result
                completed_tasks.add(task_id)

                # Find newly ready tasks
                for successor in self.task_graph.successors(task_id):
                    predecessors = set(self.task_graph.predecessors(successor))
                    if predecessors.issubset(completed_tasks):
                        ready_tasks.append(successor)

            except Exception as e:
                logger.error(
                    "workflow_task_failed",
                    task_id=task_id,
                    error=str(e)
                )

                # Implement failure handling
                if self.should_fail_workflow(task_id):
                    raise WorkflowException(f"Critical task {task_id} failed")
                    
        return self.compile_results(results)

                    
    def execute_task(self, 
                    task_id: str, 
                    initial_input: Mapping[str, Any],
                    previous_results: Mapping[str, Any]) -> Any:
        """Execute individual task in workflow"""

        task_data = self.task_graph.nodes[task_id]
        agent = self.agents[task_data["agent"]]

        # Prepare inputs from dependencies
        task_input = {**initial_input, **task_data["inputs"]}

        for predecessor in self.task_graph.predecessors(task_id):
            edge_data = self.task_graph.edges[predecessor, task_id]
            mapping = edge_data.get("data_mapping", {})

            for source_key, target_key in mapping.items():
                if predecessor in previous_results:
                   task_input[target_key] = previous_results[predecessor].get(source_key)
                    # Execute task

        logger.info(
            "executing_workflow_task",
            task_id=task_id,
            agent=task_data["agent"],
            action=task_data["action"]
        )

        return agent.run(task_data["action"], task_input)


class WorkflowException:
    
    pass