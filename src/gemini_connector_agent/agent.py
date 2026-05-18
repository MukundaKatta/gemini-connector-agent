"""ADK Gemini agent wired to the Fivetran MCP server. Takes a question
about connector health and walks the Fivetran tools to triage which
connector is broken, what error code, and what to do about it."""

from __future__ import annotations

import os
import sys
from typing import Any


try:
    from google.adk.agents import LlmAgent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters
    _ADK_AVAILABLE = True
except ImportError:  # pragma: no cover
    _ADK_AVAILABLE = False


SYSTEM_PROMPT = """\
You are a Fivetran data-pipeline operator. The user asks about the
health of their data connectors, and you walk the Fivetran MCP tools
to find broken ones, identify the error, and recommend a fix.

Workflow:
1. Call `list_connectors` first so you can see all connectors and their
   current status at a glance.
2. For any connector with `status != "active"` or
   `last_sync_status == "failure"`, call `get_connector_sync_history`
   to confirm whether the failure is recurring or transient.
3. If the user asks about a specific connector by name, call
   `get_connector` directly.

Output a structured triage with EXACTLY these labeled sections:

ANSWER: <one sentence stating which connector is broken and why>
BROKEN CONNECTOR: <name + service + status>
ERROR: <error code + verbatim error message from the tool output>
HISTORY: <count of recent runs that failed vs succeeded>
ROOT CAUSE: <one-sentence explanation grounded in the tool output>
NEXT STEP: <one concrete action the data team should take>

Quote error messages and codes verbatim. Numbers must come from the
tool output, not from estimates.
"""


def _fivetran_toolset(stub: bool = True) -> Any:
    if not _ADK_AVAILABLE:
        raise ImportError("Install google-adk and mcp: pip install google-adk mcp")
    if stub:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "gemini_connector_agent.mcp_stub"],
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
    else:
        # Real Fivetran MCP server (github.com/fivetran/fivetran-mcp) via uvx
        params = StdioServerParameters(
            command="uvx",
            args=["--from", "git+https://github.com/fivetran/fivetran-mcp",
                  "fivetran-mcp"],
            env={
                **os.environ,
                "FIVETRAN_API_KEY":    os.environ["FIVETRAN_API_KEY"],
                "FIVETRAN_API_SECRET": os.environ["FIVETRAN_API_SECRET"],
            },
        )
    return McpToolset(connection_params=StdioConnectionParams(server_params=params))


def build_agent(model: str = "gemini-2.5-flash", stub: bool = True) -> Any:
    if not _ADK_AVAILABLE:
        return None
    return LlmAgent(
        model=model,
        name="gemini_connector_agent",
        instruction=SYSTEM_PROMPT,
        tools=[_fivetran_toolset(stub=stub)],
    )
