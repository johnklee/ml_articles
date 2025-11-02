#!/usr/bin/env python
"""Single agent example1"""
import asyncio
import json # Needed for pretty printing dicts
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel, Field


# --- 1. Define Constants ---
APP_NAME = "agent_sentimental_analysis_app"
USER_ID = "test_user_456"
SESSION_TEST_ID = "session_test_id"
MODEL_NAME = "gemini-2.0-flash"


# --- 2. Define Schemas ---
# Output schema ONLY for the second agent
class SentimentalAnalysisResult(BaseModel):
  word_count: int = Field(
      description=(
          "Number of words in the source text. Call the tool `count_word` "
          "to get this value."))
  result: str = Field(
      description=(
          "Sentimental analysis result. Could be: "
          "- `Positive`: The text carries more positive sentiment like 'Good', 'Great' etc.\n"
          "- `Neutral`: The text carries no good nor bad feeling.\n"
          "- `Negative`: The text carries more negative sentiment like 'Bad', 'Sucks' etc.\n"
          "This field can only be one of above three value only."))
  reason: str = Field(description="The reason of given sentimental result.")


# --- 3. Define the Tool(s) ---
def count_word(text: str) -> dict[str, Any]:
  """Count the words from the given `text`.

  Args:
    text: Input text for analysis.

  Returns:
    `dict` with key definition as below:
    - status: "pass" means the operaiton is successful.
    - count: The number of word counted from the given `text`.
  """
  return {
      'status': 'pass',
      'count': len(text.split(' ')),
  }


# --- 4. Configure Agents ---
# Agent 1: Uses a tool and output_key
sentimental_analysis_agent = LlmAgent(
    model=MODEL_NAME,
    name="sentimental_analysis_agent",
    description="Analyze the sentiment and count the word from the given text.",
    instruction="""
You are a helpful agent to analyze the given text for:
1. Count the word in the given text.
2. Analyze the sentiment of the given text.
""",
    tools=[count_word],
    output_schema=SentimentalAnalysisResult,
    output_key="sentimental_result", # Store final text response
)

async def create_runners():
  # --- 5. Set up Session Management and Runners ---
  session_service = InMemorySessionService()
  print(f'session_service: {session_service.__class__}')

  # Create separate sessions for clarity, though not strictly necessary if context is managed
  #asyncio.run(session_service.create_session(
  #    app_name=APP_NAME,
  #    user_id=USER_ID,
  #    session_id=SESSION_TEST_ID))

  await session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_TEST_ID)

  # Create a runner for EACH agent
  runner = Runner(
      agent=sentimental_analysis_agent,
      app_name=APP_NAME,
      session_service=session_service
  )
  return runner, session_service


# --- 6. Define Agent Interaction Logic ---
async def call_agent_and_print(
    text: str,
    runner_instance: Runner,
    session_service: InMemorySessionService,
    agent_instance: LlmAgent = sentimental_analysis_agent,
    session_id: str = SESSION_TEST_ID,
):
  """Sends a query to the specified agent/runner and prints results."""
  print(f"\n>>> Calling Agent: '{agent_instance.name}' | Query: {text}")

  user_content = types.Content(
      role='user', parts=[types.Part(text=text)])

  async for event in runner_instance.run_async(
      user_id=USER_ID,
      session_id=session_id,
      new_message=user_content):
    # print(f"Event: {event.type}, Author: {event.author}") # Uncomment for detailed logging
    if event.is_final_response() and event.content and event.content.parts:
      # For output_schema, the content is the JSON string itself
      final_response_content = event.content.parts[0].text

  print(f"<<< Agent '{agent_instance.name}' Response: {final_response_content}")

  current_session = await session_service.get_session(
      app_name=APP_NAME,
      user_id=USER_ID,
      session_id=session_id)

  stored_output = current_session.state.get(agent_instance.output_key)

  # Pretty print if the stored output looks like JSON (likely from output_schema)
  print(f"--- Session State ['{agent_instance.output_key}']: ", end="")
  print(stored_output)
  print("-" * 30)

async def call_agent(
    text: str,
    runner_instance: Runner,
    session_service: InMemorySessionService,
    agent_instance: LlmAgent = sentimental_analysis_agent,
    session_id: str = SESSION_TEST_ID,
):
  user_content = types.Content(
      role='user', parts=[types.Part(text=text)])
  async for event in runner_instance.run_async(
      user_id=USER_ID,
      session_id=session_id,
      new_message=user_content):
    pass

  current_session = await session_service.get_session(
      app_name=APP_NAME,
      user_id=USER_ID,
      session_id=session_id)
  return current_session.state.get(agent_instance.output_key)


# --- 7. Run Interactions ---
async def main():
  runner, session_service = await create_runners()
  print("--- Testing Agent  ---")
  await call_agent_and_print(
      "This movie is absolute awesome!",
      runner,
      session_service)


if __name__ == "__main__":
  asyncio.run(main())
