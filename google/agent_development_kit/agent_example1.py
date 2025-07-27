#!/usr/bin/env python
# --- Full example code demonstrating LlmAgent with Tools vs. Output Schema ---
import asyncio
import json # Needed for pretty printing dicts

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel, Field

# --- 1. Define Constants ---
APP_NAME = "agent_comparison_app"
USER_ID = "test_user_456"
SESSION_ID_TOOL_AGENT = "session_tool_agent_xyz"
SESSION_ID_SCHEMA_AGENT = "session_schema_agent_xyz"
MODEL_NAME = "gemini-2.0-flash"

# --- 2. Define Schemas ---

# Input schema used by both agents
class CountryInput(BaseModel):
  country: str = Field(description="The country to get information about.")

# Output schema ONLY for the second agent
class CapitalInfoOutput(BaseModel):
  capital: str = Field(description="The capital city of the country.")
  # Note: Population is illustrative; the LLM will infer or estimate this
  # as it cannot use tools when output_schema is set.
  population_estimate: str = Field(
      description="An estimated population of the capital city.")

# --- 3. Define the Tool (Only for the first agent) ---
def get_capital_city(country: str) -> str:
  """Retrieves the capital city of a given country."""
  print(f"\n-- Tool Call: get_capital_city(country='{country}') --")
  country_capitals = {
      "united states": "Washington, D.C.",
      "canada": "Ottawa",
      "france": "Paris",
      "japan": "Tokyo",
      "taiwan": "Taipei",
  }
  result = country_capitals.get(
      country.lower(), f"Sorry, I couldn't find the capital for {country}.")
  print(f"-- Tool Result: '{result}' --")
  return result

# --- 4. Configure Agents ---

# Agent 1: Uses a tool and output_key
capital_agent_with_tool = LlmAgent(
    model=MODEL_NAME,
    name="capital_agent_tool",
    description="Retrieves the capital city using a specific tool.",
    instruction="""
You are a helpful agent to provide the capital city of a country using a tool.
The user will provide the country name in a JSON format like {"country": "country_name"}.

1. Extract the country name.
2. Use the `get_capital_city` tool to find the capital.
3. Respond clearly to the user, stating the capital city found by the tool.
""",
    tools=[get_capital_city],
    input_schema=CountryInput,
    output_key="capital_tool_result", # Store final text response
)

# Agent 2: Uses output_schema (NO tools possible)
structured_info_agent_schema = LlmAgent(
    model=MODEL_NAME,
    name="structured_info_agent_schema",
    description=(
        "Provides capital and estimated population in a specific JSON format."),
    instruction=f"""
You are an agent that provides country information.
The user will provide the country name in a JSON format like
{{"country": "country_name"}}.

Respond ONLY with a JSON object matching this exact schema:
{json.dumps(CapitalInfoOutput.model_json_schema(), indent=2)}
Use your knowledge to determine the capital and estimate the population.

Do not use any tools.
""",
    # *** NO tools parameter here - using output_schema prevents tool use ***
    input_schema=CountryInput,
    output_schema=CapitalInfoOutput, # Enforce JSON output structure
    output_key="structured_info_result", # Store final JSON response
)


# --- 6. Define Agent Interaction Logic ---
async def call_agent_and_print(
    runner_instance: Runner,
    agent_instance: LlmAgent,
    session_service: InMemorySessionService,
    session_id: str,
    query_json: str,
):
  """Sends a query to the specified agent/runner and prints results."""
  print(f"\n>>> Calling Agent: '{agent_instance.name}' | Query: {query_json}")

  user_content = types.Content(
      role='user', parts=[types.Part(text=query_json)])

  final_response_content = "No final response received."
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
  try:
    # Attempt to parse and pretty print if it's JSON
    parsed_output = json.loads(stored_output)
    print(json.dumps(parsed_output, indent=2))
  except (json.JSONDecodeError, TypeError):
    # Otherwise, print as string
    print(stored_output)
  print("-" * 30)


# --- 7. Run Interactions ---
async def main(capital_runner, structured_runner, session_service):
  print("--- Testing Agent with Tool ---")
  await call_agent_and_print(
      capital_runner,
      capital_agent_with_tool,
      session_service,
      SESSION_ID_TOOL_AGENT,
      '{"country": "Taiwan"}')

  await call_agent_and_print(
      capital_runner,
      capital_agent_with_tool,
      session_service,
      SESSION_ID_TOOL_AGENT,
      '{"country": "Canada"}')

  print("\n\n--- Testing Agent with Output Schema (No Tool Use) ---")
  await call_agent_and_print(
      structured_runner,
      structured_info_agent_schema,
      session_service,
      SESSION_ID_SCHEMA_AGENT,
      '{"country": "France"}')
  await call_agent_and_print(
      structured_runner,
      structured_info_agent_schema,
      session_service,
      SESSION_ID_SCHEMA_AGENT,
      '{"country": "Japan"}')


def create_runners():
  # --- 5. Set up Session Management and Runners ---
  session_service = InMemorySessionService()
  print(f'session_service: {session_service.__class__}')

  # Create separate sessions for clarity, though not strictly necessary if context is managed
  asyncio.run(session_service.create_session(
      app_name=APP_NAME,
      user_id=USER_ID,
      session_id=SESSION_ID_TOOL_AGENT))

  asyncio.run(session_service.create_session(
      app_name=APP_NAME,
      user_id=USER_ID,
      session_id=SESSION_ID_SCHEMA_AGENT))

  # Create a runner for EACH agent
  capital_runner = Runner(
      agent=capital_agent_with_tool,
      app_name=APP_NAME,
      session_service=session_service
  )
  structured_runner = Runner(
      agent=structured_info_agent_schema,
      app_name=APP_NAME,
      session_service=session_service
  )
  return capital_runner, structured_runner, session_service


if __name__ == "__main__":
  capital_runner, structured_runner, session_service = create_runners()
  asyncio.run(main(capital_runner, structured_runner, session_service))
