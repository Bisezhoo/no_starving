import pytest

from app.core.config import Settings
from app.services import default_agent
from app.services.openrouter_client import OpenRouterClient


def test_default_agent_passes_outbound_http_proxy_to_external_clients(monkeypatch, tmp_path):
    captured = {}

    class FakeMealDbClient:
        def __init__(self, base_url, proxy=None, trust_env=True):
            captured["meal"] = {"base_url": base_url, "proxy": proxy, "trust_env": trust_env}

    class FakeCocktailDbClient:
        def __init__(self, base_url, proxy=None, trust_env=True):
            captured["cocktail"] = {"base_url": base_url, "proxy": proxy, "trust_env": trust_env}

    class FakeOpenRouterClient:
        def __init__(self, api_key, model, base_url, proxy=None, trust_env=True):
            captured["openrouter"] = {"api_key": api_key, "model": model, "base_url": base_url, "proxy": proxy, "trust_env": trust_env}

    monkeypatch.setattr(default_agent, "MealDbClient", FakeMealDbClient)
    monkeypatch.setattr(default_agent, "CocktailDbClient", FakeCocktailDbClient)
    monkeypatch.setattr(default_agent, "OpenRouterClient", FakeOpenRouterClient)

    settings = Settings(
        OPENROUTER_API_KEY="sk-test",
        OPENROUTER_MODEL="deepseek/deepseek-chat",
        OUTBOUND_HTTP_PROXY="http://127.0.0.1:7890",
        OUTBOUND_HTTP_TRUST_ENV=False,
        _env_file=None,
    )

    default_agent.build_default_agent(settings, data_dir=tmp_path)

    assert captured["meal"]["proxy"] == "http://127.0.0.1:7890"
    assert captured["cocktail"]["proxy"] == "http://127.0.0.1:7890"
    assert captured["openrouter"]["proxy"] == "http://127.0.0.1:7890"
    assert captured["meal"]["trust_env"] is False
    assert captured["cocktail"]["trust_env"] is False
    assert captured["openrouter"]["trust_env"] is False


@pytest.mark.asyncio
async def test_openrouter_client_passes_proxy_to_httpx(monkeypatch):
    captured = {}

    class FakeStreamResponse:
        def raise_for_status(self):
            return None

        async def aiter_lines(self):
            yield "data: [DONE]"

    class FakeStreamContext:
        async def __aenter__(self):
            return FakeStreamResponse()

        async def __aexit__(self, exc_type, exc, traceback):
            return None

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return None

        def stream(self, *args, **kwargs):
            return FakeStreamContext()

    monkeypatch.setattr("app.services.openrouter_client.httpx.AsyncClient", FakeAsyncClient)

    client = OpenRouterClient(
        api_key="sk-test",
        model="deepseek/deepseek-chat",
        base_url="https://openrouter.ai/api/v1",
        proxy="http://127.0.0.1:7890",
        trust_env=False,
    )

    lines = [line async for line in client.stream_chat(messages=[], tools=[])]

    assert lines == ["data: [DONE]"]
    assert captured["proxy"] == "http://127.0.0.1:7890"
    assert captured["trust_env"] is False
