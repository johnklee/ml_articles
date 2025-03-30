#!/usr/bin/env python
# Create server parameters for stdio connection
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o")


MATH_MCP_SERVER_MODULE_PATH = (
    "/home/john/Gitrepos/ml_articles/medium/Clear_intro_to_mcp/math_mcp_server.py")

async def main():
  async with MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            # Make sure to update to the full absolute path to your math_server.py file
            "args": [MATH_MCP_SERVER_MODULE_PATH],
            "transport": "stdio",
        },
        "weather": {
            # make sure you start your weather server on port 8000
            "url": "http://localhost:8000/sse",
            "transport": "sse",
        }
    }
  ) as client:
    agent = create_react_agent(model, client.get_tools())
    for question in [
          "what's (3 + 5) x 12?",
          "what is the weather in Taiwan?",
      ]:
      response = await agent.ainvoke({"messages": question})
      print(f'===== Q: {question} =====')
      for message in response['messages']:
        print(f'{message.__class__.__name__}: {message}')
        print("")


# Run the async function
asyncio.run(main())
