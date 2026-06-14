import json
import logging

import pytest

from app.core.config import Settings
from app.domain.models import AgentMemory, IngredientItem, MealCard, TasteProfile, ToolDataResult
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.card_translation_service import CardTranslationResult


class RepeatingToolLlm:
    async def next(self, context):
        return {
            "tool_calls": [
                {"id": f"call_{len(context['tool_results']) + 1}", "name": "search_meals", "arguments": {"ingredient": "chicken"}}
            ]
        }


class SameToolTwiceLlm:
    def __init__(self):
        self.calls = 0

    async def next(self, context):
        self.calls += 1
        if self.calls <= 2:
            return {"tool_calls": [{"id": f"call_{self.calls}", "name": "search_meals", "arguments": {"ingredient": "chicken"}}]}
        return {"reply": "done"}


class FakeToolRunner:
    def __init__(self):
        self.call_count = 0
        self.external_call_count = 0

    async def run(self, name, arguments, request_id, retry_of=None):
        self.call_count += 1
        self.external_call_count += 1
        return ToolDataResult(status="success", cards=[], resultCount=0)


class OneToolThenReplyLlm:
    def __init__(self):
        self.calls = 0

    async def next(self, context):
        assert context["detectedLocale"] == "zh-CN"
        self.calls += 1
        if self.calls == 1:
            return {"tool_calls": [{"id": "call_1", "name": "search_meals", "arguments": {"ingredient": "chicken"}}]}
        assert context["tool_results"][0]["resultCount"] == 1
        return {"reply": "推荐鸡肉饭", "delta": "推荐鸡肉饭"}


class CardToolRunner:
    async def run(self, name, arguments, request_id, retry_of=None):
        card = MealCard(
            id="meal_1",
            detailLevel="detail",
            title="Chicken Rice",
            imageUrl="https://img.example/chicken-rice.jpg",
            category="Chicken",
            country="Japanese",
            ingredients=[{"name": "chicken"}, {"name": "rice"}],
            instructions=["Cook chicken with rice until tender."],
        )
        return ToolDataResult(status="success", cards=[card], resultCount=1)


class FakeMemoryStore:
    def __init__(self):
        self.saved_profile = None
        self.saved_history = None
        self.saved_memory = None

    async def load_profile(self):
        return TasteProfile()

    async def load_history(self):
        return []

    async def load_agent_memory(self):
        return AgentMemory()

    async def save_all(self, profile, history, memory):
        self.saved_profile = profile
        self.saved_history = history
        self.saved_memory = memory
        return []


class FakeCardTranslationService:
    def __init__(self):
        self.calls = []

    async def localize_cards(self, cards, locale, include_instructions=False):
        self.calls.append({"cards": cards, "locale": locale, "include_instructions": include_instructions})
        localized = [card.model_copy(deep=True) for card in cards]
        localized[0].localizedLanguage = locale
        localized[0].localizedTitle = "鸡肉饭"
        localized[0].localizedIngredients = [IngredientItem(name="鸡肉"), IngredientItem(name="米饭")]
        return CardTranslationResult(cards=localized, warnings=["部分卡片翻译未通过校验，已保留原始内容"])


@pytest.mark.asyncio
async def test_max_tool_calls_stops_loop_and_returns_warning():
    fake_tool_runner = FakeToolRunner()
    agent = AgentOrchestrator(
        llm=RepeatingToolLlm(),
        tool_runner=fake_tool_runner,
        max_tool_calls=1,
        max_llm_steps=4,
    )

    events = [event async for event in agent.run("我想吃鸡肉")]
    done = [event for event in events if event.event == "done"][-1]

    assert "已达 Tool 调用上限，请重试哦" in done.data["warnings"][0]
    assert fake_tool_runner.call_count == 1


@pytest.mark.asyncio
async def test_same_tool_same_args_returns_cached_result():
    fake_tool_runner = FakeToolRunner()
    agent = AgentOrchestrator(
        llm=SameToolTwiceLlm(),
        tool_runner=fake_tool_runner,
        max_tool_calls=6,
        max_llm_steps=4,
    )

    events = [event async for event in agent.run("我想吃鸡肉")]
    cached = [event for event in events if event.event == "tool_result" and event.data["status"] == "cached"]

    assert len(cached) == 1
    assert fake_tool_runner.external_call_count == 1


