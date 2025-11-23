"""AgentTool example.

Ref: https://google.github.io/adk-docs/agents/multi-agents/#c-explicit-invocation-agenttool
"""
import asyncio
import math
import random
from typing import ClassVar, Type

from google.adk.agents import Agent
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import agent_tool
from google.genai import types
from pydantic import BaseModel, Field


APP_NAME="summary_agent"
USER_ID="user1234"
SESSION_ID="1234"


async def roll_dice(n: int) -> int:
  """Roll the dice with n sides.

  Args:
    n: The number of side in a dice to roll.

  Returns:
    The rolling result.
  """
  print(f'Roll the dice with {n} sides...')
  return random.randint(1, n)


async def is_prime(number: int) -> bool:
  """Checks if the given `n` is prime or not.

  Args:
    number: The number to check if it is prime or not.

  Returns:
    True if the given `n` is prime. False otherwise.
  """
  # Numbers less than or equal to 1 are not prime
  if number <= 1:
    return False

  # 2 is the only even prime number
  if number == 2:
    return True

  # Exclude all other even numbers
  if number % 2 == 0:
    return False

  # Check for odd divisors from 3 up to the square root of the number
  limit = int(math.sqrt(number)) + 1
  for i in range(3, limit, 2):
    if number % i == 0:
      return False

  # If no factors were found, the number is prime
  return True


dice_agent = Agent(
    model='gemini-2.0-flash',
    name = "DiceRoll",
    description = (
        "Roll a dice with number from 1 to n and return the obtained number."
    ),
    instruction = "Roll the dice with sides `n` by request.",
    tools=[roll_dice],
)



dice_tool = agent_tool.AgentTool(agent=dice_agent) # Wrap the agent

root_agent = LlmAgent(
    name="GameAgent",
    model="gemini-2.5-pro",
    instruction="You are good at gaming and able to roll a dice.",
    tools=[
        dice_tool,  # Include the AgentTool
        is_prime,
    ]
)


# Session and Runner
async def setup_session_and_runner():
  session_service = InMemorySessionService()
  session = await session_service.create_session(
      app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
  runner = Runner(
      agent=root_agent, app_name=APP_NAME, session_service=session_service)
  return session, runner


# Agent Interaction
async def call_agent_async(query, debug: bool=False):
  content = types.Content(role='user', parts=[types.Part(text=query)])
  session, runner = await setup_session_and_runner()
  events = runner.run_async(
      user_id=USER_ID, session_id=SESSION_ID, new_message=content)

  final_response = '?'
  async for event in events:
    if event.is_final_response():
      final_response = event.content.parts[0].text
      # print("Agent Response: ", final_response)
    if debug:
     print(f"Event received: {event}")

  return final_response


if __name__ == '__main__':
  asyncio.run(
      call_agent_async(
          'Roll a dice with n as 100 twice and sum up the values. '
          'Finally, check if the final value is prime or not.', True))
