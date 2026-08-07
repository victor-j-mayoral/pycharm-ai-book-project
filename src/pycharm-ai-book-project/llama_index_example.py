from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

 # Load all documents from a directory
documents = SimpleDirectoryReader('docs').load_data()
 # Create an index (this generates embeddings)
index = VectorStoreIndex.from_documents(documents)
 # Query your documents
query_engine = index.as_query_engine()
response = query_engine.query("What does our documentation say about authentication?")

print(response)