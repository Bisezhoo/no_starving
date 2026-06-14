from pathlib import Path
import logging

import pytest

from app.domain.models import AgentMemory, RecommendationRecord, TasteProfile
from app.services.memory_store import MemoryStore


@pytest.mark.asyncio
async def test_missing_files_load_empty_state(tmp_path):
    store = MemoryStore(tmp_path)

    assert await store.load_profile() == TasteProfile()
    assert await store.load_history() == []
    assert await store.load_agent_memory() == AgentMemory()


@pytest.mark.asyncio
async def test_damaged_json_loads_empty_state(tmp_path):
    (tmp_path / "taste-profile.json").write_text("{broken", encoding="utf-8")
    store = MemoryStore(tmp_path)

    assert await store.load_profile() == TasteProfile()


@pytest.mark.asyncio
async def test_damaged_json_is_logged_without_raw_file_content(tmp_path, caplog):
    (tmp_path / "taste-profile.json").write_text('{"likedIngredients":["secret beef"', encoding="utf-8")
    store = MemoryStore(tmp_path, logger=logging.getLogger("tests.memory_store"))

    with caplog.at_level(logging.WARNING, logger="tests.memory_store"):
        assert await store.load_profile() == TasteProfile()

    assert "memory_store_read_failed" in caplog.text
    assert "secret beef" not in caplog.text


@pytest.mark.asyncio
async def test_save_all_trims_history_and_writes_json(tmp_path):
    store = MemoryStore(tmp_path)
    history = [
        RecommendationRecord(
            itemType="meal",
            itemId=str(index),
            title=f"Meal {index}",
            recommendedAt="2026-06-14T00:00:00Z",
            mainIngredients=["beef"],
            matchReasons=[],
        )
        for index in range(25)
    ]

    warnings = await store.save_all(TasteProfile(likedIngredients=["chicken"]), history, AgentMemory())
    saved_history = await store.load_history()

    assert warnings == []
    assert len(saved_history) == 20
    assert saved_history[0].itemId == "5"
    assert (tmp_path / "taste-profile.json").exists()


@pytest.mark.asyncio
async def test_save_all_returns_warning_when_atomic_write_fails(tmp_path, monkeypatch):
    store = MemoryStore(tmp_path)

    def fail_replace(self: Path, target: Path):
        raise OSError("disk full")

    monkeypatch.setattr(Path, "replace", fail_replace)
    warnings = await store.save_all(TasteProfile(), [], AgentMemory())

    assert warnings
    assert "持久化失败" in warnings[0]


@pytest.mark.asyncio
async def test_save_all_logs_write_failure(tmp_path, monkeypatch, caplog):
    store = MemoryStore(tmp_path, logger=logging.getLogger("tests.memory_store.write"))

    def fail_replace(self: Path, target: Path):
        raise OSError("disk full")

    monkeypatch.setattr(Path, "replace", fail_replace)
    with caplog.at_level(logging.ERROR, logger="tests.memory_store.write"):
        warnings = await store.save_all(TasteProfile(), [], AgentMemory())

    assert warnings
    assert "memory_store_write_failed" in caplog.text
    assert "disk full" in caplog.text
