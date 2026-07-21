"""Application validation tests for Sprint 2 backend readiness."""

from alembic.config import Config
from alembic.script import ScriptDirectory

from app.main import create_app


def test_application_boots_and_registers_expected_routes() -> None:
    app = create_app()
    schema = app.openapi()
    paths = schema["paths"].keys()

    assert "/health" in paths
    assert "/health/live" in paths
    assert "/health/ready" in paths
    assert "/api/v1/customers" in paths
    assert "/api/v1/interactions" in paths
    assert "/api/v1/complaints" in paths
    assert "/api/v1/workflows" in paths
    assert "/api/v1/notifications" in paths
    assert "/api/v1/conversations" in paths


def test_openapi_generation_succeeds() -> None:
    app = create_app()
    schema = app.openapi()

    assert schema["openapi"].startswith("3.")
    assert "/api/v1/complaints" in schema["paths"]
    assert "/api/v1/customers" in schema["paths"]
    assert "/api/v1/interactions" in schema["paths"]
    assert "/api/v1/workflows" in schema["paths"]
    assert "/api/v1/notifications" in schema["paths"]


def test_alembic_migration_chain_is_linear() -> None:
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)

    heads = script.get_heads()
    revisions = list(script.walk_revisions(base="base", head="heads"))

    assert len(heads) == 1
    assert heads[0] == "20260721_1100"
    assert len(revisions) == 15