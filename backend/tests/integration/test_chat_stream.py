import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.domain.models import SseEvent
from app.main import create_app
from app.services.agent_orchestrator import AgentOrchestrator


class FakeAgent:
    async def run(self, message: str):
        yield SseEvent(event="meta", data={"requestId": "req_test"})
        yield SseEvent(event="done", data={"reply": f"收到：{message}", "cards": [], "toolCalls": [], "warnings": []})


@pytest.mark.asyncio
async def test_chat_rejects_empty_message():
    app = create_app(agent=FakeAgent())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/chat/stream", json={"message": "   "})

    assert response.status_code == 400
    assert response.json()["message"] == "message 不能为空"


@pytest.mark.asyncio
async def test_chat_stream_returns_sse_events():
    app = create_app(agent=FakeAgent())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/chat/stream", json={"message": "我想吃鸡肉"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: meta" in response.text
    assert "event: done" in response.text


def test_create_app_builds_default_agent_when_settings_are_supplied(tmp_path):
    settings = Settings()
    app = create_app(settings=settings, data_dir=tmp_path)

    assert isinstance(app.state.agent, AgentOrchestrator)
