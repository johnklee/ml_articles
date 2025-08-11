from typing import Any

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from . import prompt


def transform(
    current_unit: str,
    current_value: int,
    target_unit: str) -> dict[str, Any]:
  """Transform the value of current unit to target unit.

  Args:
    current_unit: The unit of current value. (`N`, `M`, `P`, `Q` or `G`)
    current_value: The current value.
    target_unit: The target unit (`N`, `M`, `P`, `Q` or `G`)

  Returns:
    `dict` object containing the keys:
    - status: 'success' or 'error' as transform status.
    - process: The message of transforming process.
    - result: The final transforming result.
  """
  transform_rules = {
        'N': {'M': 13},
        'M': {'P': 10},
        'P': {'Q': 5},
        'Q': {'G': 3}
  }

  # Create a reverse mapping for transformations
  for unit, conversions in list(transform_rules.items()):
    for target, value in list(conversions.items()):
      if target not in transform_rules:
        transform_rules[target] = {}
        transform_rules[target][unit] = 1 / value

  all_units = set(transform_rules.keys())

  if current_unit not in all_units:
    return {
        'status': 'error',
          'process': f'Unknown unit as `{current_unit}`!',
          'result': -1,
    }
  if target_unit not in all_units:
    return {
        'status': 'error',
        'process': f'Unknown unit as `{target_unit}`!',
        'result': -1,
    }

  # BFS to find the shortest path of transformations
  queue = [(current_unit, current_value, f'{current_value}{current_unit}', [current_unit])]
  visited = {current_unit}

  while queue:
    unit, value, process, path = queue.pop(0)

    if unit == target_unit:
      return {
          'status': 'success',
          'process': process,
          'result': value,
      }

    for next_unit, conversion_factor in transform_rules.get(unit, {}).items():
      if next_unit not in visited:
        visited.add(next_unit)
        new_value = value * conversion_factor
        new_process = (
            f'{process}; {value}{unit} = {new_value}{next_unit}' if unit != current_unit
            else f'{current_value}{current_unit} = {new_value}{next_unit}')
        new_path = path + [next_unit]
        queue.append((next_unit, new_value, new_process, new_path))

    # If no path is found
    return {
        'status': 'error',
        'process': f'No conversion path found from {current_unit} to {target_unit}.',
        'result': -1,
    }


transform_tool = FunctionTool(func=transform)


root_agent = Agent(
    name="unit_exchanger",
    model="gemini-2.0-flash",
    description=(
        "User will given a number with unit and you will transform it into the desired unit."
    ),
    instruction=prompt.ROOT_PROMPT,
    tools=[transform_tool],
)
