#!/usr/bin/env python
import asyncio
from functools import cache
import time

# ADK Imports
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import InMemoryRunner, Runner  # Use InMemoryRunner
from google.genai import types # For types.Content
from typing import Optional, NamedTuple

# Define the model - Use the specific model name requested
GEMINI_2_FLASH="gemini-2.0-flash"


# Defined the namedtuple
class AgentEnv(NamedTuple):
  app_name: str
  user_id: str
  session_id_normal: str
  session_id_modify: str
  runner: Runner


# --- 1. Define the Callback Function ---
def modify_output_after_agent(callback_context: CallbackContext) -> Optional[types.Content]:
  """
  Logs exit from an agent and checks 'add_concluding_note' in session state.
  If True, returns new Content to *replace* the agent's original output.
  If False or not present, returns None, allowing the agent's original output to be used.
  """
  agent_name = callback_context.agent_name
  invocation_id = callback_context.invocation_id
  current_state = callback_context.state.to_dict()

  print(f"\n[Callback] Exiting agent: {agent_name} (Inv: {invocation_id})")
  print(f"[Callback] Current State: {current_state}")

  # Example: Check state to decide whether to modify the final output
  if current_state.get("add_concluding_note", False):
    print(f"[Callback] State condition 'add_concluding_note=True' met: Replacing agent {agent_name}'s output.")
    # Return Content to *replace* the agent's own output
    return types.Content(
        parts=[types.Part(text=f"Concluding note added by `after_agent_callback`, replacing original output.")],
        role="model" # Assign model role to the overriding response
    )
  else:
    print(f"[Callback] State condition not met: Using agent {agent_name}'s original output.")
    # Return None - the agent's output produced just before this callback will be used.
    return None


# --- 2. Setup Agent with Callback ---
llm_agent_with_after_cb = LlmAgent(
    name="MySimpleAgentWithAfter",
    model=GEMINI_2_FLASH,
    instruction="You are a simple agent. Just say 'Processing complete!'",
    description="An LLM agent demonstrating after_agent_callback for output modification",
    after_agent_callback=modify_output_after_agent # Assign the callback here
)


@cache
async def initialize_session_and_runner():
  app_name = "before_agent_demo"
  user_id = "test_user"
  session_id_normal = "session_run_normally"
  session_id_modify = "session_modify_output"

  # Use InMemoryRunner - it includes InMemorySessionService
  runner = InMemoryRunner(agent=llm_agent_with_after_cb, app_name=app_name)
  # Get the bundled session service to create sessions
  session_service = runner.session_service

  # Create session 1: Agent will run (default empty state)
  await session_service.create_session(
      app_name=app_name,
      user_id=user_id,
      session_id=session_id_normal
      # No initial state means 'skip_llm_agent' will be False in the callback check
  )

  # Create session 2: Agent will be skipped (state has skip_llm_agent=True)
  await session_service.create_session(
      app_name=app_name,
      user_id=user_id,
      session_id=session_id_modify,
      state={"add_concluding_note": True} # Set the state flag here
  )

  return AgentEnv(
      app_name=app_name,
      user_id=user_id,
      session_id_normal=session_id_normal,
      session_id_modify=session_id_modify,
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

  # --- Scenario 1: Run where callback allows agent's original output ---
  print(
      "\n" + "="*20 +
      f" SCENARIO 1: Running Agent on Session '{agent_env.session_id_normal}' " +
      "(Should Use Original Output) " + "="*20)
  await query(
      'Process this please.',
      agent_env,
      agent_env.session_id_normal)

  # --- Scenario 2: Run where callback replaces the agent's output ---
  print(
      "\n" + "="*20 +
      f" SCENARIO 2: Running Agent on Session '{agent_env.session_id_modify}' " +
      "(Should Replace Output) " + "="*20)
  await query(
      'Process this and add note.',
      agent_env,
      agent_env.session_id_modify)


if __name__ == '__main__':
  asyncio.run(main())
