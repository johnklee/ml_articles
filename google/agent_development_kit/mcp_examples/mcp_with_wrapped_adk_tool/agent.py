#!/usr/bin/env python
import os
import pathlib

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams, StdioServerParameters

Path = pathlib.Path

# IMPORTANT: Replace this with the ABSOLUTE path to your my_adk_mcp_server.py script
PATH_TO_YOUR_MCP_SERVER_SCRIPT = str(
    Path(os.path.dirname(os.path.abspath(__file__))) /
    Path('my_adk_mcp_server.py'))


if not os.path.isfile(PATH_TO_YOUR_MCP_SERVER_SCRIPT):
  raise Exception(
      f'MCP server script does not exist: {PATH_TO_YOUR_MCP_SERVER_SCRIPT}')


root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='web_reader_mcp_client_agent',
    instruction=(
        "Use the 'load_web_page' tool to fetch content from a URL provided by "
        "the user."),
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='python', # Command to run your MCP server script
                    args=[PATH_TO_YOUR_MCP_SERVER_SCRIPT], # Argument is the path to the script
                )
            )
            # tool_filter=['load_web_page'] # Optional: ensure only specific tools are loaded
        )
    ],
)
