#!/usr/bin/env python3
"""Hierarchical Decomposition Pattern Example using Google Agent Development Kit (ADK).

This module implements nested hierarchical task delegation using AgentTool:
1. Level 3 (Leaf Agents):
   - KnowledgeRetrievalAgent: Queries technical databases for domain facts.
   - FactSummarizerAgent: Condenses detailed findings into bullet points.
2. Level 2 (Sub-Orchestrator):
   - ResearchAssistant: Coordinates knowledge retrieval and summarization.
3. Level 1 (Top-Level Executive Agent):
   - ExecutiveReportWriter: Receives high-level requests and invokes the ResearchAssistant
     as a callable function via AgentTool.
"""

from typing import Dict
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool


MODEL_NAME = "gemini-3.5-flash"


def query_technical_database(query: str) -> str:
  """Queries the internal enterprise knowledge database for verified technical facts.

  Args:
    query: The search query topic.

  Returns:
    A string containing technical documentation snippets and factual records.
  """
  db_records: Dict[str, str] = {
    "quantum": (
      "Quantum Computing Updates 2025: Google Quantum AI demonstrated suppression of logical "
      "error rates using surface codes. IBM unveiled Heron processors focusing on qLDPC codes. "
      "Neutral atom systems from QuEra demonstrated algorithmic execution across 48 logical qubits."
    ),
    "microservices": (
      "Microservices Architecture: Emphasizes decoupled domain services, gRPC/REST communication, "
      "event-driven choreography via Kafka, and decentralized data ownership with eventual consistency."
    ),
    "ai_agent": (
      "AI Agent Architecture: Multi-agent systems decompose monolithic prompts into specialized roles "
      "(Pipelines, Coordinators, Parallel Swarms, Evaluator Loops). State is synchronized via shared session memory."
    ),
  }

  query_lower = query.lower()
  matches = [v for k, v in db_records.items() if k in query_lower]
  if matches:
    return "\n\n".join(matches)
  return (
    f"Knowledge Record for '{query}': High-performance enterprise systems leverage modular "
    "abstractions, automated validation gates, and hierarchical delegation."
  )


# Level 3: Leaf Tool Agent - Knowledge Retrieval
knowledge_retriever = LlmAgent(
  name="KnowledgeRetrievalAgent",
  model=MODEL_NAME,
  instruction=(
    "You are a Knowledge Retrieval Specialist. Query the technical database using the "
    "query_technical_database tool and return factual information without fabrication."
  ),
  description="Searches the internal technical database for domain facts and documentation.",
  tools=[query_technical_database],
)

# Level 3: Leaf Tool Agent - Fact Summarizer
fact_summarizer = LlmAgent(
  name="FactSummarizerAgent",
  model=MODEL_NAME,
  instruction=(
    "You are a Fact Summarizer. Organize and condense the provided raw technical text "
    "into precise, structured key points."
  ),
  description="Condenses raw technical text into structured key points.",
)

# Level 2: Sub-Orchestrator Agent
research_assistant = LlmAgent(
  name="ResearchAssistant",
  model=MODEL_NAME,
  instruction=(
    "You are a Research Assistant. Analyze the research query, retrieve relevant domain "
    "facts using KnowledgeRetrievalAgent, and distill them using FactSummarizerAgent. "
    "Provide a consolidated research brief."
  ),
  description="Coordinates technical information retrieval and summarization on requested topics.",
  sub_agents=[knowledge_retriever, fact_summarizer],
)

# Level 1: Top-Level Executive Agent (Uses ResearchAssistant as an AgentTool)
report_writer = LlmAgent(
  name="ExecutiveReportWriter",
  model=MODEL_NAME,
  instruction=(
    "You are an Executive Technology Analyst and Report Writer. "
    "Your objective is to produce comprehensive executive briefings on complex topics. "
    "Always invoke the ResearchAssistant tool to gather factual research before composing the final report. "
    "Structure the report with Executive Summary, Technical Highlights, and Strategic Implications."
  ),
  description="Produces structured executive technology briefings using nested research sub-agents.",
  tools=[AgentTool(research_assistant)],
)

# Expose root agent for ADK compatibility
root_agent = report_writer


def create_hierarchical_research_agent(model: str = MODEL_NAME) -> LlmAgent:
  """Factory function to construct a 3-level hierarchical agent system.

  Args:
    model: The Gemini model identifier to use across all sub-agents.

  Returns:
    LlmAgent configured as the top-level executive writer with nested AgentTool.
  """
  retriever = LlmAgent(
    name="KnowledgeRetrievalAgent",
    model=model,
    instruction=(
      "You are a Knowledge Retrieval Specialist. Query the technical database using the "
      "query_technical_database tool and return factual information without fabrication."
    ),
    description="Searches the internal technical database for domain facts and documentation.",
    tools=[query_technical_database],
  )

  summarizer = LlmAgent(
    name="FactSummarizerAgent",
    model=model,
    instruction=(
      "You are a Fact Summarizer. Organize and condense the provided raw technical text "
      "into precise, structured key points."
    ),
    description="Condenses raw technical text into structured key points.",
  )

  sub_orchestrator = LlmAgent(
    name="ResearchAssistant",
    model=model,
    instruction=(
      "You are a Research Assistant. Analyze the research query, retrieve relevant domain "
      "facts using KnowledgeRetrievalAgent, and distill them using FactSummarizerAgent."
    ),
    description="Coordinates technical information retrieval and summarization on requested topics.",
    sub_agents=[retriever, summarizer],
  )

  return LlmAgent(
    name="ExecutiveReportWriter",
    model=model,
    instruction=(
      "You are an Executive Technology Analyst and Report Writer. "
      "Always invoke the ResearchAssistant tool to gather factual research before composing the final report. "
      "Structure the report with Executive Summary, Technical Highlights, and Strategic Implications."
    ),
    description="Produces structured executive technology briefings using nested research sub-agents.",
    tools=[AgentTool(sub_orchestrator)],
  )


if __name__ == "__main__":
  from agent_tools import AgentRunner

  runner = AgentRunner(agent=report_writer)
  question = "Provide an executive briefing on recent advances in quantum computing architectures."
  print(f"User Prompt: {question}\n")
  response = runner.prompt(question)
  print("\nAgent Response:\n")
  print(response)
