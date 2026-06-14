import pytest

from app.domain.models import ToolDataResult
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
