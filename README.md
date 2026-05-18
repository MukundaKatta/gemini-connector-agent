# gemini-connector-agent

A Fivetran connector-health triage agent built on Google Cloud Agent
Builder (ADK), Gemini 2.5, and the Fivetran MCP server.

Open source under Apache 2.0.

## What it does

You ask "which connectors are broken and why?" The agent walks the
Fivetran MCP tools (`list_connectors`, `get_connector_sync_history`,
`get_destination`), identifies broken connectors, quotes their error
codes verbatim, and recommends the exact next step.

Tool surface matches the official
[`fivetran/fivetran-mcp`](https://github.com/fivetran/fivetran-mcp). A
stub MCP server ships with the repo — canned dataset: 5 connectors
(Postgres, Salesforce, Stripe, GitHub, Zendesk) across 2 destinations
(Snowflake, BigQuery), one of which (Salesforce) is in a known-broken
state with a realistic recurring `API_DISABLED_FOR_ORG` failure.

## Try it locally

```bash
git clone https://github.com/MukundaKatta/gemini-connector-agent
cd gemini-connector-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=your-project
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_LOCATION=us-central1

PYTHONPATH=src streamlit run app/dashboard.py
```

## Try it against a real Fivetran account

```bash
export FIVETRAN_API_KEY="..."
export FIVETRAN_API_SECRET="..."
```

Untick "Use stub Fivetran MCP" in the sidebar. The agent now spawns the
official Fivetran MCP server via `uvx`.

## Tests

```bash
PYTHONPATH=src pytest -q
```

13 tests cover stub responses + the agent wiring.

## License

Apache 2.0. Mukunda Katta, independent developer.
