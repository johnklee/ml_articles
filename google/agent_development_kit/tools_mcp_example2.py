#!/usr/bin/env python
"""OOO version of agent to integrate MCP tools.

Reference:
  - https://stackoverflow.com/questions/33128325/how-to-set-class-attribute-with-await-in-init
"""
from __future__ import annotations

import pathlib
import logging
import os
import asyncio
import warnings

from dotenv import find_dotenv, load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # Optional
from google.adk.tools.base_toolset import BaseTool
from google.adk.sessions import Session
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams, StdioConnectionParams, StdioServerParameters


logging.getLogger('google_adk.google.adk.tools.base_authenticated_tool').setLevel(logging.ERROR)
logging.getLogger('google_genai.types').setLevel(logging.ERROR)
warnings.filterwarnings('ignore')
Path = pathlib.Path

# --- Load Environment Variables (If ADK tools need them, e.g., API keys) ---
_ = load_dotenv(find_dotenv(os.path.expanduser('~/.env'))) # read local .env file


# IMPORTANT: Replace this with the ABSOLUTE path to your my_adk_mcp_server.py script
TARGET_FOLDER_PATH = (
    str(Path(os.path.dirname(os.path.abspath(__file__))) / Path('mcp_examples/mcp_filesystem/test/')))


class SimpleAgent:
  model_name: str
  agent_name: str
  root_agent: LlmAgent
  runner: Runner
  session: Session
  llm_last_query_resp: str

  @classmethod
  async def create(
      cls,
      app_name: str='mcp_filesystem_app',
      model_name: str='gemini-2.0-flash',
      agent_name: str='enterprise_assistant',
      instruction='Help user accessing their file systems',
      tools: list[BaseTool] | None = None,
      user_id: str='user_fs') -> SimpleAgent:
    self = SimpleAgent()
    self.model_name = model_name
    self.agent_name = agent_name
    tools = tools or []
    self.root_agent = LlmAgent(
        model=model_name,
        name=agent_name,
        instruction=instruction,
        tools=tools, # Provide the MCP tools to the ADK agent
    )

    session_service = InMemorySessionService()
    # Artifact service might not be needed for this example
    artifacts_service = InMemoryArtifactService()
    self.session = await session_service.create_session(
        state={}, app_name=app_name, user_id=user_id)

    self.runner = Runner(
        app_name=app_name,
        agent=self.root_agent,
        artifact_service=artifacts_service, # Optional
        session_service=session_service)

    return self

  def query(self, query_str: str) -> str:
    coroutine = self.query_async(query_str)
    try:
      loop = asyncio.get_event_loop()
    except RuntimeError:
      return asyncio.run(coroutine)
    else:
      loop.run_until_complete(coroutine)

    return self.llm_last_query_resp

  async def query_async(self, query_str: str) -> str:
    logging.debug("User Query: '%s'", query_str)
    content = types.Content(
        role='user',
        parts=[types.Part(text=query_str)])

    logging.debug("Running agent...")
    events_async = self.runner.run_async(
        session_id=self.session.id,
        user_id=self.session.user_id,
        new_message=content)

    async for event in events_async:
      if event.is_final_response():
        final_response = event.content.parts[0].text
        self.llm_last_query_resp = final_response
        return final_response

    return '?'

  async def interact_async(self):
    while True:
      user_query = input('>>> User$  ')
      if user_query.strip() in {'bye', 'exit', 'quit', 'q'}:
        print('>>> Agent# Bye!')
        break

      resp = await self.query_async(user_query)
      print(f'>>> Agent# {resp}')


async def async_main():
  toolset = MCPToolset(
      # Use StdioConnectionParams for local process communication
      connection_params=StdioConnectionParams(
          server_params = StdioServerParameters(
            command='npx', # Command to run the server
            args=["-y",    # Arguments for the command
                "@modelcontextprotocol/server-filesystem",
                TARGET_FOLDER_PATH],
          ),
          auth_config=None,
      ),
      tool_filter=['read_file', 'list_directory'], # Optional: filter specific tools
      # For remote servers, you would use SseConnectionParams instead:
      # connection_params=SseConnectionParams(url="http://remote-server:port/path", headers={...})
  )
  demo_agent = await SimpleAgent.create(tools=[toolset])

  query_str = f'list files in the path {TARGET_FOLDER_PATH}'
  print(f'>>> User: {query_str}')
  resp = await demo_agent.query_async(query_str)
  resp = resp.strip()
  print(f'>>> Agent: {resp}')
  query_str = (
      f'Show me the content of the files from your response "{resp}".'
      f' Those files are under the directory path as "{TARGET_FOLDER_PATH}"')
  print(f'>>> User: {query_str}')
  resp = await demo_agent.query_async(query_str)
  print(f'>>> Agent: {resp}')
  await toolset.close()


async def async_main_interact():
  toolset = MCPToolset(
      # Use StdioConnectionParams for local process communication
      connection_params=StdioConnectionParams(
          server_params = StdioServerParameters(
            command='npx', # Command to run the server
            args=["-y",    # Arguments for the command
                "@modelcontextprotocol/server-filesystem",
                TARGET_FOLDER_PATH],
          ),
          auth_config=None,
      ),
      tool_filter=['read_file', 'list_directory'], # Optional: filter specific tools
      # For remote servers, you would use SseConnectionParams instead:
      # connection_params=SseConnectionParams(url="http://remote-server:port/path", headers={...})
  )
  demo_agent = await SimpleAgent.create(tools=[toolset])
  await demo_agent.interact_async()
  await toolset.close()


if __name__ == '__main__':
  try:
    asyncio.run(async_main_interact())
  except Exception as e:
    print(f"An error occurred: {e}")
