"""Stub Fivetran MCP server.

Exposes a slice of the official `fivetran/fivetran-mcp` tool surface
(`list_connectors`, `get_connector`, `list_destinations`,
`get_destination`, `get_connector_sync_history`) shaped so the same
agent code drops in unchanged against a real Fivetran tenant via the
official MCP server.

Run with: python -m gemini_connector_agent.mcp_stub
"""

from __future__ import annotations

import asyncio
import json
import random
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


NOW = datetime.now(timezone.utc)
_RNG = random.Random(2026)


@dataclass
class Connector:
    id: str
    name: str
    service: str          # postgres, salesforce, stripe, github, ...
    destination_id: str
    status: str           # active | paused | broken | incomplete
    sync_frequency_minutes: int
    last_sync_started_at: str
    last_sync_completed_at: str | None
    last_sync_status: str  # success | failure | in_progress
    last_sync_error: str | None = None
    monthly_active_rows: int = 0


_CONNECTORS: list[Connector] = [
    Connector(
        id="c_pg_prod_users",
        name="postgres-prod-users",
        service="postgres",
        destination_id="d_snowflake_prod",
        status="active",
        sync_frequency_minutes=60,
        last_sync_started_at=(NOW - timedelta(minutes=11)).isoformat(),
        last_sync_completed_at=(NOW - timedelta(minutes=4)).isoformat(),
        last_sync_status="success",
        last_sync_error=None,
        monthly_active_rows=4_812_310,
    ),
    Connector(
        id="c_salesforce_main",
        name="salesforce-main",
        service="salesforce",
        destination_id="d_snowflake_prod",
        status="broken",
        sync_frequency_minutes=360,
        last_sync_started_at=(NOW - timedelta(hours=2, minutes=3)).isoformat(),
        last_sync_completed_at=(NOW - timedelta(hours=1, minutes=58)).isoformat(),
        last_sync_status="failure",
        last_sync_error=(
            "API_DISABLED_FOR_ORG: REST API requests are disabled for this "
            "organization. Re-enable API access in Salesforce Setup > "
            "Profiles > System Administrator > Administrative Permissions."
        ),
        monthly_active_rows=812_402,
    ),
    Connector(
        id="c_stripe_billing",
        name="stripe-billing",
        service="stripe",
        destination_id="d_snowflake_prod",
        status="active",
        sync_frequency_minutes=15,
        last_sync_started_at=(NOW - timedelta(minutes=8)).isoformat(),
        last_sync_completed_at=(NOW - timedelta(minutes=6)).isoformat(),
        last_sync_status="success",
        last_sync_error=None,
        monthly_active_rows=204_117,
    ),
    Connector(
        id="c_github_audit",
        name="github-audit-logs",
        service="github",
        destination_id="d_bigquery_security",
        status="incomplete",
        sync_frequency_minutes=1440,
        last_sync_started_at=(NOW - timedelta(hours=14)).isoformat(),
        last_sync_completed_at=None,
        last_sync_status="in_progress",
        last_sync_error=None,
        monthly_active_rows=88_204,
    ),
    Connector(
        id="c_zendesk_support",
        name="zendesk-support",
        service="zendesk",
        destination_id="d_snowflake_prod",
        status="paused",
        sync_frequency_minutes=720,
        last_sync_started_at=(NOW - timedelta(days=3)).isoformat(),
        last_sync_completed_at=(NOW - timedelta(days=3) + timedelta(minutes=8)).isoformat(),
        last_sync_status="success",
        last_sync_error=None,
        monthly_active_rows=46_902,
    ),
]


_DESTINATIONS = [
    {"id": "d_snowflake_prod",      "service": "snowflake",  "region": "AWS_US_EAST_1",
     "setup_status": "connected", "name": "snowflake-prod"},
    {"id": "d_bigquery_security",   "service": "bigquery",   "region": "GCP_US_CENTRAL1",
     "setup_status": "connected", "name": "bigquery-security"},
]


