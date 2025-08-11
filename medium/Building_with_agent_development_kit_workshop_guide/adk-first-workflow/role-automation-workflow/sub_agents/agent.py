from google.adk.agents.llm_agent import Agent

from . import prompt

# --- 1. Define Sub-Agents for Each Pipeline Stage ---

job_description_agent = Agent(
    model='gemini-2.0-flash',
    name="job_description_agent",
    description="A helpful agent to find job descriptions from google search",
    instruction=prompt.JOB_DESCRIPTION_AGENT_PROMPT,
    output_key="job_description",
)

workflow_analysis_agent = Agent(
    model='gemini-2.0-flash',
    name="workflow_analysis_agent",
    description="A helpful agent to analyze workflows",
    instruction=prompt.WORKFLOW_ANALYSIS_AGENT_PROMPT,
    output_key="workflow_analysis",
)

prompt_engineer_agent = Agent(
    model='gemini-2.0-flash',
    name="prompt_engineer_agent",
    description="selects high potential for optimazation from analysis and creates prompts, and adds them to the prompt library",
    instruction=prompt.PROMPT_ENGINEER_AGENT_PROMPT,
    output_key="prompt_library",
)
