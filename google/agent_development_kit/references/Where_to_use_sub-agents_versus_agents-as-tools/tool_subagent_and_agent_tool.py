#!/usr/bin/env python3
"""Codelab demonstrating ADK LlmAgent with tool, subagent, and AgentTool."""

import asyncio
import os
from typing import Any, Sequence

from absl import app
from google.adk.agents import llm_agent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import InMemoryRunner
from google.adk.tools.agent_tool import AgentTool
from google.genai import types


MODEL_NAME = "gemini-3.5-flash"


class DemoMockModel(BaseLlm):
  """Mock LLM for offline demonstration of tool execution and event collection."""

  model: str = "mock"

  @classmethod
  def supported_models(cls) -> list[str]:
    return ["mock", "gemini-3.5-flash"]

  async def generate_content_async(
      self, llm_request: LlmRequest, stream: bool = False
  ):
    del stream
    has_func_resp = False
    if llm_request.contents:
      for content in llm_request.contents:
        if content.parts:
          for part in content.parts:
            if getattr(part, "function_response", None):
              has_func_resp = True
              break

    if has_func_resp:
      yield LlmResponse(
          content=types.Content(
              role="model",
              parts=[types.Part.from_text(text="The sum of 1 and 2 is 3.")],
          ),
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              prompt_token_count=18,
              candidates_token_count=12,
              total_token_count=30,
          ),
      )
    else:
      available_func_names = set()
      if llm_request.config and llm_request.config.tools:
        for tool_group in llm_request.config.tools:
          if getattr(tool_group, "function_declarations", None):
            for decl in tool_group.function_declarations:
              available_func_names.add(decl.name)

      if "add" in available_func_names:
        call_part = types.Part(
            function_call=types.FunctionCall(
                name="add",
                args={"a": 1, "b": 2},
            )
        )
      elif "transfer_to_agent" in available_func_names:
        call_part = types.Part(
            function_call=types.FunctionCall(
                name="transfer_to_agent",
                args={"agent_name": "math_sub_agent"},
            )
        )
      elif "math_agent_for_tool" in available_func_names:
        call_part = types.Part(
            function_call=types.FunctionCall(
                name="math_agent_for_tool",
                args={"request": "Add 1 with 2."},
            )
        )
      else:
        call_part = types.Part(
            function_call=types.FunctionCall(
                name="add",
                args={"a": 1, "b": 2},
            )
        )

      yield LlmResponse(
          content=types.Content(
              role="model",
              parts=[call_part],
          ),
          usage_metadata=types.GenerateContentResponseUsageMetadata(
              prompt_token_count=22,
              candidates_token_count=14,
              total_token_count=36,
          ),
      )


def _init_environment() -> None:
  if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyFakeKeyForTestingPurposes1234567"


def add(a: int, b: int) -> int:
  """Adds two numbers."""
  return a + b


def _serialize_val_to_toml(val: Any) -> str:
  """Converts a Python data structure to TOML format string representation."""
  if isinstance(val, bool):
    return "true" if val else "false"
  elif isinstance(val, (int, float)):
    return str(val)
  elif isinstance(val, str):
    escaped = val.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'
  elif isinstance(val, (list, tuple)):
    if not val:
      return "[]"
    items_str = ", ".join(_serialize_val_to_toml(item) for item in val)
    return f"[{items_str}]"
  elif isinstance(val, dict):
    items = [f"{k} = {_serialize_val_to_toml(v)}" for k, v in val.items()]
    return "{ " + ", ".join(items) + " }"
  else:
    escaped = str(val).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def save_events_to_toml(events: Sequence[Any], filepath: str) -> None:
  """Saves a list of ADK events to a TOML formatted file."""
  lines = [
      "# Events collected for agent execution",
      f"total_events = {len(events)}",
      "",
  ]
  for idx, event in enumerate(events, 1):
    lines.append("[[events]]")
    lines.append(f"event_number = {idx}")
    event_id = getattr(event, "id", "") or ""
    author = getattr(event, "author", "") or ""
    lines.append(f'id = "{event_id}"')
    lines.append(f'author = "{author}"')

    content = getattr(event, "content", None)
    if content:
      lines.append("  [events.content]")
      role = getattr(content, "role", "") or ""
      lines.append(f'  role = "{role}"')

      parts = getattr(content, "parts", []) or []
      parts_serialized = []
      for p in parts:
        p_dict = {}
        if getattr(p, "thought", False):
          p_dict["thought"] = True
        if getattr(p, "text", None):
          p_dict["text"] = p.text
        if getattr(p, "function_call", None):
          fc = p.function_call
          p_dict["function_call"] = {
              "name": fc.name,
              "args": dict(fc.args) if fc.args else {},
          }
        if getattr(p, "function_response", None):
          fr = p.function_response
          resp = (
              dict(fr.response)
              if isinstance(fr.response, dict)
              else str(fr.response)
          )
          p_dict["function_response"] = {
              "name": fr.name,
              "response": resp,
          }
        if p_dict:
          parts_serialized.append(p_dict)

      lines.append("  parts = [")
      for p_dict in parts_serialized:
        lines.append(f"    {_serialize_val_to_toml(p_dict)},")
      lines.append("  ]")
    lines.append("")

  dir_name = os.path.dirname(filepath)
  if dir_name:
    os.makedirs(dir_name, exist_ok=True)
  with open(filepath, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))


