#!/usr/bin/env python3
"""Iterative Refinement Pattern Example using Google Agent Development Kit (ADK).

This module implements progressive qualitative improvement (the sculptor pattern):
1. InitialDraftGenerator (LlmAgent): Produces an initial rough draft.
2. CritiqueAgent (LlmAgent): Formulates specific qualitative critique and improvement suggestions.
   Can trigger early exit via exit_loop if the draft achieves publication grade.
3. RefinementAgent (LlmAgent): Rewrites and polishes the draft based on critique notes.
4. RefinementLoop (LoopAgent): Repeats the critique-refine cycle up to max_iterations.
5. SequentialAgent: Orchestrates initial draft generation followed by the refinement loop.
"""

from google.adk.agents import Context, LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools import exit_loop


MODEL_NAME = "gemini-3.5-flash"

# Step 1: Initial Draft Generator
draft_generator = LlmAgent(
  name="InitialDraftGenerator",
  model=MODEL_NAME,
  instruction=(
    "You are a Technical Writer. Produce a concise, informative initial draft "
    "addressing the user's topic. Cover the foundational concepts clearly."
  ),
  description="Produces initial rough drafts on technical topics.",
  output_key="current_draft",
)


def _critique_instruction(ctx: Context) -> str:
  """Generates dynamic instructions for the Critique Agent.

  Args:
    ctx: Execution context containing session state.

  Returns:
    Instruction string containing current draft text and review rubric.
  """
  draft = ctx.state.get("current_draft", "")
  return (
    f"You are a Senior Technical Editor and Architect.\n\n"
    f"Review the following draft:\n{draft}\n\n"
    "Evaluation Criteria:\n"
    "1. Depth, accuracy, and nuance of technical explanations.\n"
    "2. Elimination of common misconceptions.\n"
    "3. Inclusion of structured diagrams (ASCII/Mermaid) and comparative tables.\n\n"
    "CRITICAL ACTIONS:\n"
    "- If the draft is already comprehensive, publication-ready, and top-tier, "
    "YOU MUST CALL the 'exit_loop' tool to finalize.\n"
    "- Otherwise, provide 2-3 specific, actionable critique points for the refiner."
  )


# Step 2a: Critique Agent
critique_agent = LlmAgent(
  name="CritiqueAgent",
  model=MODEL_NAME,
  instruction=_critique_instruction,
  tools=[exit_loop],
  description="Evaluates technical drafts and yields targeted revision notes.",
  output_key="critique_notes",
)


def _refinement_instruction(ctx: Context) -> str:
  """Generates dynamic instructions for the Refinement Agent.

  Args:
    ctx: Execution context containing session state.

  Returns:
    Instruction string for rewriting and polishing the draft.
  """
  draft = ctx.state.get("current_draft", "")
  notes = ctx.state.get("critique_notes", "")
  return (
    "You are a Technical Refinement Specialist.\n\n"
    f"Current Draft:\n{draft}\n\n"
    f"Critique & Improvement Notes:\n{notes}\n\n"
    "Rewrite and polish the draft to fully address every critique note. "
    "Elevate technical rigor, clarity, and visual presentation (e.g. tables, code, ASCII charts)."
  )


# Step 2b: Refinement Agent (Overwrites current_draft)
refinement_agent = LlmAgent(
  name="RefinementAgent",
  model=MODEL_NAME,
  instruction=_refinement_instruction,
  description="Refines and rewrites technical drafts according to editor critique notes.",
  output_key="current_draft",
)

# Step 2: Loop (Critique -> Refine)
refinement_loop = LoopAgent(
  name="RefinementLoop",
  sub_agents=[critique_agent, refinement_agent],
  max_iterations=2,
  description="Iterative refinement loop alternating between critique and revision.",
)

# Full Workflow Pipeline
workflow = SequentialAgent(
  name="IterativeRefinementWorkflow",
  sub_agents=[draft_generator, refinement_loop],
  description="End-to-end workflow generating an initial draft and polishing it iteratively.",
)

# Expose root agent for ADK compatibility
root_agent = workflow


def create_iterative_refinement_pipeline(
  model: str = MODEL_NAME, max_iterations: int = 2
) -> SequentialAgent:
  """Factory function to build the Iterative Refinement agent pipeline.

  Args:
    model: The Gemini model identifier to use across all sub-agents.
    max_iterations: Maximum critique-refinement passes to execute.

  Returns:
    SequentialAgent configured with initial generator and refinement loop.
  """
  gen = LlmAgent(
    name="InitialDraftGenerator",
    model=model,
    instruction=(
      "You are a Technical Writer. Produce a concise, informative initial draft "
      "addressing the user's topic."
    ),
    description="Produces initial rough drafts on technical topics.",
    output_key="current_draft",
  )

  crt = LlmAgent(
    name="CritiqueAgent",
    model=model,
    instruction=_critique_instruction,
    tools=[exit_loop],
    description="Evaluates technical drafts and yields targeted revision notes.",
    output_key="critique_notes",
  )

  ref = LlmAgent(
    name="RefinementAgent",
    model=model,
    instruction=_refinement_instruction,
    description="Refines and rewrites technical drafts according to editor critique notes.",
    output_key="current_draft",
  )

  loop = LoopAgent(
    name="RefinementLoop",
    sub_agents=[crt, ref],
    max_iterations=max_iterations,
    description="Iterative refinement loop alternating between critique and revision.",
  )

  return SequentialAgent(
    name="IterativeRefinementWorkflow",
    sub_agents=[gen, loop],
    description="End-to-end workflow generating an initial draft and polishing it iteratively.",
  )


if __name__ == "__main__":
  from agent_tools import AgentRunner

  runner = AgentRunner(agent=workflow)
  topic = "Explain the CAP theorem for distributed databases, its misconceptions, and real-world PACELC extensions."
  print(f"User Topic: {topic}\n")
  response = runner.prompt(topic)
  print("\nAgent Response:\n")
  print(response)
