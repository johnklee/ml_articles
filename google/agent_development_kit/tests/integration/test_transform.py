from google.adk.evaluation.agent_evaluator import AgentEvaluator
import pytest


@pytest.mark.asyncio
async def test_with_single_test_file():
  """Test the agent's basic ability via a session file."""
  test_json_path = (
      "tests/integration/fixture/transform/evalsete613dc.evalset.json")
  await AgentEvaluator.evaluate(
      agent_module="evaluate_transform",
      eval_dataset_file_path_or_dir=test_json_path,
  )
