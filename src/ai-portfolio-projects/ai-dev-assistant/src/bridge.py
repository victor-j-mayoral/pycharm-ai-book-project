# src/bridge.py

import sys
import json
from ai_core import AIDevAssistant


def main():

    if len(sys.argv) < 3:
        print(json.dumps({"error": "Invalid arguments"}))
        return
     
    action = sys.argv[1]
    code = sys.argv[2]

     # Get API key from environment or config
    import os
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print(json.dumps({"error": "No API key found"}))
        return

    assistant = AIDevAssistant(api_key)
    
    if action == 'explain':
        result = assistant.explain_code(code)
        print(result)
    elif action == 'fix':
        result = assistant.fix_bug(code)
        print(json.dumps(result))
    elif action == 'test':
        result = assistant.generate_tests(code)
        print(result)

    if __name__ == "__main__":
        main()