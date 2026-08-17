#!/usr/bin/env python3
"""Agent runner utilities and callback plugins for Google Agent Development Kit (ADK)."""

import asyncio
import os
from typing import Any, Dict, List, Optional
from google.adk.agents import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.plugins import BasePlugin
from google.adk.runners import Runner
from google.adk.sessions import BaseSessionService, InMemorySessionService
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types
import nest_asyncio

# Suppress duplicate API key warning from google-genai
if os.environ.get("GOOGLE_API_KEY") and os.environ.get("GEMINI_API_KEY"):
  del os.environ["GEMINI_API_KEY"]


class AgentIOCallbackPlugin(BasePlugin):
  """ADK Plugin to print input and output of root and sub-agents during execution.

  Intercepts agent execution lifecycle hooks to provide real-time visibility
  into prompts, state variables, tool invocations, and responses for each agent.

  Attributes:
    root_agent_name: Name of the top-level root agent.
  """

  def __init__(
    self,
    root_agent_name: Optional[str] = None,
    name: str = "agent_io_callback_plugin",
  ):
    """Initializes AgentIOCallbackPlugin.

    Args:
      root_agent_name: Optional name of the root agent to distinguish root
        from sub-agents.
      name: Plugin instance identifier name.
    """
    super().__init__(name=name)
    self.root_agent_name = root_agent_name
    self._agent_outputs: Dict[str, List[str]] = {}
    self._initial_state_snapshots: Dict[str, Dict[str, Any]] = {}

  async def before_run_callback(
    self, *, invocation_context: InvocationContext
  ) -> Optional[types.Content]:
    """Executed before the runner begins the execution loop.

    Args:
      invocation_context: The invocation context containing runner state.

    Returns:
      Optional Content to short-circuit invocation, or None to continue.
    """
    if (
      not self.root_agent_name
      and hasattr(invocation_context, "agent")
      and invocation_context.agent
    ):
      self.root_agent_name = invocation_context.agent.name
    self._agent_outputs.clear()
    self._initial_state_snapshots.clear()
    return None

  async def before_agent_callback(
    self, *, agent: BaseAgent, callback_context: CallbackContext
  ) -> Optional[types.Content]:
    """Callback executed before an agent starts its primary logic.

    Logs input prompts, instructions, and existing state variables for
    the agent.

    Args:
      agent: The agent instance about to run.
      callback_context: The context for the agent invocation.

    Returns:
      Optional Content to override agent output, or None to proceed.
    """
    is_root = agent.name == self.root_agent_name
    agent_type = "Root Agent" if is_root else "Sub-Agent"
    current_state = (
      callback_context.state.to_dict()
      if hasattr(callback_context.state, "to_dict")
      else {}
    )
    self._initial_state_snapshots[agent.name] = dict(current_state)

    border = "=" * 60 if is_root else "-" * 60
    print(f"\n{border}")
    print(f"▶ [{agent_type}: {agent.name}] Input")
    print(f"{border}")

    # Display user prompt if present
    if callback_context.user_content and callback_context.user_content.parts:
      user_texts = [
        p.text for p in callback_context.user_content.parts if p.text
      ]
      if user_texts:
        print(f"  • User Prompt: {' '.join(user_texts).strip()}")

    # Display input state variables if present
    if current_state:
      print("  • Input State:")
      for key, val in current_state.items():
        val_str = str(val).strip()
        if len(val_str) > 300:
          val_str = val_str[:300] + "..."
        print(f"    - {key}: {val_str}")

    return None

  async def on_event_callback(
    self, *, invocation_context: InvocationContext, event: Event
  ) -> Optional[Event]:
    """Callback executed when an event is yielded by an agent.

    Collects response content and logs any tool/function calls and responses.

    Args:
      invocation_context: The invocation context.
      event: The event emitted by the agent.

    Returns:
      Optional modified Event, or None to pass through unmodified.
    """
    if event.author and event.content and event.content.parts:
      texts = [
        p.text
        for p in event.content.parts
        if p.text and not getattr(p, "thought", False)
      ]
      if texts:
        author = event.author
        if author not in self._agent_outputs:
          self._agent_outputs[author] = []
        self._agent_outputs[author].extend(texts)

    if event.get_function_calls():
      for fc in event.get_function_calls():
        print(f"  ⚙ [Tool Call: {fc.name}] args: {fc.args}")

    if event.get_function_responses():
      for fr in event.get_function_responses():
        print(f"  ⚙ [Tool Response: {fr.name}] response received")

    return None

  async def after_agent_callback(
    self, *, agent: BaseAgent, callback_context: CallbackContext
  ) -> Optional[types.Content]:
    """Callback executed after an agent completes its primary logic.

    Logs generated text responses and new/updated session state keys.

    Args:
      agent: The agent instance that has finished running.
      callback_context: The context for the agent invocation.

    Returns:
      Optional Content to override the final agent response, or None.
    """
    is_root = agent.name == self.root_agent_name
    agent_type = "Root Agent" if is_root else "Sub-Agent"
    current_state = (
      callback_context.state.to_dict()
      if hasattr(callback_context.state, "to_dict")
      else {}
    )
    initial_state = self._initial_state_snapshots.get(agent.name, {})

    border = "=" * 60 if is_root else "-" * 60
    print(f"\n{border}")
    print(f"◀ [{agent_type}: {agent.name}] Output")
    print(f"{border}")

    outputs = self._agent_outputs.get(agent.name, [])
    if outputs:
      print(f"  • Generated Response:\n{' '.join(outputs).strip()}")

    # Display state mutations produced by this agent
    new_or_updated = {
      k: v
      for k, v in current_state.items()
      if k not in initial_state or initial_state[k] != v
    }
    if new_or_updated:
      print("  • State Updates:")
      for key, val in new_or_updated.items():
        val_str = str(val).strip()
        if len(val_str) > 300:
          val_str = val_str[:300] + "..."
        print(f"    - {key}: {val_str}")

    return None

  async def before_tool_callback(
    self,
    *,
    tool: BaseTool,
    tool_args: Dict[str, Any],
    tool_context: ToolContext,
  ) -> Optional[Dict[str, Any]]:
    """Callback executed before a tool is invoked.

    Args:
      tool: The tool about to be executed.
      tool_args: Dictionary of tool input arguments.
      tool_context: The tool execution context.

    Returns:
      Optional modified tool arguments dictionary, or None.
    """
    print(f"  🔧 [Tool Invocation: {tool.name}] args: {tool_args}")
    return None

  async def after_tool_callback(
    self,
    *,
    tool: BaseTool,
    tool_args: Dict[str, Any],
    tool_context: ToolContext,
    result: Dict[str, Any],
  ) -> Optional[Dict[str, Any]]:
    """Callback executed after a tool execution completes.

    Args:
      tool: The tool that was executed.
      tool_args: The arguments passed to the tool.
      tool_context: The tool execution context.
      result: The result returned by the tool.

    Returns:
      Optional modified tool result dictionary, or None.
    """
    result_str = str(result).strip()
    if len(result_str) > 300:
      result_str = result_str[:300] + "..."
    print(f"  🔧 [Tool Result: {tool.name}] result: {result_str}")
    return None

  async def on_tool_error_callback(
    self,
    *,
    tool: BaseTool,
    tool_args: Dict[str, Any],
    tool_context: ToolContext,
    error: Exception,
  ) -> Optional[Dict[str, Any]]:
    """Callback executed when a tool execution encounters an error.

    Args:
      tool: The tool that raised the error.
      tool_args: The arguments passed to the tool.
      tool_context: The tool execution context.
      error: The Exception raised by the tool.

    Returns:
      Optional error recovery dictionary, or None.
    """
    print(f"  ❌ [Tool Error: {tool.name}] error: {error}")
    return None


