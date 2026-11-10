# src/ai_core.py

import openai
import ast
import json

from typing import Dict, List, Optional


class AIDevAssistant:

    def __init__(self, api_key: str):

        """Initialize the AI assistant with API credentials"""
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "gpt-4"

        
    def analyze_code(self, code: str, language: str) -> Dict:

        """Analyze code using AST for Python or regex for other languages"""
        if language == "python":
            try:
                tree = ast.parse(code)
                return {
                    "functions": [node.name for node in ast.walk(tree) 
                                    if isinstance(node, ast.FunctionDef)],
                    "classes": [node.name for node in ast.walk(tree) 
                                    if isinstance(node, ast.ClassDef)],
                    "imports": [node.names[0].name for node in ast.walk(tree) 
                                    if isinstance(node, ast.Import)]
                                            }
            except SyntaxError as e:
                return {"error": str(e), "line": e.lineno}
        
        # For other languages, use simpler pattern matching
        return {"language": language, "lines": len(code.split('\n'))}

    
    def explain_code(self, code: str, context: str = "") -> str:

        """Generate natural language explanation of code"""
        prompt = f"""
        Explain this code in simple terms. Focus on what it does, not how:
         Context: {context}
         Code:
        {code}
         Explanation:
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant. Explain code clearly and concisely."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    

    def fix_bug(self, code: str, error_message: str = "") -> Dict:
         
        """Detect and fix bugs in code"""
        # First, analyze the code structure
        analysis = self.analyze_code(code, "python")

        if "error" in analysis:
            # We found a syntax error
            prompt = f"""
            This code has a syntax error on line {analysis['line']}:
            Error: {analysis['error']}
            Code:
            {code}
            Please fix the code and explain what was wrong.
            Return as JSON with 'fixed_code' and 'explanation' keys.
            """
        else:
            # Look for logical errors
            prompt = f"""
            Review this code for potential bugs or issues:
            Code:
            {code}
            Error message (if any): {error_message}
            Identify bugs and provide fixed code.
            Return as JSON with 'fixed_code', 'bugs_found', and 'explanation' keys.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a debugging expert. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"error": "Failed to parse AI response"}

    
    def generate_tests(self, code: str) -> str:

        """Generate comprehensive unit tests"""
        # Analyze code to understand structure
        analysis = self.analyze_code(code, "python")
        prompt = f"""
        Generate comprehensive unit tests for this code:
        Code:
        {code}
        Requirements:
        1. Test all functions and methods
        2. Include edge cases
        3. Use pytest framework
        4. Add clear test descriptions
        5. Include both positive and negative test cases
        Generate the complete test file.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a test automation expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content


    def generate_documentation(self, code: str, style: str = "google") -> str:

        """Generate documentation in specified style"""
        prompt = f""""
        Add comprehensive documentation to this code using {style} style:
        Code:
        {code}
        Requirements:
        1. Add docstrings to all functions and classes
        2. Document parameters, returns, and exceptions
        3. Include usage examples where helpful
        4. Keep descriptions clear and concise
        Return the fully documented code.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"You are a documentation expert. Use {style} docstring style."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content