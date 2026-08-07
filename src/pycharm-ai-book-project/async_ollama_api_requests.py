import asyncio
import time
from ollama import AsyncClient

 # Create async client
client = AsyncClient()

async def get_ai_response_async(prompt):
    # Async version of the same function
    response = await client.chat(
        model="llama2",
        messages=[{"role": "user", "content": prompt}]
        )
    return response['message']['content']

async def process_questions():
    questions = ["What is Python?", "What is JavaScript?", "What is Go?"]
     # Create all tasks at once
    tasks = []
    for question in questions:
        task = get_ai_response_async(question)
        tasks.append(task)
     # Wait for all to complete
    start = time.time()
    answers = await asyncio.gather(*tasks)
     # Print results
    for question, answer in zip(questions, answers):
        print(f"Q: {question}")
        print(f"A: {answer[:50]}...\n")
    print(f"Total time: {time.time() - start:.1f} seconds")
     # Output: Total time: less seconds (all processed in parallel!)

 # Run the async function
asyncio.run(process_questions())