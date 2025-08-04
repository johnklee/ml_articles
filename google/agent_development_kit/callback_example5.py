#!/usr/bin/env python
import asyncio
from collections import namedtuple
from functools import cache
import time

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from typing import Optional
from google.genai import types
from google.adk.sessions import InMemorySessionService, Session
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from typing import Dict, Any, NamedTuple


GEMINI_2_FLASH="gemini-2.0-flash"
APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"


# Defined the namedtuple
class AgentEnv(NamedTuple):
  runner: Runner
  session: Session


def get_capital_city(country: str) -> str:
  """Retrieves the capital city of a given country."""
  print(f"--- Tool 'get_capital_city' executing with country: {country} ---")
  country_capitals = {
      "united states": "Washington, D.C.",
      "canada": "Ottawa",
      "france": "Paris",
      "germany": "Berlin",
      "taiwan": "taipei",
  }
  return country_capitals.get(
      country.lower(), f"Capital not found for {country}")


capital_tool = FunctionTool(func=get_capital_city)


def simple_before_tool_modifier(
    tool: BaseTool, args: Dict[str, Any],
    tool_context: ToolContext) -> Optional[Dict]:
  """Inspects/modifies tool args or skips the tool call."""
  agent_name = tool_context.agent_name
  tool_name = tool.name
  print(f"[Callback] Before tool call for tool '{tool_name}' in agent '{agent_name}'")
  print(f"[Callback] Original args: {args}")

  if tool_name == 'get_capital_city' and args.get('country', '').lower() == 'canada':
    print("[Callback] Detected 'Canada'. Modifying args to 'France'.")
    args['country'] = 'France'
    print(f"[Callback] Modified args: {args}")
    return None

  # If the tool is 'get_capital_city' and country is 'BLOCK'
  if tool_name == 'get_capital_city' and args.get('country', '').upper() == 'BLOCK':
    print("[Callback] Detected 'BLOCK'. Skipping tool execution.")
    return {"result": "Tool execution was blocked by `before_tool_callback`."}

  print("[Callback] Proceeding with original or previously modified args.")
  return None


my_llm_agent = LlmAgent(
    name="ToolCallbackAgent",
    model=GEMINI_2_FLASH,
    instruction="You are an agent that can find capital cities. Use the get_capital_city tool.",
    description="An LLM agent demonstrating before_tool_callback",
    tools=[capital_tool],
    before_tool_callback=simple_before_tool_modifier)


# Session and Runner
async def setup_session_and_runner():
  session_service = InMemorySessionService()
  session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
  runner = Runner(
      agent=my_llm_agent,
      app_name=APP_NAME,
      session_service=session_service)
  return AgentEnv(
      session=session,
      runner=runner)


# Agent Interaction
async def call_agent_async(query):
  content = types.Content(role='user', parts=[types.Part(text=query)])
  agent_env = await setup_session_and_runner()
  events = agent_env.runner.run_async(
      user_id=USER_ID, session_id=SESSION_ID, new_message=content)

  async for event in events:
    if event.is_final_response():
      final_response = event.content.parts[0].text
      print("Agent Response: ", final_response)


if __name__ == '__main__':
  asyncio.run(call_agent_async("Canada"))
