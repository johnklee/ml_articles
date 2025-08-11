from google.adk.agents import Agent
from . import prompt


root_agent = Agent(
    name="automation_analyst",
    model="gemini-2.0-flash",
    description=(
        "Give me a role or a job description and I'll break it down to tasks "
        "and analyze for automation potential"
    ),
    instruction=prompt.ROOT_PROMPT,
)
