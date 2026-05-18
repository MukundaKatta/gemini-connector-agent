"""gemini-connector-agent dashboard."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gemini_connector_agent.runner import ask  # noqa: E402


st.set_page_config(page_title="gemini-connector-agent", layout="wide", page_icon=":electric_plug:")
st.title("gemini-connector-agent")
st.caption(
    "Fivetran connector-health triage agent on Google Cloud Agent Builder "
    "(ADK) + Gemini 2.5, wired to the Fivetran MCP server. Apache 2.0."
)

with st.sidebar:
    st.header("Triage Fivetran")
    question = st.text_area(
        "Your question",
        value="Which Fivetran connectors are broken right now and why?",
        height=120,
    )
    model = st.selectbox(
        "Gemini model",
        options=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite"],
        index=0,
    )
    stub = st.toggle(
        "Use stub Fivetran MCP",
        value=True,
        help="On = local stub with five canned connectors. Off = real account (set FIVETRAN_API_KEY + FIVETRAN_API_SECRET).",
    )
    run = st.button("Run triage", type="primary", use_container_width=True)
    st.divider()
    st.caption(
        f"Project: `{os.getenv('GOOGLE_CLOUD_PROJECT', 'not-set')}`  "
        f"Vertex AI: `{os.getenv('GOOGLE_GENAI_USE_VERTEXAI', 'true')}`"
    )

st.markdown(
    """
The agent walks these Fivetran MCP tools to triage connector health:
- **list_connectors** to see all connectors at a glance
- **get_connector** for a specific connector's details
- **list_destinations** / **get_destination** for Snowflake / BigQuery setup status
- **get_connector_sync_history** to confirm recurring vs transient failures
"""
)

if run:
    with st.status("Running Vertex AI Gemini...", expanded=True) as status:
        t0 = time.perf_counter()
        try:
            resp = ask(question, stub=stub, model=model)
        except Exception as e:  # pragma: no cover
            status.update(label=f"Error: {e}", state="error")
            st.exception(e)
            st.stop()
        elapsed = (time.perf_counter() - t0) * 1000
        status.update(label=f"Done in {elapsed:.0f} ms", state="complete")

    st.subheader("Triage")
    st.markdown(resp.final_text or "_(no final response)_")

    with st.expander(f"Agent event trace ({len(resp.events)} events)"):
        for i, ev in enumerate(resp.events):
            st.markdown(f"**{i}.** author=`{ev.get('author')}` final=`{ev.get('is_final')}`")
            text = ev.get("text") or ""
            if text:
                st.code(text[:1500], language=None)
else:
    st.info("Use the sidebar to fire a triage against the stub Fivetran MCP.")
