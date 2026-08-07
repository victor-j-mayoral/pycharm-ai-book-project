import chromadb

client = chromadb.Client()
collection = client.create_collection("my_documents")
 # Add documents - ChromaDB generates embeddings automatically
collection.add(
    documents=["Paris is the capital of France", "London is the capital of England"],
    metadatas=[{"source": "wiki"}, {"source": "wiki"}],
    ids=["doc1", "doc2"]
)
# Search semantically
results = collection.query(
    query_texts=["What's the capital of France?"],
    n_results=1
)

print(results['documents'][0])