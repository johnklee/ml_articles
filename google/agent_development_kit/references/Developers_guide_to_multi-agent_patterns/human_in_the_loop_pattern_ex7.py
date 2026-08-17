#!/usr/bin/env python3
"""Human-in-the-Loop Pattern Example using Google Agent Development Kit (ADK).

This module implements safety gates and human authorization for high-stakes actions:
1. ApprovalTool: Custom tool intercepting operations above safety thresholds to require human sign-off.
2. TransactionAgent (LlmAgent): Processes routine transfers directly, but invokes the ApprovalTool
   for high-value transactions or destructive actions.
3. AuditAndReceiptAgent (LlmAgent): Generates a formal compliance record and financial receipt.
4. SafeFinancialWorkflow (SequentialAgent): Coordinates the secure transaction and audit pipeline.
"""

from typing import Any, Dict
from google.adk.agents import LlmAgent, SequentialAgent


MODEL_NAME = "gemini-3.5-flash"


def request_human_approval(
  action_description: str, amount_usd: float, recipient: str
) -> Dict[str, Any]:
  """Requests authorization from a human operator or security officer.

  Args:
    action_description: Description of the high-stakes transaction or operation.
    amount_usd: The dollar amount associated with the operation.
    recipient: The recipient entity or destination account.

  Returns:
    A dictionary containing approval status, approver identity, and authorization token.
  """
  print(
    f"\n🛡️ [HUMAN-IN-THE-LOOP INTERVENTION] Authorizing '{action_description}' "
    f"for ${amount_usd:,.2f} to '{recipient}'."
  )

  # Automated policy check for demo: reject transactions exceeding $500,000 limit
  if amount_usd > 500000:
    return {
      "status": "REJECTED",
      "reason": "Amount exceeds single-transfer safety limit ($500,000 USD).",
      "approver": "SecurityOfficer_Admin",
    }

  return {
    "status": "APPROVED",
    "approver": "SecurityOfficer_Admin",
    "authorization_token": "AUTH-SAFE-2025-SEC99",
    "timestamp_utc": "2025-12-16T14:30:00Z",
  }


# Step 1: Transaction Processing Agent with Safety Tool
transaction_agent = LlmAgent(
  name="TransactionAgent",
  model=MODEL_NAME,
  instruction=(
    "You are a Financial Transaction Processing Agent. "
    "For transactions exceeding $1,000 USD or sensitive external wire transfers, "
    "YOU MUST CALL the request_human_approval tool before completing the transaction. "
    "For small routine transactions (<= $1,000 USD), you may process directly without human approval. "
    "Summarize the transaction state and approval details in your response."
  ),
  description="Processes financial transactions and invokes human authorization gates when required.",
  tools=[request_human_approval],
  output_key="transaction_result",
)

# Step 2: Audit and Receipt Agent
audit_agent = LlmAgent(
  name="AuditAndReceiptAgent",
  model=MODEL_NAME,
  instruction=(
    "You are a Compliance Officer and Receipt Generator. "
    "Read the transaction execution details from:\n{transaction_result}\n\n"
    "Generate an official compliance receipt including: Transaction Status, Authorization Details, "
    "and an Audit Log table."
  ),
  description="Generates formal compliance records and transaction audit logs.",
)

# Sequential Workflow
workflow = SequentialAgent(
  name="SafeFinancialTransferWorkflow",
  sub_agents=[transaction_agent, audit_agent],
  description="Human-in-the-loop workflow requiring explicit human authorization for high-stakes transfers.",
)

# Expose root agent for ADK compatibility
root_agent = workflow


def create_human_in_the_loop_pipeline(model: str = MODEL_NAME) -> SequentialAgent:
  """Factory function to build a Human-in-the-Loop financial safety pipeline.

  Args:
    model: The Gemini model identifier to use across all sub-agents.

  Returns:
    SequentialAgent configured with a transaction agent and compliance auditor.
  """
  txn = LlmAgent(
    name="TransactionAgent",
    model=model,
    instruction=(
      "You are a Financial Transaction Processing Agent. "
      "For transactions exceeding $1,000 USD or sensitive external wire transfers, "
      "YOU MUST CALL the request_human_approval tool before completing the transaction. "
      "For small routine transactions (<= $1,000 USD), you may process directly without human approval."
    ),
    description="Processes financial transactions and invokes human authorization gates when required.",
    tools=[request_human_approval],
    output_key="transaction_result",
  )

  audit = LlmAgent(
    name="AuditAndReceiptAgent",
    model=model,
    instruction=(
      "You are a Compliance Officer and Receipt Generator. "
      "Read the transaction execution details from:\n{transaction_result}\n\n"
      "Generate an official compliance receipt including: Transaction Status, Authorization Details, "
      "and an Audit Log table."
    ),
    description="Generates formal compliance records and transaction audit logs.",
  )

  return SequentialAgent(
    name="SafeFinancialTransferWorkflow",
    sub_agents=[txn, audit],
    description="Human-in-the-loop workflow requiring explicit human authorization for high-stakes transfers.",
  )


if __name__ == "__main__":
  from agent_tools import AgentRunner

  runner = AgentRunner(agent=workflow)
  prompt = "Please execute an external wire transfer of $45,000 to vendor 'CloudScale Solutions' for GPU cluster hosting."
  print(f"User Request: {prompt}\n")
  response = runner.prompt(prompt)
  print("\nFinal Output:\n")
  print(response)
