#!/usr/bin/env python3
"""Generator and Critic Pattern Example using Google Agent Development Kit (ADK).

This module implements a feedback-driven quality gate loop:
1. SQLGenerator (LlmAgent): Drafts a SQL query based on user specifications and refines
   it whenever feedback is provided in session state.
2. SQLCritic (LlmAgent): Validates the draft against syntax, security, and schema constraints.
   Calls the exit_loop tool when the draft satisfies all criteria, or yields corrective feedback.
3. ValidationLoop (LoopAgent): Encapsulates the generator and critic in an iterative loop.
"""

from google.adk.agents import Context, LlmAgent, LoopAgent
from google.adk.tools import exit_loop


MODEL_NAME = "gemini-3.5-flash"


def _generator_instruction(ctx: Context) -> str:
  """Builds dynamic instruction for the SQL Generator incorporating critic feedback.

  Args:
    ctx: The execution context containing session state.

  Returns:
    Formatted instruction string for the generator agent.
  """
  feedback = ctx.state.get("critic_feedback", "No prior critique.")
  return (
    "You are an expert SQL Generator. Write an ANSI SQL query to satisfy the user request.\n\n"
    f"Previous Critic Feedback:\n{feedback}\n\n"
    "If feedback is provided above, resolve all mentioned syntax or logical issues. "
    "Output ONLY the SQL code block."
  )


# Generator Agent
sql_generator = LlmAgent(
  name="SQLGenerator",
  model=MODEL_NAME,
  instruction=_generator_instruction,
  description="Generates and refines SQL queries according to requirements and critique feedback.",
  output_key="generated_sql",
)


def _critic_instruction(ctx: Context) -> str:
  """Builds dynamic instruction for the SQL Critic inspecting the latest draft.

  Args:
    ctx: The execution context containing session state.

  Returns:
    Formatted instruction string for the critic agent.
  """
  draft = ctx.state.get("generated_sql", "")
  return (
    f"You are a strict SQL Validator and Quality Gatekeeper.\n\n"
    f"Evaluate the following SQL query draft:\n{draft}\n\n"
    "Validation Checklist:\n"
    "1. Valid ANSI SQL syntax and correct JOIN/GROUP BY clauses.\n"
    "2. All requested filters and aggregations are properly implemented.\n"
    "3. No SQL injection vulnerabilities or unsafe table mutations.\n\n"
    "CRITICAL RULE:\n"
    "- If the query satisfies ALL rules above, YOU MUST IMMEDIATELY CALL THE 'exit_loop' TOOL.\n"
    "- If any issue is found, DO NOT call exit_loop. Instead, explain the exact error clearly."
  )


# Critic Agent
sql_critic = LlmAgent(
  name="SQLCritic",
  model=MODEL_NAME,
  instruction=_critic_instruction,
  tools=[exit_loop],
  description="Reviews SQL queries for syntactic and logical correctness, exiting the loop upon approval.",
  output_key="critic_feedback",
)

# Loop Orchestrator
validation_loop = LoopAgent(
  name="SQLValidationLoop",
  sub_agents=[sql_generator, sql_critic],
  max_iterations=3,
  description="Iterative validation loop coupling SQL generation and quality gate criticism.",
)

# Expose root agent for ADK compatibility
root_agent = validation_loop


def create_generator_critic_pipeline(model: str = MODEL_NAME, max_iterations: int = 3) -> LoopAgent:
  """Factory function to create a Generator-Critic quality gate loop.

  Args:
    model: The Gemini model identifier to use across agents.
    max_iterations: Maximum loop iterations before breaking.

  Returns:
    LoopAgent configured with generator and critic sub-agents.
  """
  gen = LlmAgent(
    name="SQLGenerator",
    model=model,
    instruction=_generator_instruction,
    description="Generates and refines SQL queries according to requirements and critique feedback.",
    output_key="generated_sql",
  )

  crt = LlmAgent(
    name="SQLCritic",
    model=model,
    instruction=_critic_instruction,
    tools=[exit_loop],
    description="Reviews SQL queries for correctness, calling exit_loop upon approval.",
    output_key="critic_feedback",
  )

  return LoopAgent(
    name="SQLValidationLoop",
    sub_agents=[gen, crt],
    max_iterations=max_iterations,
    description="Iterative validation loop coupling SQL generation and quality gate criticism.",
  )


if __name__ == "__main__":
  from agent_tools import AgentRunner

  runner = AgentRunner(agent=validation_loop)
  request = "Find top 5 customers with highest total order amount in 2025 who purchased in 'Electronics'."
  print(f"User Request: {request}\n")
  response = runner.prompt(request)
  print("\nAgent Response:\n")
  print(response)
