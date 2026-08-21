class ReActAgent:

    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.history = []


    def run(self, task):
        self.history.append(f"Task: {task}")

        while not self.is_complete(task):
            # Reasoning step
            thought = self.think()
            self.history.append(f"Thought: {thought}")
             # Decide on action
            action = self.decide_action(thought)
            self.history.append(f"Action: {action}")
            # Execute action
            observation = self.execute(action)
            self.history.append(f"Observation: {observation}")

        return self.generate_final_answer()

    
    def think(self):
        prompt = f"""
        {chr(10).join(self.history)}
         What should I do next? Think step by step.
        """
        return self.llm.generate(prompt)

    
    def decide_action(self, thought):
        prompt = f"""
        Based on this thought: {thought}
        Available tools: {list(self.tools.keys())}
         What action should I take? Format: TOOL[ARGS]
        """
        return self.llm.generate(prompt)