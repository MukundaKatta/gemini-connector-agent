# Google Cloud Rapid Agent Hackathon — Fivetran partner track submission

Devpost: https://rapid-agent.devpost.com
Deadline: 2026-06-11 14:00 PDT
Track: **Fivetran**

This is the seventh substantively-different submission from Mukunda Katta
to this hackathon, completing the Google Cloud Rapid Agent partner-track
sweep (rule 7B explicitly allows multiple unique submissions):

- `ragvitals` — RAG drift agent
- `gemini-ops-agent` — Dynatrace MCP incident investigator
- `gemini-eval-agent` — Arize Phoenix MCP LLM-eval auditor
- `gemini-data-agent` — MongoDB MCP NL-to-query agent
- `gemini-search-agent` — Elastic MCP NL-to-search agent
- `gemini-pipeline-agent` — GitLab MCP CI-failure triage
- `gemini-connector-agent` (this entry) — Fivetran MCP data-pipeline health triage

Six partner MCPs, six substantively-different agents. The same
`LlmAgent` + `McpToolset` shape carried across every integration.

## Rule compliance

| Rule | How we meet it |
|---|---|
| Powered by Gemini | gemini-2.5-flash via Vertex AI |
| Powered by Google Cloud Agent Builder | `google.adk.agents.LlmAgent` (ADK) |
| Integrates a Partner's MCP server | Tool surface matches the official `fivetran/fivetran-mcp` server (uvx-installable from the official GitHub repo); stub for demos, real account via env vars |
| Newly created during Contest Period | Repo init 2026-05-18, within May 5 – Jun 11 window |
| Original creation, not extension | Standalone repo |
| OSI license at repo root | Apache 2.0 |
| Runs on web | Streamlit dashboard, Cloud Run deployable |

## Elevator pitch
A Gemini agent that triages Fivetran connector health, quoting error
codes verbatim and recommending the exact remediation step from the
sync history.

## Description
gemini-connector-agent treats every "what's wrong with my pipelines?"
question as a connector-health triage. The agent walks the Fivetran MCP
tools in order: `list_connectors` for an at-a-glance status,
`get_connector_sync_history` to confirm a failure is recurring (not
transient), and `get_connector` / `get_destination` for full details.

A real Vertex AI Gemini run on the canned dataset identified
`salesforce-main` as broken with verbatim error code
`API_DISABLED_FOR_ORG` and quoted the full remediation message (re-enable
API access in Salesforce Setup → Profiles → System Administrator →
Administrative Permissions). 5/5 recent sync runs failed; the agent
recognized this as a recurring config issue, not a flake, and proposed
the right next step.

## Built with
python, gemini, gemini-2-5, vertex-ai, google-cloud-agent-builder,
agent-development-kit, mcp, model-context-protocol, fivetran,
fivetran-mcp, data-pipelines, streamlit, google-cloud-run, apache-2

## Try it out
- Code repo: https://github.com/MukundaKatta/gemini-connector-agent
- Live demo (Cloud Run): <PASTE_AFTER_DEPLOY>
- Demo video (YouTube unlisted): <PASTE_AFTER_REC>
