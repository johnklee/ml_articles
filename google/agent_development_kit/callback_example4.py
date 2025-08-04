#!/usr/bin/env python
import asyncio
from collections import namedtuple
import copy
from functools import cache
import time

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import Runner
from google.adk.sessions import Session
from typing import Optional, NamedTuple
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.models import LlmResponse


GEMINI_2_FLASH="gemini-2.0-flash"
APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"


# Defined the namedtuple
class AgentEnv(NamedTuple):
  runner: Runner
  session: Session


# --- Define the Callback Function ---
def simple_after_model_modifier(
    callback_context: CallbackContext,
    llm_response: LlmResponse) -> Optional[LlmResponse]:
  """Inspects/modifies the LLM response after it's received."""
  agent_name = callback_context.agent_name
  print(f"[Callback] After model call for agent: {agent_name}")

  # --- Inspection ---
  original_text = ""
  if llm_response.content and llm_response.content.parts:
    # Assuming simple text response for this example
    if llm_response.content.parts[0].text:
      original_text = llm_response.content.parts[0].text
      print(
          "[Callback] Inspected original response text: "
          f"'{original_text[:100]}'...") # Log snippet
    elif llm_response.content.parts[0].function_call:
      print(
          "[Callback] Inspected response: Contains function call "
          "'{llm_response.content.parts[0].function_call.name}'. No text modification.")
      return None  # Don't modify tool calls in this example
    else:
      print("[Callback] Inspected response: No text content found.")
      return None
  elif llm_response.error_message:
    print(
        "[Callback] Inspected response: Contains error "
        f"'{llm_response.error_message}'. No modification.")
    return None
  else:
    print("[Callback] Inspected response: Empty LlmResponse.")
    return None # Nothing to modify

  # --- Modification Example ---
  # Replace "joke" with "funny story" (case-insensitive)
  search_term = "joke"
  replace_term = "funny story"
  if search_term in original_text.lower():
    print(f"[Callback] Found '{search_term}'. Modifying response.")
    modified_text = original_text.replace(search_term, replace_term)
    modified_text = modified_text.replace(
        search_term.capitalize(), replace_term.capitalize())  # Handle capitalization

    # Create a NEW LlmResponse with the modified content
    # Deep copy parts to avoid modifying original if other callbacks exist
    modified_parts = [copy.deepcopy(part) for part in llm_response.content.parts]
    modified_parts[0].text = modified_text # Update the text in the copied part

    new_response = LlmResponse(
        content=types.Content(role="model", parts=modified_parts),
        # Copy other relevant fields if necessary, e.g., grounding_metadata
        grounding_metadata=llm_response.grounding_metadata)
    print(f"[Callback] Returning modified response.")
    return new_response # Return the modified response
  else:
    print(f"[Callback] '{search_term}' not found. Passing original response through.")
    # Return None to use the original llm_response
    return None


# Create LlmAgent and Assign Callback
my_llm_agent = LlmAgent(
    name="AfterModelCallbackAgent",
    model=GEMINI_2_FLASH,
    instruction="You are a helpful assistant.",
    description="An LLM agent demonstrating after_model_callback",
    after_model_callback=simple_after_model_modifier # Assign the function here
)


# Session and Runner
async def setup_session_and_runner():
  session_service = InMemorySessionService()
  session = await session_service.create_session(
      app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
  runner = Runner(
      agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
  return AgentEnv(runner=runner, session=session)


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


async def main():
  await call_agent_async('Write two time the word "joke"')
  await call_agent_async('Write three time the word "john"')


if __name__ == '__main__':
  asyncio.run(main())
