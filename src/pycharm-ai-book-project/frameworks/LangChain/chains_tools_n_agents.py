from langchain_classic.agents import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_classic.utilities import WikipediaAPIWrapper

from langchain_ollama import ChatOllama


 # Define tools
search = DuckDuckGoSearchRun()
wikipedia = WikipediaAPIWrapper()


llm = ChatOllama(model="llama2:latest")

tools = [
    Tool(
        name="Search",
        func=search.run,
        description="Search for current information on the internet"
        ),
    Tool(
        name="Wikipedia",
        func=wikipedia.run,
        description="Look up encyclopedic information"
    )
]


 # Create agent with tools
from langchain_classic.agents import initialize_agent, AgentType

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

 # Agent automatically chooses tools
result = agent.run("What are the latest developments in quantum computing?")