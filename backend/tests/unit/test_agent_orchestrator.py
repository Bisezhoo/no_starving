import pytest

from app.domain.models import AgentMemory, MealCard, TasteProfile, ToolDataResult
from app.services.agent_orchestrator import AgentOrchestrator


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

    assert "已达 Tool 调用上限" in done.data["warnings"][0]
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
    assert profile_events[0].data["patch"] == {"likedIngredients": ["chicken"]}
    assert done.data["cards"][0]["id"] == "meal_1"
    assert memory_store.saved_history[0].itemId == "meal_1"
    assert memory_store.saved_memory.recentTurns[-2]["role"] == "user"
    assert memory_store.saved_memory.recentTurns[-2]["content"] != "我喜欢鸡肉"
