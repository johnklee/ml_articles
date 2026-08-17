#!/usr/bin/env python3
"""Coordinator/Dispatcher Pattern Example using Google Agent Development Kit (ADK).

This module implements an intelligent routing concierge:
1. BillingSpecialist: Handles invoices, subscriptions, and payment queries.
2. TechSupportSpecialist: Diagnoses bugs, connectivity issues, and system errors.
3. SalesSpecialist: Handles product pricing, upgrade options, and demonstrations.
4. CoordinatorAgent: Analyzes user intent and routes to the appropriate specialist via AutoFlow.
"""

from google.adk.agents import LlmAgent


MODEL_NAME = "gemini-3.5-flash"

# Sub-Agent 1: Billing Specialist
billing_specialist = LlmAgent(
  name="BillingSpecialist",
  model=MODEL_NAME,
  instruction=(
    "You are an expert Billing Specialist. Assist the user with invoice questions, "
    "payment disputes, billing cycles, refunds, and payment methods. "
    "Be polite, professional, and clear about billing policies."
  ),
  description="Handles billing inquiries, invoices, payments, refunds, and subscriptions.",
)

# Sub-Agent 2: Technical Support Specialist
tech_support_specialist = LlmAgent(
  name="TechSupportSpecialist",
  model=MODEL_NAME,
  instruction=(
    "You are a Technical Support Specialist. Assist the user with system errors, "
    "API integration bugs, performance troubleshooting, and connectivity issues. "
    "Provide clear diagnostic steps and technical guidance."
  ),
  description="Troubleshoots technical issues, error logs, API bugs, and platform connectivity.",
)

# Sub-Agent 3: Sales Specialist
sales_specialist = LlmAgent(
  name="SalesSpecialist",
  model=MODEL_NAME,
  instruction=(
    "You are a Sales and Solutions Specialist. Help users explore product tiers, "
    "enterprise licensing, feature comparisons, and custom onboarding demos. "
    "Be enthusiastic and solution-oriented."
  ),
  description="Handles product tier inquiries, enterprise pricing, sales quotes, and feature demos.",
)

# Root Coordinator / Dispatcher
coordinator_agent = LlmAgent(
  name="CoordinatorAgent",
  model=MODEL_NAME,
  instruction=(
    "You are the central Concierge and Coordinator. Analyze the user's intent and "
    "delegate the request to the most appropriate specialist agent:\n"
    "- BillingSpecialist: for invoices, payments, refunds, or subscription charges.\n"
    "- TechSupportSpecialist: for technical bugs, error messages, and outages.\n"
    "- SalesSpecialist: for pricing plans, product features, and enterprise sales.\n\n"
    "If the query is a general greeting or does not match a specialist, provide a welcoming response "
    "and explain how you can help."
  ),
  description="Main concierge and dispatcher routing user requests to specialized sub-agents.",
  sub_agents=[billing_specialist, tech_support_specialist, sales_specialist],
)

# Expose root agent for ADK compatibility
root_agent = coordinator_agent


def create_coordinator_agent(model: str = MODEL_NAME) -> LlmAgent:
  """Factory function to create a new Coordinator/Dispatcher agent hierarchy.

  Args:
    model: The Gemini model identifier to use across all agents.

  Returns:
    LlmAgent configured as the root coordinator with specialist sub-agents.
  """
  b_agent = LlmAgent(
    name="BillingSpecialist",
    model=model,
    instruction=(
      "You are an expert Billing Specialist. Assist the user with invoice questions, "
      "payment disputes, billing cycles, refunds, and payment methods."
    ),
    description="Handles billing inquiries, invoices, payments, refunds, and subscriptions.",
  )

  t_agent = LlmAgent(
    name="TechSupportSpecialist",
    model=model,
    instruction=(
      "You are a Technical Support Specialist. Assist the user with system errors, "
      "API integration bugs, performance troubleshooting, and connectivity issues."
    ),
    description="Troubleshoots technical issues, error logs, API bugs, and platform connectivity.",
  )

  s_agent = LlmAgent(
    name="SalesSpecialist",
    model=model,
    instruction=(
      "You are a Sales and Solutions Specialist. Help users explore product tiers, "
      "enterprise licensing, feature comparisons, and custom onboarding demos."
    ),
    description="Handles product tier inquiries, enterprise pricing, sales quotes, and feature demos.",
  )

  return LlmAgent(
    name="CoordinatorAgent",
    model=model,
    instruction=(
      "You are the central Concierge and Coordinator. Analyze the user's intent and "
      "delegate the request to the most appropriate specialist agent:\n"
      "- BillingSpecialist: for invoices, payments, refunds, or subscription charges.\n"
      "- TechSupportSpecialist: for technical bugs, error messages, and outages.\n"
      "- SalesSpecialist: for pricing plans, product features, and enterprise sales."
    ),
    description="Main concierge and dispatcher routing user requests to specialized sub-agents.",
    sub_agents=[b_agent, t_agent, s_agent],
  )


if __name__ == "__main__":
  from agent_tools import AgentRunner

  runner = AgentRunner(agent=coordinator_agent)
  question = "I was charged twice on my credit card for invoice #INV-2025-884."
  print(f"User Prompt: {question}\n")
  response = runner.prompt(question)
  print("\nAgent Response:\n")
  print(response)
