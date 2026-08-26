from langchain_classic.agents import initialize_agent, AgentType, Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_classic.utilities import WikipediaAPIWrapper
from langchain_classic.memory import ConversationSummaryBufferMemory

from langchain_ollama import ChatOllama

 # Initialize LLM with specific model
llm = ChatOllama(model="llama3.2:latest")


 # Initialize memory
memory = ConversationSummaryBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    llm=llm,
    max_token_limit=1000
)

 # Create tools
search = DuckDuckGoSearchRun()
wikipedia = WikipediaAPIWrapper()

 # Custom tool for report writing
def write_report(research_notes: str) -> str:
    """Structure research notes into a formatted report"""
    prompt = f"""
    Create a well-structured report from these research notes:
    {research_notes}
     Include:
    - Executive summary
    - Key findings
    - Detailed analysis
    - Conclusions
    """
    return llm.invoke(prompt)

tools = [
    Tool(
        name="Search",
        func=search.run,
        description="Search internet for current information"
    ),
    Tool(
        name="Wikipedia",
        func=wikipedia.run,
        description="Get encyclopedic information on topics"
    ),
    Tool(
        name="WriteReport",
        func=write_report,
        description="Structure research into a formatted report"
    )
]


 # Create research agent
research_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    max_iterations=5,
    early_stopping_method="generate"
)


 # Use the agent
task = """Research the current state of renewable energy adoption 
        globally and write a brief report on the findings."""
report = research_agent.run(task)

print(report)