#!/usr/bin/env python
import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.code_executors import BuiltInCodeExecutor
from google.genai import types


AGENT_NAME = "calculator_agent"
APP_NAME = "calculator"
USER_ID = "user1234"
SESSION_ID = "session_code_exec_async"
GEMINI_MODEL = "gemini-2.0-flash"


# Agent Definition
code_agent = LlmAgent(
    name=AGENT_NAME,
    model=GEMINI_MODEL,
    code_executor=BuiltInCodeExecutor(),
    instruction=(
        "You are a calculator agent."
        "When given a mathematical expression, "
        "write and execute Python code to calculate the result."
        "Return only the final numerical result as plain text, "
        "without markdown or code blocks."
    ),
    description="Executes Python code to perform calculations.",
)


# Session and Runner
async def setup_session_and_runner():
  # Session and Runner
  session_service = InMemorySessionService()
  session = await session_service.create_session(
      app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

  runner = Runner(
      agent=code_agent,
      app_name=APP_NAME,
      session_service=session_service)

  return session, runner


# Agent Interaction (Async)
async def call_agent_async(query):
  session, runner = await setup_session_and_runner()
  content = types.Content(role="user", parts=[types.Part(text=query)])
  print(f"\n--- Running Query: {query} ---")
  final_response_text = "No final text response captured."
  try:
    # Use run_async
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=content
    ):
      print(f"Event ID: {event.id}, Author: {event.author}")

      # --- Check for specific parts FIRST ---
      has_specific_part = False
      if event.content and event.content.parts:
        for part in event.content.parts:  # Iterate through all parts
          if part.executable_code:
            # Access the actual code string via .code
            print(
                f"  Debug: Agent generated code:\n"
                f"```python\n{part.executable_code.code}\n```")
            has_specific_part = True
          elif part.code_execution_result:
            # Access outcome and output correctly
            print(
                "  Debug: Code Execution Result: "
                f"{part.code_execution_result.outcome} - "
                f"Output:\n{part.code_execution_result.output}")
            has_specific_part = True
            # Also print any text parts found in any event for debugging
          elif part.text and not part.text.isspace():
            print(f"  Text: '{part.text.strip()}'")
            # Do not set has_specific_part=True here, as we want the final response logic below

          # --- Check for final response AFTER specific parts ---
          # Only consider it final if it doesn't have the specific code parts we just handled
          if not has_specific_part and event.is_final_response():
            if (
                event.content
                and event.content.parts
                and event.content.parts[0].text
            ):
              final_response_text = event.content.parts[0].text.strip()
              print(f"==> Final Agent Response: {final_response_text}")
            else:
              print("==> Final Agent Response: [No text content in final event]")

  except Exception as e:
    print(f"ERROR during agent run: {e}")
  print("-" * 30)


# Main async function to run the examples
async def main():
  await call_agent_async("Calculate the value of (5 + 7) * 3")
  await call_agent_async("What is 10 factorial?")


if __name__ == '__main__':
  # Execute the main async function
  try:
    asyncio.run(main())
  except RuntimeError as e:
    # Handle specific error when running asyncio.run in an already running loop (like Jupyter/Colab)
    if "cannot be called from a running event loop" in str(e):
      print("\nRunning in an existing event loop (like Colab/Jupyter).")
      print("Please run `await main()` in a notebook cell instead.")
      # If in an interactive environment like a notebook, you might need to run:
      # await main()
    else:
      raise e  # Re-raise other runtime errors
