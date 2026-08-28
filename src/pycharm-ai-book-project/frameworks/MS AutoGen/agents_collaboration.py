from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager


config_list = [
  {
    "model": "llama2:latest",
    "base_url": "http://localhost:11434/v1",
    "api_key": "ollama",
    "price": [0.0, 0.0]
  }
]


# Define specialized agents
researcher = AssistantAgent(
    name="Researcher",
    system_message="""You are a research specialist. 
    Your role is to find and analyze information from various sources.
    Always cite your sources and verify facts.""",
    llm_config={"config_list": config_list}
)

analyst = AssistantAgent(
    name="Analyst",
    system_message="""You are a data analyst.
    Your role is to analyze data, identify patterns, and provide insights.
    Present findings clearly with supporting evidence.""",
    llm_config={"config_list": config_list}
)

writer = AssistantAgent(
    name="Writer",
    system_message="""You are a technical writer.
    Your role is to create clear, well-structured documents.
    Synthesize input from other agents into cohesive content.""",
    llm_config={"config_list": config_list}
)


 # User proxy for human interaction
user_proxy = UserProxyAgent(
    name="Human",
    code_execution_config={"use_docker": False},
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=0
)


 # Create group chat
group_chat = GroupChat(
    agents=[researcher, analyst, writer, user_proxy],
    messages=[],
    max_round=10
)   

manager = GroupChatManager(groupchat=group_chat, llm_config={"config_list": config_list})


 # Initiate collaborative task
user_proxy.initiate_chat(
    manager,
    message="""Create a comprehensive report on the impact of AI on software development. 
            Include current trends, statistical analysis, and future predictions."""
)