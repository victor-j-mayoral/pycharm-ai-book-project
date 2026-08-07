from langchain_google_genai import ChatGoogleGenerativeAI

 # Create models with the same interface
genai_llm = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview", api_key="GEMINI_API_KEY", temperature=0.7)

 # Use them identically
response = genai_llm.invoke("What is machine learning?")
print(response.content)