def process_large_document_efficient(filepath):
    """GOOD: Processes file in chunks"""
    embeddings = []
     # Process file line by line
    with open(filepath, 'r') as f:
        chunk = ""
        for line in f:
            chunk += line
            # Process chunk when it reaches ~1000 characters
            # Most embedding models work best with 200-500 tokens
            # 1000 chars = 250 tokens for English text
            if len(chunk) > 1000:
                embedding = generate_embedding(chunk)
                embeddings.append(embedding)
                chunk = ""  # Reset chunk
         # Don't forget the last chunk
        if chunk:
            embedding = generate_embedding(chunk)
            embeddings.append(embedding)

    return embeddings