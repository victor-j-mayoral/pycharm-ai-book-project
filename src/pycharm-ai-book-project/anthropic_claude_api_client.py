import anthropic
client = anthropic.Anthropic(api_key="CLAUDE_API_KEY")
message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        messages=[
                    {"role": "user", "content": "Explain what an API is."}
                ]
)
print(message.content[0].text)