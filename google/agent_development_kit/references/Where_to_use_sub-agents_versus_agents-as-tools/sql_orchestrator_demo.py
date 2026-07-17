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


class AgentExecutor:
    """Wraps coordinator agent and provides a synchronous prompt method for execution."""

    def __init__(
        self,
        agent: BaseAgent):
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

    async def prompt_async(self, user_request: str) -> str:
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
        import asyncio
        import nest_asyncio
        nest_asyncio.apply() # Allows nesting of asyncio event loops
        return asyncio.run(self.prompt_async(user_request))

