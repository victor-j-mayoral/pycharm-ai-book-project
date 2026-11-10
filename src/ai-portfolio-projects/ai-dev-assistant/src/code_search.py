# src/code_search.py

import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
from typing import List, Tuple
import os


class CodeSearchEngine:

    def __init__(self, model_name: str = "microsoft/codebert-base"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.code_snippets = []
        self.file_paths = []


    def index_codebase(self, root_directory: str):
        
        """Index all Python files in the codebase"""
        code_chunks = []
        
        for root, dirs, files in os.walk(root_directory):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in 
                      {'.git', '__pycache__', 'node_modules', 'venv'}]

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                           content = f.read()
                             # Split into chunks (functions/classes)
                        chunks = self.split_code_into_chunks(content)
                        for chunk in chunks:
                            code_chunks.append(chunk)
                            self.code_snippets.append(chunk)
                            self.file_paths.append(file_path)
                    except Exception as e:
                        print(f"Error indexing {file_path}: {e}")

         # Create embeddings
        if code_chunks:
            embeddings = self.model.encode(code_chunks)
            self.index = np.array(embeddings)
             # Save index
            self.save_index()


    def split_code_into_chunks(self, code: str) -> List[str]:
        """Split code into meaningful chunks"""
        chunks = []
        current_chunk = []
        indent_level = 0
        
        for line in code.split('\n'):
            # Calculate indent
            stripped = line.lstrip()
            if stripped:
                current_indent = len(line) - len(stripped)
                 # Start new chunk on function or class definition
                if stripped.startswith(('def ', 'class ')) and current_indent == 0:
                    if current_chunk:
                       chunks.append('\n'.join(current_chunk))
                    current_chunk = [line]
                    indent_level = current_indent
                else:
                    current_chunk.append(line)
         # Add the last chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks


    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, str, float]]:

        """Search for relevant code snippets"""
        if self.index is None:
            return []
         # Encode query
        query_embedding = self.model.encode([query])
         # Calculate similarities
        similarities = np.dot(self.index, query_embedding.T).flatten()
         # Get top results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        results = []

        for idx in top_indices:
            results.append((
                self.code_snippets[idx],
                self.file_paths[idx],
                float(similarities[idx])
            ))
            
        return results       


    def save_index(self, path: str = ".ai_assistant/code_index.pkl"):

        """Save the search index"""
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'wb') as f:
            pickle.dump({
                'index': self.index,
                'snippets': self.code_snippets,
                'paths': self.file_paths
            }, f)


    def load_index(self, path: str = ".ai_assistant/code_index.pkl"):

        """Load saved index"""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = pickle.load(f)
                self.index = data['index']
                self.code_snippets = data['snippets']
                self.file_paths = data['paths']

            return True
        
        return False