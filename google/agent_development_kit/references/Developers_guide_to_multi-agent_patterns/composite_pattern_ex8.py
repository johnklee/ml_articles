#!/usr/bin/env python3
"""Composite Pattern Example using Google Agent Development Kit (ADK).

This module combines multiple multi-agent design patterns into a real-world enterprise architecture:
1. Coordinator/Dispatcher Pattern:
   - EnterpriseConcierge (LlmAgent): Routes incoming requests to specialized pipelines.
2. Parallel Fan-Out/Gather Pattern:
   - TechResearchSwarm (ParallelAgent): Concurrently searches API technical documentation
     and retrieves account infrastructure telemetry.
3. Generator and Critic Pattern:
   - ToneQualityLoop (LoopAgent): Iteratively crafts and evaluates customer support answers,
     enforcing professional empathy, technical accuracy, and safety gates.
4. Sequential Pipeline Pattern:
   - TechnicalSupportPipeline (SequentialAgent): Integrates research swarm and quality review.
"""

from google.adk.agents import Context, LlmAgent, LoopAgent, ParallelAgent, SequentialAgent
from google.adk.tools import exit_loop


MODEL_NAME = "gemini-3.5-flash"


def fetch_api_docs(query: str) -> str:
  """Retrieves technical API documentation, error guides, and remediation playbooks.

  Args:
    query: The technical topic or HTTP status code.

  Returns:
    Relevant documentation excerpt with diagnosis and resolution steps.
  """
  return (
    "Documentation Record for HTTP 504 (Gateway Timeout):\n"
    "- Cause: Upstream backend service exceeded the load balancer's default response deadline (30s).\n"
    "- Troubleshooting: (1) Check backend health check status; (2) Verify firewall rules for LB subnets; "
    "(3) Inspect database slow query logs; (4) Increase backend timeout in GCP Load Balancer settings."
  )


def fetch_account_infrastructure(account_id: str = "enterprise_acct_default") -> str:
  """Retrieves infrastructure telemetry, deployment regions, and active incident records.

  Args:
    account_id: The customer account identifier.

  Returns:
    Account configuration and regional health telemetry.
  """
  return (
    f"Infrastructure Telemetry for '{account_id}':\n"
    "- Tier: Enterprise Platinum (SLA 99.99%)\n"
    "- Primary Region: us-central1\n"
    "- Ingress Health: 100% healthy\n"
    "- Incident Status: Minor transient latency reported in us-central1 ingress cluster 02."
  )


# --- Pattern 1 & 3: Parallel Research Workers ---
doc_agent = LlmAgent(
  name="DocumentationSearchAgent",
  model=MODEL_NAME,
  instruction=(
    "You are an API Documentation Specialist. Look up diagnostic documentation and resolution steps "
    "for the technical issue using fetch_api_docs."
  ),
  description="Searches API documentation and troubleshooting playbooks.",
  tools=[fetch_api_docs],
  output_key="doc_findings",
)

infra_agent = LlmAgent(
  name="InfrastructureTelemetryAgent",
  model=MODEL_NAME,
  instruction=(
    "You are an Infrastructure Telemetry Specialist. Retrieve customer deployment region and "
    "incident status using fetch_account_infrastructure."
  ),
  description="Retrieves customer infrastructure status, SLA tier, and active incident telemetry.",
  tools=[fetch_account_infrastructure],
  output_key="infra_status",
)

research_swarm = ParallelAgent(
  name="TechResearchSwarm",
  sub_agents=[doc_agent, infra_agent],
  description="Concurrently gathers technical documentation and infrastructure telemetry.",
)


# --- Pattern 5: Generator and Critic Loop ---
def _generator_instruction(ctx: Context) -> str:
  """Builds dynamic instruction for the technical support generator."""
  docs = ctx.state.get("doc_findings", "No documentation records.")
  infra = ctx.state.get("infra_status", "No infrastructure status records.")
  feedback = ctx.state.get("tone_feedback", "No previous review feedback.")
  return (
    "You are a Senior Technical Support Engineer.\n\n"
    f"Technical Documentation:\n{docs}\n\n"
    f"Infrastructure Telemetry:\n{infra}\n\n"
    f"Editorial & Quality Feedback:\n{feedback}\n\n"
    "Draft a thorough, empathetic, and highly actionable support response for the customer. "
    "Include root cause explanation, step-by-step diagnostic checklist, and next steps."
  )


tech_generator = LlmAgent(
  name="TechSupportGenerator",
  model=MODEL_NAME,
  instruction=_generator_instruction,
  description="Generates customer-ready technical support responses from research findings.",
  output_key="proposed_response",
)


def _critic_instruction(ctx: Context) -> str:
  """Builds dynamic instruction for the tone and quality critic."""
  resp = ctx.state.get("proposed_response", "")
  return (
    f"You are the Support Quality and Tone Gatekeeper.\n\n"
    f"Review the draft response:\n{resp}\n\n"
    "Checklist:\n"
    "1. Is the tone empathetic, professional, and clear?\n"
    "2. Are the technical remediation steps accurate and actionable?\n"
    "3. Does it reference relevant infrastructure context?\n\n"
    "CRITICAL RULE:\n"
    "- If the response meets all quality standards, YOU MUST CALL the 'exit_loop' tool.\n"
    "- If revisions are needed, provide concise bullet-pointed feedback."
  )


