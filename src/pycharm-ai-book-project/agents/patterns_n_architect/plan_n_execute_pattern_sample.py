class PlanAndExecuteAgent:

    def __init__(self, planner, executor):
        self.planner = planner
        self.executor = executor
        self.plan = []
        self.results = []


    def solve(self, problem):
        # Planning phase
        self.plan = self.create_plan(problem)
        self.validate_plan()
         # Execution phase
        for step in self.plan:
            result = self.execute_step(step)
            self.results.append(result)
             # Replan if necessary
            if self.should_replan(result):
                remaining_steps = self.plan[self.plan.index(step)+1:]
                new_plan = self.replan(problem, self.results, remaining_steps)
                self.plan = self.plan[:self.plan.index(step)+1] + new_plan

        return self.synthesize_results()


    def create_plan(self, problem):
        planning_prompt = f"""
        Problem: {problem}
         Create a detailed plan to solve this problem.
        Format each step as:
        1. [Action]: [Details]
        2. [Action]: [Details]
        ...
        """
        raw_plan = self.planner.generate(planning_prompt)

        return self.parse_plan(raw_plan)

    
    def should_replan(self, result):
        return result.get("status") == "failed" or result.get("unexpected", False)