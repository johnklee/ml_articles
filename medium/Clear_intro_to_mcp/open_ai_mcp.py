#!/usr/bin/env python
import openai
from mcp import MCPClient, Context, Message

# Set your OpenAI API key
openai.api_key = "..."

# Initialize MCP Client
client = MCPClient(model="gpt-4", provider="openai")

# Create a structured context
context = Context(name="chat_session", description="A conversation with OpenAI LLM")

# Add initial system instructions
context.add_message(Message(role="system", content="You are a helpful AI assistant."))

# Function to chat with the AI using MCP
def chat_with_ai(user_input):
    # Add user message to context
    context.add_message(Message(role="user", content=user_input))

    # Send request to OpenAI via MCP
    response = client.chat(context=context)

    # Add assistant response to context
    context.add_message(Message(role="assistant", content=response.content))

    return response.content


# Example conversation
print("Chatbot: Hello! How can I assist you?")
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    response = chat_with_ai(user_input)
    print("Chatbot:", response)