async def run_agent_and_collect(
    agent: llm_agent.LlmAgent, prompt_text: str = "Add 1 with 2."
) -> tuple[list[Any], int]:
  """Runs an agent with prompt_text, returning collected events and total token usage."""
  runner = InMemoryRunner(agent=agent)
  session = await runner.session_service.create_session(
      app_name=runner.app_name,
      user_id="user",
      state={},
  )
  new_message = types.Content(
      role="user",
      parts=[types.Part.from_text(text=prompt_text)],
  )

  events = []
  total_tokens = 0

  try:
    async for event in runner.run_async(
        user_id="user",
        session_id=session.id,
        new_message=new_message,
    ):
      events.append(event)
      if hasattr(event, "usage_metadata") and event.usage_metadata:
        meta = event.usage_metadata
        if getattr(meta, "total_token_count", None):
          total_tokens += meta.total_token_count
        elif getattr(meta, "prompt_token_count", None):
          p_tokens = meta.prompt_token_count or 0
          c_tokens = meta.candidates_token_count or 0
          total_tokens += p_tokens + c_tokens
  except Exception as e:
    print(f"[{agent.name}] Execution notice/error: {e}")

  return events, total_tokens


def create_agents() -> (
    tuple[llm_agent.LlmAgent, llm_agent.LlmAgent, llm_agent.LlmAgent]
):
  """Creates the three required ADK agents."""
  key = os.environ.get("GOOGLE_API_KEY", "")
  if not key or key.startswith("AIzaSyFake"):
    model_obj: Any = DemoMockModel()
  else:
    model_obj = MODEL_NAME

  # 1. Agent with function tool
  agent_with_tool = llm_agent.Agent(
      name="agent_with_tool",
      model=model_obj,
      instruction=(
          "You are a helpful math assistant. Use the provided tools to add"
          " numbers."
      ),
      tools=[add],
  )

  # 2. Agent with subagent
  math_sub_agent = llm_agent.Agent(
      name="math_sub_agent",
      model=model_obj,
      description="A subagent that performs math addition.",
      instruction="You perform math addition when asked.",
      tools=[add],
  )
  agent_with_subagent = llm_agent.Agent(
      name="agent_with_subagent",
      model=model_obj,
      instruction=(
          "You are a root agent. Delegate math addition tasks to your subagent."
      ),
      sub_agents=[math_sub_agent],
  )

  # 3. Agent with subagent wrapped as AgentTool
  math_agent_for_tool = llm_agent.Agent(
      name="math_agent_for_tool",
      model=model_obj,
      description="An agent that performs addition.",
      instruction="You add numbers for the user.",
      tools=[add],
  )
  agent_with_subagent_as_tool = llm_agent.Agent(
      name="agent_with_subagent_as_tool",
      model=model_obj,
      instruction=(
          "You are a root agent. Use the math_agent_for_tool tool to perform"
          " math addition."
      ),
      tools=[AgentTool(agent=math_agent_for_tool)],
  )

  return agent_with_tool, agent_with_subagent, agent_with_subagent_as_tool


async def async_main() -> None:
  agent_with_tool, agent_with_subagent, agent_with_subagent_as_tool = (
      create_agents()
  )

  prompt = "Add 1 with 2."
  agent_runs = [
      ("agent_with_tool", agent_with_tool, "/tmp/agent_with_tool_events.toml"),
      (
          "agent_with_subagent",
          agent_with_subagent,
          "/tmp/agent_with_subagent_events.toml",
      ),
      (
          "agent_with_subagent_as_tool",
          agent_with_subagent_as_tool,
          "/tmp/agent_with_subagent_as_tool_events.toml",
      ),
  ]

  print(f"Prompt: '{prompt}'\n" + "=" * 50)
  for name, agent, toml_path in agent_runs:
    events, total_tokens = await run_agent_and_collect(agent, prompt)
    save_events_to_toml(events, toml_path)
    print(f"Agent Name     : {name}")
    print(f"Saved Events To: {toml_path}")
    print(f"Total Events   : {len(events)}")
    print(f"Total Tokens   : {total_tokens}")
    print("-" * 50)


def main(argv: Sequence[str]) -> None:
  del argv
  _init_environment()
  asyncio.run(async_main())


if __name__ == "__main__":
  app.run(main)
