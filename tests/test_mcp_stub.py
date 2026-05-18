from gemini_connector_agent.mcp_stub import (
    _CONNECTORS,
    _DESTINATIONS,
    list_connectors_response,
    get_connector_response,
    list_destinations_response,
    get_destination_response,
    get_connector_sync_history_response,
)


def test_data_seeded():
    assert len(_CONNECTORS) >= 5
    assert len(_DESTINATIONS) == 2
    names = [c.name for c in _CONNECTORS]
    assert "salesforce-main" in names
    assert "stripe-billing" in names


def test_list_connectors_returns_all():
    payload = list_connectors_response()
    assert len(payload["connectors"]) == len(_CONNECTORS)


def test_list_connectors_includes_broken_one():
    payload = list_connectors_response()
    broken = [c for c in payload["connectors"] if c["status"] == "broken"]
    assert len(broken) == 1
    assert broken[0]["name"] == "salesforce-main"
    assert "API_DISABLED_FOR_ORG" in broken[0]["last_sync_error"]


def test_get_connector_by_name():
    payload = get_connector_response("salesforce-main")
    assert payload["service"] == "salesforce"
    assert payload["last_sync_status"] == "failure"


def test_get_connector_unknown_returns_error():
    payload = get_connector_response("does-not-exist")
    assert "error" in payload


def test_list_destinations_includes_snowflake_and_bigquery():
    payload = list_destinations_response()
    services = [d["service"] for d in payload["destinations"]]
    assert "snowflake" in services
    assert "bigquery" in services


def test_get_destination_by_id():
    payload = get_destination_response("d_snowflake_prod")
    assert payload["service"] == "snowflake"
    assert payload["setup_status"] == "connected"


def test_sync_history_for_salesforce_shows_recurring_failures():
    payload = get_connector_sync_history_response("c_salesforce_main", limit=10)
    failures = [r for r in payload["history"] if r["status"] == "failure"]
    assert len(failures) >= 8, "salesforce-main should show a recurring failure pattern"


def test_sync_history_returns_requested_limit():
    payload = get_connector_sync_history_response("c_pg_prod_users", limit=3)
    assert len(payload["history"]) == 3


def test_sync_history_records_have_required_fields():
    payload = get_connector_sync_history_response("c_stripe_billing", limit=2)
    for run in payload["history"]:
        assert set(run.keys()) >= {"started_at", "completed_at", "status", "error_code", "rows_synced"}
