from crewai import Agent, Task, Crew, LLM


llm = LLM(
    model="ollama/llama3.2",
    base_url="http://localhost:11434"
)

 # Define agents with specific roles
project_manager = Agent(
    role='Project Manager',
    goal='Coordinate the team to deliver a high-quality mobile app',
    backstory="""You are an experienced project manager who has delivered
    dozens of successful mobile applications. You excel at breaking down
    complex projects and coordinating team efforts.
    When delegating work, use exactly these coworker names:
    - UI/UX Designer
    - Mobile Developer""",
    llm=llm,
    verbose=True,
    allow_delegation=True
)

ui_designer = Agent(
    role='UI/UX Designer',
    goal='Design intuitive and beautiful user interfaces',
    backstory="""You are a creative designer with a keen eye for user experience.
    You stay updated with the latest design trends and prioritize usability.""",
    llm=llm,
    verbose=True
)

developer = Agent(
    role='Mobile Developer',
    goal='Implement robust and efficient mobile applications',
    backstory="""You are a skilled developer proficient in React Native and Flutter.
    You write clean, maintainable code and follow best practices.""",
    llm=llm,
    verbose=True
)


 # Define tasks
design_task = Task(
    description="""Design the user interface for a fitness tracking app.
    Include wireframes for main screens: dashboard, workout logging, and progress tracking.
    Consider accessibility and mobile-first design principles.""",
    expected_output="""A detailed UI/UX design document containing wireframes for the
    dashboard, workout logging, and progress tracking screens, along with accessibility
    and mobile-first design recommendations.""",
    agent=ui_designer
)

development_task = Task(
    description="""Implement the core features of the fitness tracking app.
    Build the workout logging system with real-time data synchronization.
    Ensure smooth performance on both iOS and Android.""",
    expected_output="""A functional implementation of the core application features,
    including workout logging, real-time synchronization, and cross-platform support
    for iOS and Android.""",
    agent=developer
)

coordination_task = Task(
    description="""Create a project timeline and coordinate between design and development.
    Ensure milestones are met and communication flows smoothly.
    Identify and mitigate any risks to project delivery.""",
    expected_output="""A project plan with milestones, task dependencies, risk assessment,
    mitigation strategies, and a communication schedule between teams.""",
    agent=project_manager
)


 # Create and run crew
crew = Crew(
    agents=[project_manager, ui_designer, developer],
    tasks=[design_task, development_task, coordination_task],
    verbose=True
)

result = crew.kickoff()

print(result)