from datetime import UTC, datetime, timedelta

import pytest

from app.domain.models import AssistantChatHistoryMessage, UserChatHistoryMessage
from app.services.chat_history_store import ChatHistoryStore


@pytest.mark.asyncio
async def test_missing_chat_history_loads_empty_messages(tmp_path):
    store = ChatHistoryStore(tmp_path)

    assert await store.load_messages() == []


@pytest.mark.asyncio
async def test_damaged_chat_history_loads_empty_messages(tmp_path):
    (tmp_path / "chat-history.json").write_text("{broken", encoding="utf-8")
    store = ChatHistoryStore(tmp_path)

    assert await store.load_messages() == []


@pytest.mark.asyncio
async def test_chat_history_trims_to_recent_24_hours_and_60_messages(tmp_path):
    store = ChatHistoryStore(tmp_path)
    now = datetime(2026, 6, 14, 20, 0, tzinfo=UTC)
    old = UserChatHistoryMessage(
        role="user",
        content="old",
        createdAt=(now - timedelta(hours=25)).isoformat(),
    )
    recent = [
        UserChatHistoryMessage(
            role="user",
            content=f"u{index}",
            createdAt=(now - timedelta(minutes=60 - index)).isoformat(),
        )
        for index in range(61)
    ]

    warnings = await store.append_messages([old, *recent], now=now)
    messages = await store.load_messages(now=now)

    assert warnings == []
    assert len(messages) == 60
    assert messages[0].role == "user"
    assert messages[0].content == "u1"
    assert messages[-1].content == "u60"


@pytest.mark.asyncio
async def test_chat_history_keeps_assistant_snapshot(tmp_path):
    store = ChatHistoryStore(tmp_path)
    now = datetime(2026, 6, 14, 20, 0, tzinfo=UTC)
    assistant = AssistantChatHistoryMessage(
        role="assistant",
        reply="推荐鸡肉饭",
        cards=[],
        toolCalls=[{"id": "tool_1", "name": "search_meals", "status": "success"}],
        warnings=["历史保存较慢"],
        profileUpdates=[{"patch": {"likedIngredients": ["chicken"]}}],
        createdAt=now.isoformat(),
    )

    await store.append_messages([assistant], now=now)
    messages = await store.load_messages(now=now)

    assert len(messages) == 1
    assert messages[0].role == "assistant"
    assert messages[0].reply == "推荐鸡肉饭"
    assert messages[0].toolCalls[0]["name"] == "search_meals"
    assert messages[0].profileUpdates[0]["patch"] == {"likedIngredients": ["chicken"]}