class AgentRunner:
  """Wraps an ADK Agent and provides convenient execution methods and callbacks.

  Attributes:
    agent: The BaseAgent or SequentialAgent to run.
    app_name: The application name for session management.
    user_id: The user identifier for session management.
    session_id: The session identifier.
    session_service: The session service instance used to manage state.
    plugins: List of BasePlugin instances registered with the runner.
    runner: The underlying ADK Runner instance.
  """

  def __init__(
    self,
    agent: BaseAgent,
    app_name: str = "agent_runner_app",
    user_id: str = "default_user",
    session_id: str = "default_session",
    session_service: Optional[BaseSessionService] = None,
    plugins: Optional[List[BasePlugin]] = None,
    enable_logging: bool = True,
  ):
    """Initializes AgentRunner with an agent, session parameters, and callbacks.

    Args:
      agent: The ADK agent instance (e.g., LlmAgent, SequentialAgent).
      app_name: Name of the application namespace.
      user_id: User identifier.
      session_id: Session identifier.
      session_service: Optional custom session service. Defaults to
        InMemorySessionService.
      plugins: Optional list of ADK plugins for custom callbacks.
      enable_logging: Whether to automatically register AgentIOCallbackPlugin
        to print inputs and outputs of root and sub-agents. Defaults to True.
    """
    self.agent = agent
    self.app_name = app_name
    self.user_id = user_id
    self.session_id = session_id
    self.session_service = session_service or InMemorySessionService()
    self.plugins: List[BasePlugin] = list(plugins) if plugins is not None else []

    if enable_logging and not any(
      isinstance(p, AgentIOCallbackPlugin) for p in self.plugins
    ):
      self.plugins.append(
        AgentIOCallbackPlugin(root_agent_name=self.agent.name)
      )

    self.runner = Runner(
      agent=self.agent,
      app_name=self.app_name,
      session_service=self.session_service,
      plugins=self.plugins,
    )
    self._session_initialized = False

  def register_plugin(self, plugin: BasePlugin) -> None:
    """Registers an additional plugin with the runner.

    Args:
      plugin: The BasePlugin instance to register.
    """
    self.plugins.append(plugin)
    if hasattr(self.runner, "plugin_manager"):
      self.runner.plugin_manager.register_plugin(plugin)

  async def prompt_async(self, prompt: str) -> str:
    """Asynchronously feeds a prompt to the agent and returns the final response.

    Args:
      prompt: The user input prompt string.

    Returns:
      The agent's final text response.
    """
    if not self._session_initialized:
      await self.session_service.create_session(
        app_name=self.app_name,
        user_id=self.user_id,
        session_id=self.session_id,
      )
      self._session_initialized = True

    user_content = types.Content(
      role="user",
      parts=[types.Part(text=prompt)],
    )

    final_response_content = ""
    async for event in self.runner.run_async(
      user_id=self.user_id,
      session_id=self.session_id,
      new_message=user_content,
    ):
      if event.is_final_response() and event.content and event.content.parts:
        response_parts = [
          p.text
          for p in event.content.parts
          if not getattr(p, "thought", False) and p.text
        ]
        if response_parts:
          final_response_content = "".join(response_parts)

    return final_response_content

  def prompt(self, prompt: str) -> str:
    """Synchronously receives user prompt, feeds into the agent, and returns the response.

    Supports execution in standard Python runtime as well as within existing
    asyncio event loops (such as Jupyter notebooks).

    Args:
      prompt: The user input prompt string.

    Returns:
      The agent's final text response.
    """
    nest_asyncio.apply()
    return asyncio.run(self.prompt_async(prompt))
