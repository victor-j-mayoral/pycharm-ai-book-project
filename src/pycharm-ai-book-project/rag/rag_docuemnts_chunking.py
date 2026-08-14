class DocumentChunker:
    
    def __init__(self, chunk_size=500, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_by_tokens(self, text, tokenizer):
        """Chunk based on token count for consistent sizing"""
        tokens = tokenizer.encode(text)
        chunks = []
        for i in range(0, len(tokens), self.chunk_size - self.overlap):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)

        return chunks
    
    def chunk_by_sentences(self, text):
        """Chunk at sentence boundaries for semantic coherence"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = []
        current_size = 0
        for sentence in sentences:
            sentence_size = len(sentence.split())
            if current_size + sentence_size > self.chunk_size:
                chunks.append('. '.join(current_chunk) + '.')
                current_chunk = [sentence]
                current_size = sentence_size
            else:
                current_chunk.append(sentence)
                current_size += sentence_size
        if current_chunk:
            chunks.append('. '.join(current_chunk))

        return chunks