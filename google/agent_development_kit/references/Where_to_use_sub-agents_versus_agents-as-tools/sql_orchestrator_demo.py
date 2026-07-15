#!/usr/bin/env python
"""Sample code to demonstrate SQL orchestrator agent."""
from typing import Any
import asyncio
import json
import os
import sqlite3
import pandas as pd

from google.adk.agents import LlmAgent, BaseAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import agent_tool
from google.genai import types

from IPython.display import Image, display


TEST_CSV_DATA_FILE = 'employees.csv'
FLASH_MODEL = "gemini-3.5-flash"


# 1. Load CSV into a Pandas DataFrame
df = pd.read_csv(TEST_CSV_DATA_FILE)

# 2. Connect to a temporary, in-memory SQLite database
conn = sqlite3.connect(':memory:')

# 3. Write the DataFrame to the SQL database
df.to_sql('Employee', conn, index=False, if_exists='replace')


# Sub-Agent: Text-to-SQL Translator
sql_generator_agent = LlmAgent(
    name="SQL_Generator",
    model=FLASH_MODEL,
    description="Translate natural language into SQL.",
    instruction=f"""
    You are an expert SQL assistant. Your job is to translate natural language questions into valid SQLite queries.
    The database contains a table named 'Employee' with the following schema:
    {EMPLOYEE_TABLE_SCHEMA}

    Respond ONLY with the executable SQL query string. Do not include markdown formatting or explanations.
    """
)


# Agent tool to execute SQL.
def execute_sql_query(sql_query: str, conn: Any = conn) -> str:
    """
    Executes a given SQL query string on the Employee database and returns the result as a JSON string.

    Args:
        sql_query (str): The SQL query string to be executed.
        conn (Any): An active database connection object (e.g., sqlite3 or SQLAlchemy connection).

    Returns:
        str: A JSON-formatted string containing the query results or error details.
    """
    try:
        # Execute query and load into a pandas DataFrame
        df_result = pd.read_sql_query(sql_query, conn)

        # Returns a JSON string representation of list of dictionaries
        return df_result.to_json(orient="records")

    except Exception as e:
        # Return a structured JSON error string so the LLM or ADK environment
        # can predictably parse it without breaking schema expectations.
        return json.dumps({
            "status": "error",
            "message": f"Error executing query: {str(e)}"
        })


# Tool to display chart on notebook.
def display_image(image_file_path: str) -> str:
    """
    Renders or registers a generated chart/image file so it can be viewed by the user.

    Args:
        image_file_path (str): The absolute file path to the saved image (e.g., '/tmp/chart.png').

    Returns:
        str: A confirmation status message verifying the file path is valid.
    """
    if not os.path.exists(image_file_path):
        return f"Error: File not found at {image_file_path}"

    # In a real ADK, instead of notebook's display(), you might log it,
    # upload it to an artifact store, or return a payload the UI understands.
    print(f"[ADK Tool] Displaying image located at: {image_file_path}")

    return json.dumps({
        "status": "success",
        "message": f"Image successfully loaded and rendered from {image_file_path}",
        "file_path": image_file_path
    })


# Sub-Agent: Generate the chart with given dataset.
chart_generator_agent = LlmAgent(
    name="Chart_Generator",
    model=FLASH_MODEL,
    instruction="""
    You are a data visualization expert. Given a dataset (provided as a JSON string) and a user request,
    your job is to generate Python code using matplotlib or seaborn to create a visually appealing chart.

    CRITICAL EXECUTION RULES:
    1. Label everything clearly: Ensure your code includes titles, X/Y axis labels, and legends where appropriate.
    2. Save the output: Your generated Python code must explicitly save the resulting figure as an image file into the '/tmp/' directory (e.g., `/tmp/generated_chart.png`).
    3. Do not leave plots open: Always include `plt.close()` or `plt.clf()` at the end of your script to prevent memory leaks in the backend environment.
    4. Call the Viewer Tool: Immediately after generating and saving the image file, you MUST invoke the `display_image` tool, passing the exact file path you saved the image to.
    """,
    tools=[display_image],
)


# Root agent
coordinator = LlmAgent(
    name="SQLCoordinator",
    model=FLASH_MODEL,
    instruction="TBD",
    description="Accept request, compose SQL to query the DB and generate the chart to display the result.",
    # allow_transfer=True is often implicit with sub_agents in AutoFlow
    sub_agents=[chart_generator_agent],
    tools=[
        execute_sql_query,
        agent_tool.AgentTool(agent=sql_generator_agent),
    ]
)


class AgentExecutor:
    """Wraps coordinator agent and provides a synchronous prompt method for execution."""

    def __init__(self, agent: BaseAgent = coordinator):
        self.agent = agent
        self.session_service = InMemorySessionService()
        self.app_name = "sql_orchestrator_app"
        self.user_id = "default_user"
        self.session_id = "default_session"
        self.runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service,
        )
        self._session_initialized = False

    async def _prompt_async(self, user_request: str) -> str:
        if not self._session_initialized:
            await self.session_service.create_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=self.session_id,
            )
            self._session_initialized = True

        user_content = types.Content(
            role="user", parts=[types.Part(text=user_request)]
        )

        final_response_content = ""
        async for event in self.runner.run_async(
            user_id=self.user_id,
            session_id=self.session_id,
            new_message=user_content,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_content = event.content.parts[0].text

        return final_response_content

    def prompt(self, user_request: str) -> str:
        """Receives user request as str, feeds into agent for execution, and returns the response as text."""
        return asyncio.run(self._prompt_async(user_request))

