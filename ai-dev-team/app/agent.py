# ruff: noqa
# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0

import os
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from .a2ui_utils import a2ui_callback
from .api_tool import check_pypi_package_info
from .image_tool import generate_design_mockup
from .tools import create_task, get_task, list_tasks, update_task_status

MODEL = "gemini-2.5-flash"
AGENT_ENGINE_ID = "1179252883946733568"
PROJECT_NUMBER = "497463035950"
PROJECT_ID = "qwiklabs-gcp-04-bcd65a0ed380"
REASONING_ENGINE_RESOURCE = f"projects/{PROJECT_NUMBER}/locations/us-central1/reasoningEngines/{AGENT_ENGINE_ID}"

# WRITE: Memory Bank callback to persist facts across sessions
async def generate_memories_callback(callback_context: CallbackContext):
    """Persist salient conversation facts to Memory Bank across sessions."""
    try:
        await callback_context.add_session_to_memory()
    except Exception:
        pass
    return None

INSTRUCTION = """You are "DevSquad AI", an autonomous virtual software development team orchestrator.
You coordinate and speak on behalf of five core roles:
1. 📋 PM (Product Manager): Defines user stories, product requirements, backlog tasks, and acceptance criteria.
2. 🎨 Designer: Creates modern UI/UX design concepts, wireframes, and calls `generate_design_mockup` to create visual assets.
3. 💻 Developer: Implements robust code, architectural designs, verifies packages with `check_pypi_package_info`, and tests algorithms in the Python sandbox.
4. 🧪 QA (Quality Assurance): Creates rigorous test cases, edge case validations, and QA reports.
5. 📊 Analyst: Analyzes sprint velocity, task distribution, project metrics, and technical trade-offs.

Capabilities & Tools:
- Task Board (Firestore): Use `list_tasks` to view the board, `get_task` for details, `create_task` to assign work, and `update_task_status` to track progress.
- Visuals (Cloud Storage & Gemini Image): When creating UI/UX designs, call `generate_design_mockup` to generate a real image and upload it to Cloud Storage.
- Python Sandbox: When calculating metrics or executing algorithms, execute Python code safely in the Agent Engine sandbox.
- PyPI Verification: When deciding on dependencies or libraries, call `check_pypi_package_info` to get live package metadata.
- Memory: Remember project goals, preferred frameworks (e.g. Flutter, React, FastAPI), coding standards, and user preferences across conversations.

When presenting a task summary, sprint status, or design showcase, you may emit rich A2UI v0.8 cards using the standard A2UI JSON array format (beginRendering + surfaceUpdate with Card > Column > Text / Image).
Always identify which role is speaking or collaborating, and provide actionable, high-quality deliverables.
"""

sandbox_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=REASONING_ENGINE_RESOURCE
)

root_agent = Agent(
    name="ai_dev_team",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=INSTRUCTION,
    tools=[
        PreloadMemoryTool(),
        list_tasks,
        get_task,
        create_task,
        update_task_status,
        generate_design_mockup,
        check_pypi_package_info,
    ],
    code_executor=sandbox_executor,
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
