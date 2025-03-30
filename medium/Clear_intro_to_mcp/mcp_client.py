#!/usr/bin/env python
from mcp import ClientSession
from mcp.client.sse import sse_client


async def run():
  async with sse_client(url="http://localhost:8000/sse") as streams:
    async with ClientSession(*streams) as session:
      await session.initialize()

      # List available tools
      print('===== List available tools =====')
      tools = await session.list_tools()
      print(str(tools) + '\n')

      # Call a tool
      print('===== Call a tool =====')
      result = await session.call_tool("add", arguments={"a": 4, "b": 5})
      print(result.content[0].text + '\n')

      # List available resources
      print('===== List resources =====')
      resources = await session.list_resources()
      print("resources", resources)
      print("")

      # Read a resource
      print('===== Read a resource =====')
      content = await session.read_resource("greeting://john")
      print("content", content.contents[0].text)
      print("")


if __name__ == "__main__":
  import asyncio

  asyncio.run(run())
