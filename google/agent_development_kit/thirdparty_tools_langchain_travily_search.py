#!/usr/bin/env python
import asyncio
import os

from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.langchain_tool import LangchainTool
from google.genai import types
from langchain_tavily import TavilySearch


TAVILY_API_KEY = None
# Ensure TAVILY_API_KEY is set in your environment
if not (TAVILY_API_KEY := os.getenv("TAVILY_API_KEY")):
  raise Exception("Error: TAVILY_API_KEY environment variable not set.")

print(f'TRAVILY_API_KEY: {"*" * len(TAVILY_API_KEY)}')


APP_NAME = "news_app"
USER_ID = "1234"
SESSION_ID = "session1234"


# Instantiate LangChain tool
tavily_search = TavilySearch(
    max_results=5,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True,
    include_images=True)


# Wrap with LangchainTool
adk_tavily_tool = LangchainTool(tool=tavily_search)


# Define Agent with the wrapped tool
my_agent = Agent(
    name="langchain_tool_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions using TavilySearch.",
    instruction=(
        "I can answer your questions by searching the internet. "
        "Just ask me anything!"),
    tools=[adk_tavily_tool] # Add the wrapped tool here
)


async def setup_session_and_runner():
  session_service = InMemorySessionService()
  session = await session_service.create_session(
      app_name=APP_NAME,
      user_id=USER_ID,
      session_id=SESSION_ID)
  runner = Runner(
      agent=my_agent,
      app_name=APP_NAME,
      session_service=session_service)

  return session, runner


# Agent Interaction
async def call_agent_async(query):
  content = types.Content(role='user', parts=[types.Part(text=query)])
  session, runner = await setup_session_and_runner()
  events = runner.run_async(
      user_id=USER_ID, session_id=SESSION_ID, new_message=content)

  async for event in events:
    if event.is_final_response():
      final_response = event.content.parts[0].text
      print("Agent Response: ", final_response)


if __name__ == '__main__':
  asyncio.run(call_agent_async('Stock price of GOOG'))
