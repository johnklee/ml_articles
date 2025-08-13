#!/usr/bin/env python
import pathlib
import os
import asyncio

from dotenv import find_dotenv, load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # Optional
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams, StdioConnectionParams, StdioServerParameters


Path = pathlib.Path

# --- Load Environment Variables (If ADK tools need them, e.g., API keys) ---
_ = load_dotenv(find_dotenv(os.path.expanduser('~/.env'))) # read local .env file


# IMPORTANT: Replace this with the ABSOLUTE path to your my_adk_mcp_server.py script
TARGET_FOLDER_PATH = (
    str(Path(os.path.dirname(os.path.abspath(__file__))) / Path('mcp_examples/mcp_filesystem/test/')))


# --- Step 1: Agent Definition ---
async def get_agent_async():
  """Creates an ADK Agent equipped with tools from the MCP Server."""
  toolset = MCPToolset(
      # Use StdioConnectionParams for local process communication
      connection_params=StdioConnectionParams(
          server_params = StdioServerParameters(
            command='npx', # Command to run the server
            args=["-y",    # Arguments for the command
                "@modelcontextprotocol/server-filesystem",
                TARGET_FOLDER_PATH],
          ),
      ),
      tool_filter=['read_file', 'list_directory'] # Optional: filter specific tools
      # For remote servers, you would use SseConnectionParams instead:
      # connection_params=SseConnectionParams(url="http://remote-server:port/path", headers={...})
  )

  # Use in an agent
  root_agent = LlmAgent(
      model='gemini-2.0-flash', # Adjust model name if needed based on availability
      name='enterprise_assistant',
      instruction='Help user accessing their file systems',
      tools=[toolset], # Provide the MCP tools to the ADK agent
  )
  return root_agent, toolset


# --- Step 2: Main Execution Logic ---
async def async_main():
  session_service = InMemorySessionService()
  # Artifact service might not be needed for this example
  artifacts_service = InMemoryArtifactService()

  session = await session_service.create_session(
      state={}, app_name='mcp_filesystem_app', user_id='user_fs'
  )

  # TODO: Change the query to be relevant to YOUR specified folder.
  # e.g., "list files in the 'documents' subfolder" or "read the file 'notes.txt'"
  query = f"list files in the path {TARGET_FOLDER_PATH}"
  print(f"User Query: '{query}'")
  content = types.Content(role='user', parts=[types.Part(text=query)])

  root_agent, toolset = await get_agent_async()

  runner = Runner(
      app_name='mcp_filesystem_app',
      agent=root_agent,
      artifact_service=artifacts_service, # Optional
      session_service=session_service,
  )

  print("Running agent...")
  events_async = runner.run_async(
      session_id=session.id, user_id=session.user_id, new_message=content
  )

  async for event in events_async:
    if event.is_final_response():
      final_response = event.content.parts[0].text
      print("Agent Response: ", final_response)

  # Cleanup is handled automatically by the agent framework
  # But you can also manually close if needed:
  print("Closing MCP server connection...")
  await toolset.close()
  print("Cleanup complete.")


if __name__ == '__main__':
  try:
    asyncio.run(async_main())
  except Exception as e:
    print(f"An error occurred: {e}")
