#!/usr/bin/env python
import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.agent_tool import AgentTool
from google.genai import types


APP_NAME="summary_agent"
USER_ID="user1234"
SESSION_ID="1234"

summary_agent = Agent(
    model="gemini-2.0-flash",
    name="summary_agent",
    instruction=(
        "You are an expert summarizer. Please read the given text and "
        "provide a concise summary in 3-4 sentences with the prefix `[Summary]`"
        " as response."),
    description="Agent to summarize text")

root_agent = Agent(
    model='gemini-2.0-flash',
    name='root_agent',
    instruction=(
        "You are a helpful assistant. When the user provides a text, use the "
        "'summary_agent' tool to generate a summary. Always forward the user's "
        "message exactly as received to the 'summary_agent' tool without modifying."
        "Present the response from the tool to the"
        " user without modifying too."),
    tools=[AgentTool(agent=summary_agent)])

# Session and Runner
async def setup_session_and_runner():
  session_service = InMemorySessionService()
  session = await session_service.create_session(
      app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
  runner = Runner(
      agent=root_agent, app_name=APP_NAME, session_service=session_service)
  return session, runner


# Agent Interaction
async def call_agent_async(query):
  content = types.Content(role='user', parts=[types.Part(text=query)])
  session, runner = await setup_session_and_runner()
  events = runner.run_async(
      user_id=USER_ID, session_id=SESSION_ID, new_message=content)

  async for event in events:
    #if event.is_final_response():
    #  final_response = event.content.parts[0].text
    #  print("Agent Response: ", final_response)
    print(f"Event received: {event}")


if __name__ == '__main__':
  long_text = """
  Quantum computing represents a fundamentally different approach to computation,
  leveraging the bizarre principles of quantum mechanics to process information.
  Unlike classical computers that rely on bits representing either 0 or 1,
  quantum computers use qubits which can exist in a state of superposition -
  effectively being 0, 1, or a combination of both simultaneously. Furthermore,
  qubits can become entangled, meaning their fates are intertwined regardless of
  distance, allowing for complex correlations. This parallelism and
  interconnectedness grant quantum computers the potential to solve specific types
  of incredibly complex problems - such as drug discovery, materials science,
  complex system optimization, and breaking certain types of cryptography - far
  faster than even the most powerful classical supercomputers could ever achieve,
  although the technology is still largely in its developmental stages."""
  asyncio.run(call_agent_async(long_text))