tone_critic = LlmAgent(
  name="ToneAndQualityCritic",
  model=MODEL_NAME,
  instruction=_critic_instruction,
  tools=[exit_loop],
  description="Reviews support responses for quality, accuracy, and tone, exiting the loop upon approval.",
  output_key="tone_feedback",
)

quality_loop = LoopAgent(
  name="SupportQualityLoop",
  sub_agents=[tech_generator, tone_critic],
  max_iterations=2,
  description="Ensures technical responses meet enterprise customer experience standards.",
)

# --- Pattern 1: Sequential Support Pipeline ---
tech_pipeline = SequentialAgent(
  name="TechnicalSupportPipeline",
  sub_agents=[research_swarm, quality_loop],
  description="Handles technical issues by performing parallel research and quality-checked response generation.",
)

# Specialist Agent: Billing
billing_agent = LlmAgent(
  name="BillingSpecialist",
  model=MODEL_NAME,
  instruction=(
    "You are an enterprise Billing Specialist. Answer invoice, payment method, subscription, "
    "and pricing queries with clarity and professionalism."
  ),
  description="Handles billing inquiries, invoices, payment methods, and account upgrades.",
)

# --- Pattern 2: Root Coordinator Concierge ---
enterprise_concierge = LlmAgent(
  name="EnterpriseSupportConcierge",
  model=MODEL_NAME,
  instruction=(
    "You are the Central Enterprise Support Concierge. Analyze incoming customer inquiries and route:\n"
    "- TechnicalSupportPipeline: For technical outages, 5xx/4xx errors, API bugs, performance degradation, or architecture questions.\n"
    "- BillingSpecialist: For invoice queries, payment receipts, subscription renewals, or refund requests."
  ),
  description="Main concierge routing customer inquiries between Technical Support and Billing.",
  sub_agents=[tech_pipeline, billing_agent],
)

# Expose root agent for ADK compatibility
root_agent = enterprise_concierge


def create_composite_support_system(model: str = MODEL_NAME) -> LlmAgent:
  """Factory function to build the multi-pattern enterprise support system.

  Args:
    model: The Gemini model identifier to use across all sub-agents.

  Returns:
    LlmAgent configured as the root concierge with nested parallel, sequential, and loop agents.
  """
  d_agent = LlmAgent(
    name="DocumentationSearchAgent",
    model=model,
    instruction=(
      "You are an API Documentation Specialist. Look up diagnostic documentation and resolution steps "
      "for the technical issue using fetch_api_docs."
    ),
    description="Searches API documentation and troubleshooting playbooks.",
    tools=[fetch_api_docs],
    output_key="doc_findings",
  )

  i_agent = LlmAgent(
    name="InfrastructureTelemetryAgent",
    model=model,
    instruction=(
      "You are an Infrastructure Telemetry Specialist. Retrieve customer deployment region and "
      "incident status using fetch_account_infrastructure."
    ),
    description="Retrieves customer infrastructure status, SLA tier, and active incident telemetry.",
    tools=[fetch_account_infrastructure],
    output_key="infra_status",
  )

  swarm = ParallelAgent(
    name="TechResearchSwarm",
    sub_agents=[d_agent, i_agent],
    description="Concurrently gathers technical documentation and infrastructure telemetry.",
  )

  gen = LlmAgent(
    name="TechSupportGenerator",
    model=model,
    instruction=_generator_instruction,
    description="Generates customer-ready technical support responses from research findings.",
    output_key="proposed_response",
  )

  crt = LlmAgent(
    name="ToneAndQualityCritic",
    model=model,
    instruction=_critic_instruction,
    tools=[exit_loop],
    description="Reviews support responses for quality, accuracy, and tone, exiting the loop upon approval.",
    output_key="tone_feedback",
  )

  loop = LoopAgent(
    name="SupportQualityLoop",
    sub_agents=[gen, crt],
    max_iterations=2,
    description="Ensures technical responses meet enterprise customer experience standards.",
  )

  tech_pipe = SequentialAgent(
    name="TechnicalSupportPipeline",
    sub_agents=[swarm, loop],
    description="Handles technical issues via parallel doc/history research and quality-checked responses.",
  )

  bill = LlmAgent(
    name="BillingSpecialist",
    model=model,
    instruction=(
      "You are an enterprise Billing Specialist. Answer invoice, payment method, subscription, "
      "and pricing queries with clarity and professionalism."
    ),
    description="Handles billing inquiries, invoices, payment methods, and account upgrades.",
  )

  return LlmAgent(
    name="EnterpriseSupportConcierge",
    model=model,
    instruction=(
      "You are the Central Enterprise Support Concierge. Analyze incoming customer inquiries and route:\n"
      "- TechnicalSupportPipeline: For technical outages, 5xx/4xx errors, API bugs, performance degradation, or architecture questions.\n"
      "- BillingSpecialist: For invoice queries, payment receipts, subscription renewals, or refund requests."
    ),
    description="Main concierge routing customer inquiries between Technical Support and Billing.",
    sub_agents=[tech_pipe, bill],
  )


if __name__ == "__main__":
  from agent_tools import AgentRunner

  runner = AgentRunner(agent=enterprise_concierge)
  query = "We are encountering 504 Gateway Timeouts in us-central1 on our backend API."
  print(f"Customer Query: {query}\n")
  response = runner.prompt(query)
  print("\nConcierge Response:\n")
  print(response)
