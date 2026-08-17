#!/usr/bin/env python3
"""Parallel Fan-Out/Gather Pattern Example using Google Agent Development Kit (ADK).

This module implements parallel agent execution to evaluate code simultaneously:
1. SecurityAuditor: Inspects code for vulnerabilities and security anti-patterns.
2. StyleEnforcer: Evaluates coding style, PEP8 compliance, and type annotations.
3. PerformanceAnalyst: Evaluates time/space complexity and resource bottlenecks.
4. CodeReviewSwarm (ParallelAgent): Executes all 3 reviewers in parallel.
5. PRSummarizer (LlmAgent): Aggregates all reports into a unified Pull Request review.
"""

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent


MODEL_NAME = "gemini-3.5-flash"

# Parallel Worker 1: Security Auditor
security_scanner = LlmAgent(
  name="SecurityAuditor",
  model=MODEL_NAME,
  instruction=(
    "You are a Security Auditor. Inspect the provided source code for security vulnerabilities, "
    "such as injection flaws, unescaped queries, unsafe memory access, and credential leakage. "
    "Provide a concise, bullet-pointed security assessment."
  ),
  description="Performs automated security vulnerability and risk audits on source code.",
  output_key="security_report",
)

# Parallel Worker 2: Style & Standards Enforcer
style_checker = LlmAgent(
  name="StyleEnforcer",
  model=MODEL_NAME,
  instruction=(
    "You are a Software Quality & Style Enforcer. Inspect the code for adherence to PEP8, "
    "idiomatic naming conventions, type hint completeness, and docstring quality. "
    "Provide concise bullet-pointed style findings."
  ),
  description="Enforces code style guides, naming conventions, and PEP8 standards.",
  output_key="style_report",
)

# Parallel Worker 3: Performance Analyst
complexity_analyzer = LlmAgent(
  name="PerformanceAnalyst",
  model=MODEL_NAME,
  instruction=(
    "You are a Performance & Complexity Analyst. Evaluate the time complexity, space complexity, "
    "I/O blocking, and algorithmic bottlenecks in the code. "
    "Provide concise bullet-pointed performance findings."
  ),
  description="Analyzes algorithmic time/space complexity and performance bottlenecks.",
  output_key="performance_report",
)

# Fan-Out Agent (ParallelAgent)
parallel_reviews = ParallelAgent(
  name="CodeReviewSwarm",
  sub_agents=[security_scanner, style_checker, complexity_analyzer],
  description="Runs security, style, and performance code reviews concurrently in parallel.",
)

# Gather / Synthesizer Agent
pr_summarizer = LlmAgent(
  name="PRSummarizer",
  model=MODEL_NAME,
  instruction=(
    "You are the Lead Code Reviewer and Synthesizer. Based on the individual parallel reports:\n\n"
    "### Security Report:\n{security_report}\n\n"
    "### Style & Standards Report:\n{style_report}\n\n"
    "### Performance Report:\n{performance_report}\n\n"
    "Synthesize these findings into a cohesive, structured Pull Request review comment. "
    "Include a clear summary, itemized key issues, a verdict (Approve / Request Changes), "
    "and a refactored code example addressing all identified problems."
  ),
  description="Aggregates parallel code review reports into a consolidated PR review.",
)

# Sequential Pipeline wrapping Fan-Out and Gather stages
workflow = SequentialAgent(
  name="ParallelCodeReviewPipeline",
  sub_agents=[parallel_reviews, pr_summarizer],
  description="A parallel fan-out/gather workflow for automated pull request code reviews.",
)

# Expose root agent for ADK compatibility
root_agent = workflow


def create_parallel_review_pipeline(model: str = MODEL_NAME) -> SequentialAgent:
  """Factory function to create a new Parallel Fan-Out/Gather review pipeline.

  Args:
    model: The Gemini model identifier to use across all sub-agents.

  Returns:
    SequentialAgent configured with a ParallelAgent swarm and a synthesizer.
  """
  sec = LlmAgent(
    name="SecurityAuditor",
    model=model,
    instruction=(
      "You are a Security Auditor. Inspect the provided source code for security vulnerabilities, "
      "such as injection flaws, unescaped queries, unsafe memory access, and credential leakage. "
      "Provide a concise, bullet-pointed security assessment."
    ),
    description="Performs automated security vulnerability and risk audits on source code.",
    output_key="security_report",
  )

  style = LlmAgent(
    name="StyleEnforcer",
    model=model,
    instruction=(
      "You are a Software Quality & Style Enforcer. Inspect the code for adherence to PEP8, "
      "idiomatic naming conventions, type hint completeness, and docstring quality. "
      "Provide concise bullet-pointed style findings."
    ),
    description="Enforces code style guides, naming conventions, and PEP8 standards.",
    output_key="style_report",
  )

  perf = LlmAgent(
    name="PerformanceAnalyst",
    model=model,
    instruction=(
      "You are a Performance & Complexity Analyst. Evaluate the time complexity, space complexity, "
      "I/O blocking, and algorithmic bottlenecks in the code. "
      "Provide concise bullet-pointed performance findings."
    ),
    description="Analyzes algorithmic time/space complexity and performance bottlenecks.",
    output_key="performance_report",
  )

  swarm = ParallelAgent(
    name="CodeReviewSwarm",
    sub_agents=[sec, style, perf],
    description="Runs security, style, and performance code reviews concurrently in parallel.",
  )

  synth = LlmAgent(
    name="PRSummarizer",
    model=model,
    instruction=(
      "You are the Lead Code Reviewer and Synthesizer. Based on the individual parallel reports:\n\n"
      "### Security Report:\n{security_report}\n\n"
      "### Style & Standards Report:\n{style_report}\n\n"
      "### Performance Report:\n{performance_report}\n\n"
      "Synthesize these findings into a cohesive, structured Pull Request review comment. "
      "Include a clear summary, itemized key issues, a verdict (Approve / Request Changes), "
      "and a refactored code example addressing all identified problems."
    ),
    description="Aggregates parallel code review reports into a consolidated PR review.",
  )

  return SequentialAgent(
    name="ParallelCodeReviewPipeline",
    sub_agents=[swarm, synth],
    description="A parallel fan-out/gather workflow for automated pull request code reviews.",
  )


if __name__ == "__main__":
  from agent_tools import AgentRunner

  runner = AgentRunner(agent=workflow)
  code_to_review = (
    "def fetch_user_orders(user_id):\n"
    "    query = 'SELECT * FROM orders WHERE customer_id = ' + str(user_id)\n"
    "    results = db.execute(query)\n"
    "    return results\n"
  )
  prompt = f"Please review the following code snippet for our pull request:\n\n```python\n{code_to_review}```"
  print(f"User Prompt:\n{prompt}\n")
  response = runner.prompt(prompt)
  print("\nAgent Response:\n")
  print(response)
