from pinecone import Pinecone, ServerlessSpec

pc=Pinecone(api_key="PINECONE_API_KEY")

 # Create an index (one-time operation)
pc.create_index(name="indice-pinecone-test",
                    dimension=1536,
                    metric="euclidean",
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-west-2'
                    ),
                    tags={
                        "environment": "development"
                    }
                    )
index = Pinecone.Index("indice-pinecone-test")