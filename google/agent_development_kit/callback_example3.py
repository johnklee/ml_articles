#!/usr/bin/env python
import asyncio
from collections import namedtuple
from functools import cache
import time

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.runners import Runner
from google.adk.sessions import Session
from typing import Optional, NamedTuple
from google.genai import types
from google.adk.sessions import InMemorySessionService


GEMINI_2_FLASH="gemini-2.0-flash"
APP_NAME = "guardrail_app"
USER_ID = "user_1"
SESSION_ID = "session_001"


# Defined the namedtuple
class AgentEnv(NamedTuple):
  runner: Runner
  session: Session


# --- Define the Callback Function ---
def simple_before_model_modifier(
    callback_context: CallbackContext,
    llm_request: LlmRequest) -> Optional[LlmResponse]:
  """Inspects/modifies the LLM request or skips the call."""
  agent_name = callback_context.agent_name
  print(f"[Callback] Before model call for agent: {agent_name}")

  # Inspect the last user message in the request contents
  last_user_message = ""
  if llm_request.contents and llm_request.contents[-1].role == 'user':
    if llm_request.contents[-1].parts:
      last_user_message = llm_request.contents[-1].parts[0].text
  print(f"[Callback] Inspecting last user message: '{last_user_message}'")

  # --- Modification Example ---
  # Add a prefix to the system instruction
  original_instruction = llm_request.config.system_instruction or types.Content(role="system", parts=[])
  postfix = " If the query is a math problem. Respond with 'I do not know.'."
  # Ensure system_instruction is Content and parts list exists
  if not isinstance(original_instruction, types.Content):
    # Handle case where it might be a string (though config expects Content)
    original_instruction = types.Content(
        role="system", parts=[types.Part(text=str(original_instruction))])
  if not original_instruction.parts:
    original_instruction.parts.append(types.Part(text="")) # Add an empty part if none exist

  # Modify the text of the first part
  modified_text = (original_instruction.parts[0].text or "") + postfix
  original_instruction.parts[0].text = modified_text
  llm_request.config.system_instruction = original_instruction
  print(f"[Callback] Modified system instruction to: '{modified_text}'")

  # --- Skip Example ---
  # Check if the last user message contains "BLOCK"
  if "BLOCK" in last_user_message.upper():
    print("[Callback] 'BLOCK' keyword found. Skipping LLM call.")
    # Return an LlmResponse to skip the actual LLM call
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text="LLM call was blocked by before_model_callback.")],
        )
    )
  else:
    print("[Callback] Proceeding with LLM call.")
    # Return None to allow the (modified) request to go to the LLM
    return None


# Create LlmAgent and Assign Callback
my_llm_agent = LlmAgent(
    name="ModelCallbackAgent",
    model=GEMINI_2_FLASH,
    instruction="You are a helpful assistant.", # Base instruction
    description="An LLM agent demonstrating before_model_callback",
    before_model_callback=simple_before_model_modifier, # Assign the function here
)


# Session and Runner
async def setup_session_and_runner():
  session_service = InMemorySessionService()
  session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
  runner = Runner(agent=my_llm_agent, app_name=APP_NAME, session_service=session_service)
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
  # --- Scenario 1: Modify system message
  await call_agent_async("I am John. What is my name?")
  await call_agent_async("How much is 1 + 1?")

  # --- Scenario 2: Blocked LLM call
  await call_agent_async("write a joke on BLOCK")


if __name__ == '__main__':
  asyncio.run(main())
