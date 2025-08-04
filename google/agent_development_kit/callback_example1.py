#!/usr/bin/env python
import asyncio
from collections import namedtuple
from functools import cache
import time

# ADK Imports
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import InMemoryRunner, Runner  # Use InMemoryRunner
from google.adk.sessions import Session
from google.genai import types # For types.Content
from typing import Optional, NamedTuple


# Define the model - Use the specific model name requested
GEMINI_2_FLASH="gemini-2.0-flash"

# Defined the namedtuple
class AgentEnv(NamedTuple):
  app_name: str
  user_id: str
  session_id_run: str
  session_id_skip: str
  runner: Runner


# --- 1. Define the Callback Function ---
def check_if_agent_should_run(callback_context: CallbackContext) -> Optional[types.Content]:
  """
  Logs entry and checks 'skip_llm_agent' in session state.
  If True, returns Content to skip the agent's execution.
  If False or not present, returns None to allow execution.
  """
  agent_name = callback_context.agent_name
  invocation_id = callback_context.invocation_id
  current_state = callback_context.state.to_dict()

  print(f"\n[Callback] Entering agent: {agent_name} (Inv: {invocation_id})")
  print(f"[Callback] Current State: {current_state}")

  # Check the condition in session state dictionary
  if current_state.get("skip_llm_agent", False):
    print(f"[Callback] State condition 'skip_llm_agent=True' met: Skipping agent {agent_name}.")
    # Return Content to skip the agent's run
    return types.Content(
        parts=[types.Part(text=f"Agent {agent_name} skipped by `before_agent_callback` due to state.")],
        role="model" # Assign model role to the overriding response
    )

  print(f"[Callback] State condition not met: Proceeding with agent {agent_name}.")
  # Return None to allow the LlmAgent's normal execution
  return None


# --- 2. Setup Agent with Callback ---
llm_agent_with_before_cb = LlmAgent(
    name="MyControlledAgent",
    model=GEMINI_2_FLASH,
    instruction="You are a concise assistant.",
    description="An LLM agent demonstrating stateful before_agent_callback",
    before_agent_callback=check_if_agent_should_run # Assign the callback
)


@cache
async def initialize_session_and_runner():
  app_name = "before_agent_demo"
  user_id = "test_user"
  session_id_run = "session_will_run"
  session_id_skip = "session_will_skip"

  # Use InMemoryRunner - it includes InMemorySessionService
  runner = InMemoryRunner(agent=llm_agent_with_before_cb, app_name=app_name)
  # Get the bundled session service to create sessions
  session_service = runner.session_service

  # Create session 1: Agent will run (default empty state)
  await session_service.create_session(
      app_name=app_name,
      user_id=user_id,
      session_id=session_id_run
      # No initial state means 'skip_llm_agent' will be False in the callback check
  )

  # Create session 2: Agent will be skipped (state has skip_llm_agent=True)
  await session_service.create_session(
      app_name=app_name,
      user_id=user_id,
      session_id=session_id_skip,
      state={"skip_llm_agent": True} # Set the state flag here
  )

  return AgentEnv(
      app_name=app_name,
      user_id=user_id,
      session_id_run=session_id_run,
      session_id_skip=session_id_skip,
      runner=runner)


async def query(text: str, agent_env, session_id):
  start_time = time.time()
  async for event in agent_env.runner.run_async(
      user_id=agent_env.user_id,
      session_id=session_id,
      new_message=types.Content(
          role="user", parts=[types.Part(text=text)])
  ):
    # Print final output (either from LLM or callback override)
    if event.is_final_response() and event.content:
      print(f"Final Output: [{event.author}] {event.content.parts[0].text.strip()}")
    elif event.is_error():
      print(f"Error Event: {event.error_details}")

  spent_time_sec = time.time() - start_time
  print(f'[Query] Spent time {spent_time_sec:.02f}s!')


async def main():
  agent_env = await initialize_session_and_runner()

  # --- Scenario 1: Run where callback allows agent execution ---
  await query(
      'Hello, please respond.',
      agent_env,
      agent_env.session_id_run)

  # --- Scenario 2: Run where callback intercepts and skips agent ---
  await query(
      "This message won't reach the LLM.",
      agent_env,
      agent_env.session_id_skip)


if __name__ == '__main__':
  asyncio.run(main())
