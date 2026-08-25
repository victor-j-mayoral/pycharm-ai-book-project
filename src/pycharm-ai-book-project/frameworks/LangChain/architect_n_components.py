from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_ollama import ChatOllama


 # Models - Wrap various LLMs with consistent interface
 # llm = OpenAI(temperature=0.7)
# Note: LangChain supports many LLM providers. You can easily swap: 
# from langchain.llms import Anthropic 
# llm = Anthropic(model="claude-2") 
# 
# from langchain.llms import Cohere 
# llm = Cohere(model="command") 
# 
# from langchain_huggingface import HuggingFaceEndpoint
# llm = HuggingFaceEndpoint(repo_id="HuggingFaceTB/SmolLM2-360M-Instruct", task="text-generation", huggingfacehub_api_token=os.getenv("HUGGINGFACE_TOKEN"))

# from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama2:latest")

# Prompts - Manage messages with variables
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a senior developer."),
    MessagesPlaceholder("history"),
    ("human", "{input}")   
])

 # Chains - Combine components
chain = prompt | llm

# Memory - Maintain conversation state
store = {}

def get_session_history(session_id):

    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()

    return store[session_id]

chain_with_history = RunnableWithMessageHistory (
            chain,
            get_session_history,
            input_messages_key="input",            
            history_messages_key="history"
)

session_config = {
    "configurable": {
    "session_id": "test-current-session"
    }
}

# Execute chain
response1 = chain_with_history.invoke({"input": "My favorite programming language is Python."},
                                config=session_config)
print("Response 1:", response1.content)

response2 = chain_with_history.invoke({"input": "What is my favorite programming language?"},
                                config=session_config)
print("Response 2:", response2.content)
