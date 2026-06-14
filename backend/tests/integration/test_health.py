import json
import logging

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.main import create_app


@pytest.mark.asyncio
async def test_health_returns_success(tmp_path):
    settings = Settings()
    app = create_app(settings=settings, data_dir=tmp_path)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"code": 200, "message": "success", "data": {"status": "ok"}}


def test_create_app_logs_startup_switches_without_api_key(tmp_path, caplog):
    settings = Settings(
        openrouter_api_key="sk-startup-secret",
        openrouter_model="deepseek/deepseek-chat",
        log_full_user_message=False,
        log_full_source_text=False,
    )

    with caplog.at_level(logging.INFO, logger="app.main"):
        create_app(settings=settings, data_dir=tmp_path)

    payload = json.loads(caplog.records[0].message)
    assert payload["event"] == "app_startup"
    assert payload["openrouterModel"] == "deepseek/deepseek-chat"
    assert payload["logSwitches"]["logFullUserMessage"] is False
    assert "sk-startup-secret" not in caplog.text