def list_connectors_response() -> dict[str, Any]:
    return {"connectors": [asdict(c) for c in _CONNECTORS]}


def get_connector_response(connector_id: str) -> dict[str, Any]:
    for c in _CONNECTORS:
        if c.id == connector_id or c.name == connector_id:
            return asdict(c)
    return {"error": f"unknown connector {connector_id!r}"}


def list_destinations_response() -> dict[str, Any]:
    return {"destinations": _DESTINATIONS}


def get_destination_response(destination_id: str) -> dict[str, Any]:
    for d in _DESTINATIONS:
        if d["id"] == destination_id or d["name"] == destination_id:
            return d
    return {"error": f"unknown destination {destination_id!r}"}


def get_connector_sync_history_response(connector_id: str, limit: int = 5) -> dict[str, Any]:
    """Return a short canned sync history. Stable per connector_id so judges
    can reproduce the same answer twice in a row."""
    rng = random.Random(hash(connector_id) & 0xFFFFFFFF)
    runs = []
    for i in range(limit):
        started = NOW - timedelta(hours=i, minutes=rng.randint(0, 55))
        completed = started + timedelta(minutes=rng.randint(2, 14))
        # The broken connector has been failing for the last 3 days
        if connector_id.startswith("c_salesforce") and i < 12:
            status = "failure"
            err = "API_DISABLED_FOR_ORG"
        else:
            status = rng.choices(["success", "failure"], weights=[9, 1])[0]
            err = "RATE_LIMITED" if status == "failure" else None
        runs.append({
            "started_at":   started.isoformat(),
            "completed_at": completed.isoformat(),
            "status":       status,
            "error_code":   err,
            "rows_synced":  rng.randint(2_000, 220_000) if status == "success" else 0,
        })
    return {"connector_id": connector_id, "history": runs}


def _make_server() -> Server:
    server = Server("fivetran-stub")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(name="list_connectors",
                 description="List all Fivetran connectors on this account, with their current sync status, last error, and monthly active rows.",
                 inputSchema={"type": "object", "properties": {}, "required": []}),
            Tool(name="get_connector",
                 description="Fetch one connector's full details by id or name.",
                 inputSchema={"type": "object",
                              "properties": {"connector_id": {"type": "string"}},
                              "required": ["connector_id"]}),
            Tool(name="list_destinations",
                 description="List Fivetran destinations (e.g. Snowflake, BigQuery) and their setup status.",
                 inputSchema={"type": "object", "properties": {}, "required": []}),
            Tool(name="get_destination",
                 description="Fetch one destination's details by id or name.",
                 inputSchema={"type": "object",
                              "properties": {"destination_id": {"type": "string"}},
                              "required": ["destination_id"]}),
            Tool(name="get_connector_sync_history",
                 description="Return the last N sync runs for a connector with started_at, completed_at, status, error_code, and rows_synced. Use this to spot a recurring failure.",
                 inputSchema={"type": "object",
                              "properties": {
                                  "connector_id": {"type": "string"},
                                  "limit": {"type": "integer", "default": 5},
                              },
                              "required": ["connector_id"]}),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        a = arguments
        if name == "list_connectors":
            payload = list_connectors_response()
        elif name == "get_connector":
            payload = get_connector_response(a.get("connector_id", ""))
        elif name == "list_destinations":
            payload = list_destinations_response()
        elif name == "get_destination":
            payload = get_destination_response(a.get("destination_id", ""))
        elif name == "get_connector_sync_history":
            payload = get_connector_sync_history_response(
                a.get("connector_id", ""), int(a.get("limit") or 5),
            )
        else:
            payload = {"error": f"unknown tool {name!r}"}
        return [TextContent(type="text", text=json.dumps(payload, indent=2, default=str))]

    return server


async def _main() -> None:
    server = _make_server()
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
