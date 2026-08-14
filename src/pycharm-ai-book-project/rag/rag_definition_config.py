class RAGSystem:
    
    def __init__(self, document_store, embedder, llm):
        self.document_store = document_store
        self.embedder = embedder
        self.llm = llm

    def answer_question(self, question):

        # 1. Convert question to embedding
        question_embedding = self.embedder.encode(question)

         # 2. Retrieve relevant documents
        relevant_docs = self.document_store.search(
            question_embedding, 
            top_k=5
        )

         # 3. Create context from documents
        context = "\n".join([doc.content for doc in relevant_docs])

         # 4. Generate answer with context
        prompt = f"""Answer based on the following context:
        Context: {context}
        Question: {question}
        Answer:"""

        return self.llm.generate(prompt)