@pytest.mark.asyncio
async def test_agent_emits_cards_and_persists_memory_after_tool_result():
    memory_store = FakeMemoryStore()
    agent = AgentOrchestrator(
        llm=OneToolThenReplyLlm(),
        tool_runner=CardToolRunner(),
        memory_store=memory_store,
        max_tool_calls=6,
        max_llm_steps=4,
    )

    events = [event async for event in agent.run("我喜欢鸡肉")]
    card_events = [event for event in events if event.event == "card"]
    profile_events = [event for event in events if event.event == "profile_update"]
    done = [event for event in events if event.event == "done"][-1]

    assert card_events[0].data["cards"][0]["id"] == "meal_1"
    assert card_events[0].data["cards"][0]["localizedLanguage"] == "zh-CN"
    assert "Chicken Rice" in card_events[0].data["cards"][0]["localizedSummary"]
    assert "localizedInstructions" not in card_events[0].data["cards"][0] or card_events[0].data["cards"][0]["localizedInstructions"] is None
    assert profile_events[0].data["patch"] == {"likedIngredients": ["chicken"]}
    assert done.data["cards"][0]["id"] == "meal_1"
    assert done.data["cards"][0]["localizedLanguage"] == "zh-CN"
    assert memory_store.saved_history[0].itemId == "meal_1"
    assert memory_store.saved_memory.recentTurns[-2]["role"] == "user"
    assert memory_store.saved_memory.recentTurns[-2]["content"] != "我喜欢鸡肉"


@pytest.mark.asyncio
async def test_agent_uses_card_translation_service_before_emitting_cards():
    translation_service = FakeCardTranslationService()
    agent = AgentOrchestrator(
        llm=OneToolThenReplyLlm(),
        tool_runner=CardToolRunner(),
        card_translation_service=translation_service,
        max_tool_calls=6,
        max_llm_steps=4,
    )

    events = [event async for event in agent.run("我喜欢鸡肉")]
    card_event = [event for event in events if event.event == "card"][0]
    done = [event for event in events if event.event == "done"][-1]

    assert translation_service.calls[0]["locale"] == "zh-CN"
    assert translation_service.calls[0]["include_instructions"] is False
    assert card_event.data["cards"][0]["localizedTitle"] == "鸡肉饭"
    assert card_event.data["cards"][0]["localizedIngredients"][0]["name"] == "鸡肉"
    assert done.data["cards"][0]["localizedTitle"] == "鸡肉饭"
    assert done.data["warnings"] == ["部分卡片翻译未通过校验，已保留原始内容"]


@pytest.mark.asyncio
async def test_agent_localizes_detail_instructions_when_user_asks_how_to_make_it():
    agent = AgentOrchestrator(
        llm=OneToolThenReplyLlm(),
        tool_runner=CardToolRunner(),
        max_tool_calls=6,
        max_llm_steps=4,
    )

    events = [event async for event in agent.run("第一个怎么做")]
    done = [event for event in events if event.event == "done"][-1]

    assert done.data["cards"][0]["localizedLanguage"] == "zh-CN"
    assert done.data["cards"][0]["localizedInstructions"][0].startswith("步骤 1：")
    assert "Cook chicken with rice" in done.data["cards"][0]["localizedInstructions"][0]


@pytest.mark.asyncio
async def test_agent_logs_start_and_finish_without_full_user_message(caplog):
    settings = Settings(
        openrouter_api_key="sk-test",
        openrouter_model="deepseek/deepseek-chat",
        log_full_user_message=False,
    )
    logger = logging.getLogger("tests.agent_orchestrator")
    agent = AgentOrchestrator(
        llm=OneToolThenReplyLlm(),
        tool_runner=CardToolRunner(),
        memory_store=FakeMemoryStore(),
        settings=settings,
        logger=logger,
        max_tool_calls=6,
        max_llm_steps=4,
    )

    with caplog.at_level(logging.INFO, logger=logger.name):
        events = [event async for event in agent.run("我喜欢鸡肉")]

    assert [event.event for event in events][-1] == "done"
    payloads = [json.loads(record.message) for record in caplog.records]
    assert payloads[0]["event"] == "agent_request_started"
    assert payloads[0]["userMessage"] == {"present": True, "length": 5}
    assert payloads[-1]["event"] == "agent_request_finished"
    assert payloads[-1]["cardCount"] == 1
    assert payloads[-1]["toolCallCount"] == 1
    assert "我喜欢鸡肉" not in caplog.text
