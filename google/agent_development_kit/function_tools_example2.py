#!/usr/bin/env python
import asyncio

from typing import Any
from google.adk.agents import Agent
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.tools import LongRunningFunctionTool
from google.adk.sessions import InMemorySessionService
from google.genai import types


APP_NAME = "human_in_the_loop"
USER_ID = "1234"
SESSION_ID = "session1234"


# 1. Define the long running function
def ask_for_approval(purpose: str, amount: float) -> dict[str, Any]:
  """Ask for approval for the reimbursement.

  Args:
    purpose: The purpose of the approval.
    amount: The amount for approval.

  Returns:
    dict object with keys:
    - status: The approval status.
    - approver: The people to ask for approval,
    - purpose: The copy of input `purpose`.
    - amount: The copy of input `amount`.
    - ticket-id: The id of fired ticket.
  """
  # create a ticket for the approval
  # Send a notification to the approver with the link of the ticket
  return {
      'status': 'pending',
      'approver': 'Sean Zhou',
      'purpose' : purpose,
      'amount': amount,
      'ticket-id': 'approval-ticket-1'
  }


def reimburse(purpose: str, amount: float) -> dict[str, Any]:
  """Reimburse the amount of money to the employee.

  Args:
    purpose: The purpose of the approval.
    amount: The amount for approval.

  Returns:
    dict object with key `status` as 'ok' or 'reject'.
  """
  # send the reimbrusement request to payment vendor
  return {'status': 'ok'}


# 2. Wrap the function with LongRunningFunctionTool
long_running_tool = LongRunningFunctionTool(func=ask_for_approval)

# 3. Use the tool in an Agent
file_processor_agent = Agent(
    # Use a model compatible with function calling
    model="gemini-2.0-flash",
    name='reimbursement_agent',
    instruction="""
      You are an agent whose job is to handle the reimbursement process for
      the employees. If the amount is less than $100, you will automatically
      approve the reimbursement.

      If the amount is greater than $100, you will
      ask for approval from the manager. If the manager approves, you will
      call reimburse() to reimburse the amount to the employee. If the manager
      rejects, you will inform the employee of the rejection.
    """,
    tools=[reimburse, long_running_tool])


# Session and Runner
async def setup_session_and_runner():
  print('Seting up session and runner...')
  session_service = InMemorySessionService()
  session = await session_service.create_session(
      app_name=APP_NAME,
      user_id=USER_ID,
      session_id=SESSION_ID)
  runner = Runner(
      agent=file_processor_agent,
      app_name=APP_NAME,
      session_service=session_service)
  return session, runner


# Agent Interaction
async def call_agent_async(query: str, session, runner):
  def get_long_running_function_call(event: Event) -> types.FunctionCall:
    # Get the long running function call from the event
    if (
        not event.long_running_tool_ids
        or not event.content
        or not event.content.parts
    ):
      return

    for part in event.content.parts:
      if (
          part
          and part.function_call
          and event.long_running_tool_ids
          and part.function_call.id in event.long_running_tool_ids
      ):
        return part.function_call

  def get_function_response(
      event: Event, function_call_id: str) -> types.FunctionResponse:
    # Get the function response for the fuction call with specified id.
    if not event.content or not event.content.parts:
      return

    for part in event.content.parts:
      if (
          part
          and part.function_response
          and part.function_response.id == function_call_id
      ):
        return part.function_response

  if session is None or runner is None:
    session, runner = await setup_session_and_runner()

  content = types.Content(role='user', parts=[types.Part(text=query)])
  events = runner.run_async(
      user_id=USER_ID,
      session_id=SESSION_ID,
      new_message=content)

  print("\nRunning agent...")
  events_async = runner.run_async(
      session_id=session.id, user_id=USER_ID, new_message=content)

  long_running_function_call, long_running_function_response, ticket_id = (
      None, None, None)

  async for event in events_async:
    # Use helper to check for the specific auth request event
    if not long_running_function_call:
      long_running_function_call = get_long_running_function_call(event)
      if long_running_function_call:
        print(
            '\tGetting long running function call: '
            f'{long_running_function_call}')
    elif long_running_function_call and not long_running_function_response:
      long_running_function_response = get_function_response(
          event, long_running_function_call.id)
      print(
          '\tGetting long running function resp with id '
          f'"{long_running_function_call.id}": '
          f'{long_running_function_response}')
      if long_running_function_response:
        ticket_id = long_running_function_response.response['ticket-id']

    if event.content and event.content.parts:
      text = ''.join(
          part.text or ''
          for part in event.content.parts
          if hasattr(part, 'text')
      )
      if text:
        print(f'[{event.author}]: {text}')

  if long_running_function_response:
    # query the status of the correpsonding ticket via tciket_id
    # send back an intermediate / final response
    updated_response = long_running_function_response.model_copy(deep=True)
    updated_response.response = {'status': 'approved'}
    print('Sending approved event...')
    async for event in runner.run_async(
        session_id=session.id,
        user_id=USER_ID,
        new_message=types.Content(
            parts=[
                types.Part(function_response = updated_response)
            ], role='user')
    ):
      if event.content and event.content.parts:
        text = ''.join(
            part.text or ''
            for part in event.content.parts
            if hasattr(part, 'text')
        )
        if text:
          print(f'[{event.author}]: {text}')

    long_running_function_call, long_running_function_response, ticket_id = (
        None, None, None)
  else:
    print('No need to wait for long running function resp.')

  return session, runner


if __name__ == '__main__':
  session, runner = None, None
  session, runner = asyncio.run(call_agent_async("Please reimburse 50$ for meals", session, runner))
  asyncio.run(call_agent_async("Please reimburse 200$ for meals", session, runner))
