#!/usr/bin/env python3
"""Sequential Pipeline Pattern Example using Google Agent Development Kit (ADK).

This module implements a sequential multi-agent assembly line:
1. thinking_agent: Formulates an effective Google search query from the user's question.
2. query_agent: Executes the Google search query and retrieves the top 3 results in text.
3. summary_agent: Synthesizes the search results into a concise, accurate summary.
"""

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search


MODEL_NAME = "gemini-3.5-flash"

# Step 1: Thinking Agent (Formulates Google Search query from the user question)
thinking_agent = LlmAgent(
  name="ThinkingAgent",
  model=MODEL_NAME,
  instruction=(
    "You are an expert search query formulation assistant. "
    "Analyze the user's question and compose an effective, concise Google search query. "
    "Output ONLY the search query string without any introductory or explanatory text."
  ),
  description="Composes optimized Google search queries based on user questions.",
  output_key="search_query",
)

# Step 2: Query Agent (Executes Google Search and retrieves top 3 results in text)
query_agent = LlmAgent(
  name="QueryAgent",
  model=MODEL_NAME,
  instruction=(
    "You are an information retrieval agent. Using the search query: {search_query}, "
    "conduct a Google search using the Google Search tool and retrieve the top 3 most "
    "relevant search results in text, including key details and snippets. "
    "Output ONLY the retrieved search results."
  ),
  description="Conducts Google search and retrieves top 3 text search results.",
  tools=[google_search],
  output_key="search_results",
)

# Step 3: Summary Agent (Summarizes the search results to answer the question)
summary_agent = LlmAgent(
  name="SummaryAgent",
  model=MODEL_NAME,
  instruction=(
    "You are an expert summarization assistant. Based on the retrieved search results:\n"
    "{search_results}\n\n"
    "Provide a clear, accurate, and comprehensive summary that directly answers the user's original question."
  ),
  description="Summarizes retrieved search results into a comprehensive answer.",
)

# Orchestrate the Assembly Line using SequentialAgent
pipeline = SequentialAgent(
  name="SearchAndSummarizePipeline",
  sub_agents=[thinking_agent, query_agent, summary_agent],
  description=(
    "A sequential pipeline that formulates search queries, retrieves top Google"
    " search results, and synthesizes a final summary."
  ),
)

# Expose as root_agent for ADK compatibility
root_agent = pipeline


def create_sequential_search_agent(model: str = MODEL_NAME) -> SequentialAgent:
  """Factory function to create a new instance of the sequential search pipeline.

  Args:
    model: The Gemini model identifier to use across all sub-agents.

  Returns:
    SequentialAgent configured with thinking, query, and summary agents.
  """
  t_agent = LlmAgent(
    name="ThinkingAgent",
    model=model,
    instruction=(
      "You are an expert search query formulation assistant. "
      "Analyze the user's question and compose an effective, concise Google search query. "
      "Output ONLY the search query string without any introductory or explanatory text."
    ),
    description="Composes optimized Google search queries based on user questions.",
    output_key="search_query",
  )

  q_agent = LlmAgent(
    name="QueryAgent",
    model=model,
    instruction=(
      "You are an information retrieval agent. Using the search query: {search_query}, "
      "conduct a Google search using the Google Search tool and retrieve the top 3 most "
      "relevant search results in text, including key details and snippets. "
      "Output ONLY the retrieved search results."
    ),
    description="Conducts Google search and retrieves top 3 text search results.",
    tools=[google_search],
    output_key="search_results",
  )

  s_agent = LlmAgent(
    name="SummaryAgent",
    model=model,
    instruction=(
      "You are an expert summarization assistant. Based on the retrieved search results:\n"
      "{search_results}\n\n"
      "Provide a clear, accurate, and comprehensive summary that directly answers the user's original question."
    ),
    description="Summarizes retrieved search results into a comprehensive answer.",
  )

  return SequentialAgent(
    name="SearchAndSummarizePipeline",
    sub_agents=[t_agent, q_agent, s_agent],
    description=(
      "A sequential pipeline that formulates search queries, retrieves top Google"
      " search results, and synthesizes a final summary."
    ),
  )


if __name__ == "__main__":
  from agent_tools import AgentRunner

  runner = AgentRunner(agent=pipeline)
  question = "What is the James Webb Space Telescope's latest major discovery?"
  print(f"User Prompt: {question}\n")
  response = runner.prompt(question)
  print("Agent Response:\n")
  print(response)
