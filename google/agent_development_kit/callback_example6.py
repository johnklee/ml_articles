#!/usr/bin/env python
import asyncio
from collections import namedtuple
from copy import deepcopy
from functools import cache
import time

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from typing import Any, Dict, Optional, NamedTuple
from google.genai import types
from google.adk.models import LlmResponse
from google.adk.tools.base_tool import BaseTool


GEMINI_2_FLASH="gemini-2.0-flash"
APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"


# Defined the namedtuple
class AgentEnv(NamedTuple):
  runner: Runner
  session: Session


# --- Define a Simple Tool Function (Same as before) ---
def get_capital_city(country: str) -> Dict[str, Any]:
  """Retrieves the capital city of a given country."""
  print(f"--- Tool 'get_capital_city' executing with country: {country} ---")
  country_capitals = {
      "united states": "Washington, D.C.",
      "canada": "Ottawa",
      "france": "Paris",
      "germany": "Berlin",
      "taiwan": "taipei",
  }

  return {
      "result": country_capitals.get(country.lower(), f"Capital not found for {country}")}


# --- Wrap the function into a Tool ---
capital_tool = FunctionTool(func=get_capital_city)


# --- Define the Callback Function ---
def simple_after_tool_modifier(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
    tool_response: Dict
) -> Optional[Dict]:
  """Inspects/modifies the tool result after execution."""
  agent_name = tool_context.agent_name
  tool_name = tool.name
  print(f"[Callback] After tool call for tool '{tool_name}' in agent '{agent_name}'")
  print(f"[Callback] Args used: {args}")
  print(f"[Callback] Original tool_response: {tool_response}")

  # Default structure for function tool results is {"result": <return_value>}
  original_result_value = tool_response.get("result", "")
  # original_result_value = tool_response

  # --- Modification Example ---
  # If the tool was 'get_capital_city' and result is 'Washington, D.C.'
  if tool_name == 'get_capital_city' and original_result_value == "Washington, D.C.":
    print("[Callback] Detected 'Washington, D.C.'. Modifying tool response.")

    # IMPORTANT: Create a new dictionary or modify a copy
    modified_response = deepcopy(tool_response)
    modified_response["result"] = f"{original_result_value} (Note: This is the capital of the USA)."
    modified_response["note_added_by_callback"] = True # Add extra info if needed

    print(f"[Callback] Modified tool_response: {modified_response}")
    return modified_response # Return the modified dictionary

  print("[Callback] Passing original tool response through.")
  # Return None to use the original tool_response
  return None


# Create LlmAgent and Assign Callback
my_llm_agent = LlmAgent(
    name="AfterToolCallbackAgent",
    model=GEMINI_2_FLASH,
    instruction="You are an agent that finds capital cities using the get_capital_city tool. Report the result clearly.",
    description="An LLM agent demonstrating after_tool_callback",
    tools=[capital_tool], # Add the tool
    after_tool_callback=simple_after_tool_modifier, # Assign the callback
)


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
  asyncio.run(call_agent_async("united states"))
