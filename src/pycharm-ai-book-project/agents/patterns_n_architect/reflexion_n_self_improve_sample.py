class ReflexionAgent:

    def __init__(self, llm):
        self.llm = llm  # LLM for reflection and strategy generation
        self.experiences = []
        self.strategies = {}
        self.performance_history = []


    def attempt_task(self, task):
        # Select strategy based on past experience
        strategy = self.select_strategy(task)
         # Execute with monitoring
        result = self.execute_with_monitoring(task, strategy)
         # Reflect on performance
        reflection = self.reflect(task, strategy, result)
         # Learn from experience
        self.update_strategies(reflection)

        return result

    
    def reflect(self, task, strategy, result):
        reflection_prompt = f"""
        Task: {task}
        Strategy used: {strategy}
        Result: {result}
        Analyze What worked well and what didn't.
                What would you do differently next time?
                What patterns do you notice?
        """
        reflection = self.llm.generate(reflection_prompt)
         # Store experience
        self.experiences.append({
            "task": task,
            "strategy": strategy,
            "result": result,
            "reflection": reflection,
            "success_score": self.evaluate_success(result)
        })

        return reflection

    
    def evaluate_success(self, result):
        """Evaluate how successful the result was (0-1 score)
        Override this method for task-specific evaluation"""
        # Simple placeholder - check if result contains success indicators
        if isinstance(result, dict):
            return result.get("success", 0.5)
        elif isinstance(result, str):
            # Basic sentiment analysis
            positive_words = ["success", "completed", "achieved", "solved"]
            negative_words = ["failed", "error", "unable", "problem"]
            result_lower = result.lower()
            positive_count = sum(1 for word in positive_words if word in result_lower)
            negative_count = sum(1 for word in negative_words if word in result_lower)
            if positive_count > negative_count:
                return 0.8
            elif negative_count > positive_count:
                return 0.2
            else:
                return 0.5
            
        return 0.5  # Default neutral score

    
    def extract_lessons(self, reflection):
        """Extract actionable lessons from reflection
        Returns list of lesson objects with strategy_type and content"""
        # Use LLM to extract structured lessons
        extraction_prompt = f"""
        From this reflection, extract actionable lessons:
        {reflection}
         Format each lesson as:
        STRATEGY_TYPE: [type of strategy]
        LESSON: [specific learning]
        """
        lessons_text = self.llm.generate(extraction_prompt)
         # Parse lessons (simple implementation)
        lessons = []
        current_lesson = {}
        for line in lessons_text.strip().split('\n'):
            if line.startswith("STRATEGY_TYPE:"):
                if current_lesson:
                    lessons.append(type('Lesson', (), current_lesson))
                current_lesson = {"strategy_type": line.split(":", 1)[1].strip()}
            elif line.startswith("LESSON:"):
                current_lesson["content"] = line.split(":", 1)[1].strip()
         # Add last lesson
        if current_lesson and "content" in current_lesson:
            lessons.append(type('Lesson', (), current_lesson))

        return lessons

    
    def update_strategies(self, reflection):
        # Extract lessons learned
        lessons = self.extract_lessons(reflection)
         # Update strategy database
        for lesson in lessons:
            if lesson.strategy_type not in self.strategies:
                self.strategies[lesson.strategy_type] = []
            self.strategies[lesson.strategy_type].append(lesson)


    def select_strategy(self, task):
        """Select best strategy based on past experiences
        Override for task-specific selection"""
        # Placeholder - returns most successful past strategy
        if not self.experiences:
            return "default_strategy"
        # Find similar past tasks and their strategies
        best_score = 0
        best_strategy = "default_strategy"
        for exp in self.experiences:
            if exp["success_score"] > best_score:
                best_score = exp["success_score"]
                best_strategy = exp["strategy"]

        return best_strategy