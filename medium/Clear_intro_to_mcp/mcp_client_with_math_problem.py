#!/usr/bin/env python
# Create server parameters for stdio connection
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o")


server_params = StdioServerParameters(
    command="python",
    # Make sure to update to the full absolute path to your math_server.py file
    args=["/tmp/math_mcp_server.py"])


async def main():
  async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
      # Initialize the connection
      await session.initialize()

      # Get tools
      tools = await load_mcp_tools(session)

      # Create and run the agent
      agent = create_react_agent(model, tools)
      agent_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
      print('Agent response:')
      for message in agent_response['messages']:
        print(f'{message.__class__.__name__}: {message}')
        print("")


# Run the async function
asyncio.run(main())
