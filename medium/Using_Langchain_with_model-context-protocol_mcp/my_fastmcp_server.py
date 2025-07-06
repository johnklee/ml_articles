#!/usr/bin/env python
from fastmcp import FastMCP
import asyncio # We'll need this later for the client


# Instantiate the server, giving it a name
mcp = FastMCP(name="My First MCP Server")

print("FastMCP server object created.")


@mcp.tool()
def greet(name: str) -> str:
    """Returns a simple greeting."""
    return f"Hello, {name}!"

@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two numbers together."""
    return a + b

print("Tools 'greet' and 'add' added.")


APP_CONFIG = {"theme": "dark", "version": "1.1", "feature_flags": ["new_dashboard"]}


@mcp.resource("data://config")
def get_config() -> dict:
    """Provides the application configuration."""
    return APP_CONFIG

print("Resource 'data://config' added.")

USER_PROFILES = {
    101: {"name": "Alice", "status": "active"},
    102: {"name": "Bob", "status": "inactive"},
}


@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: int) -> dict:
    """Retrieves a user's profile by their ID."""
    # The {user_id} from the URI is automatically passed as an argument
    return USER_PROFILES.get(user_id, {"error": "User not found"})

print("Resource template 'users://{user_id}/profile' added.")


@mcp.prompt("summarize")
async def summarize_prompt(text: str) -> list[dict]:
    """Generates a prompt to summarize the provided text."""
    return [
        {"role": "system", "content": "You are a helpful assistant skilled at summarization."},
        {"role": "user", "content": f"Please summarize the following text:\n\n{text}"}
    ]

print("Prompt 'summarize' added.")


from fastmcp import Client # Import the client

async def test_server_locally():
    print("\n--- Testing Server Locally ---")
    # Point the client directly at the server object
    client = Client(mcp)

    # Clients are asynchronous, so use an async context manager
    async with client:
        # Call the 'greet' tool
        greet_result = await client.call_tool("greet", {"name": "FastMCP User"})
        print(f"greet result: {greet_result}")

        # Call the 'add' tool
        add_result = await client.call_tool("add", {"a": 5, "b": 7})
        print(f"add result: {add_result}")

        # Read the 'config' resource
        config_data = await client.read_resource("data://config")
        print(f"config resource: {config_data}")

        # Read a user profile using the template
        user_profile = await client.read_resource("users://101/profile")
        print(f"User 101 profile: {user_profile}")

        # Get the 'summarize' prompt structure (doesn't execute the LLM call here)
        prompt_messages = await client.get_prompt("summarize", {"text": "This is some text."})
        print(f"Summarize prompt structure: {prompt_messages}")


# Run the local test function
# asyncio.run(test_server_locally())
# Commented out for now, we'll focus on running the server next

if __name__ == "__main__":
    print("\n--- Starting FastMCP Server via __main__ ---")
    # This starts the server, typically using the stdio transport by default
    mcp.run()
