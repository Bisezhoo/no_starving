import json

import pytest

from app.services.openrouter_client import OpenRouterStepLlm


class FakeStreamClient:
    def __init__(self, lines):
        self.lines = lines
        self.messages = []
        self.tools = []

    async def stream_chat(self, messages, tools):
        self.messages = messages
        self.tools = tools
        for line in self.lines:
            yield line


@pytest.mark.asyncio
async def test_openrouter_step_parses_streamed_content_and_tool_calls():
    lines = [
        "data: " + json.dumps({"choices": [{"delta": {"content": "先查一下"}}]}),
        "data: "
        + json.dumps(
            {
                "choices": [
                    {
                        "delta": {
                            "tool_calls": [
                                {
                                    "index": 0,
                                    "id": "call_1",
                                    "function": {"name": "search_meals", "arguments": '{"ingre'},
                                }
                            ]
                        }
                    }
                ]
            }
        ),
        "data: "
        + json.dumps(
            {
                "choices": [
                    {
                        "delta": {
                            "tool_calls": [
                                {
                                    "index": 0,
                                    "function": {"arguments": 'dient":"chicken"}'},
                                }
                            ]
                        }
                    }
                ]
            }
        ),
        "data: [DONE]",
    ]
    client = FakeStreamClient(lines)
    llm = OpenRouterStepLlm(client=client, tools=[{"type": "function", "function": {"name": "search_meals"}}])

    step = await llm.next({"message": "我想吃鸡肉", "tool_results": []})

    assert step["delta"] == "先查一下"
    assert step["reply"] == "先查一下"
    assert step["tool_calls"] == [
        {"id": "call_1", "name": "search_meals", "arguments": {"ingredient": "chicken"}}
    ]
    assert client.tools[0]["function"]["name"] == "search_meals"


@pytest.mark.asyncio
async def test_openrouter_step_streams_delta_before_final_step():
    lines = [
        "data: " + json.dumps({"choices": [{"delta": {"content": "你"}}]}),
        "data: " + json.dumps({"choices": [{"delta": {"content": "好"}}]}),
        "data: [DONE]",
    ]
    llm = OpenRouterStepLlm(client=FakeStreamClient(lines), tools=[])

    events = [event async for event in llm.stream_step({"message": "hi", "tool_results": []})]

    assert events[:2] == [{"type": "delta", "text": "你"}, {"type": "delta", "text": "好"}]
    assert events[-1] == {"type": "step", "step": {"reply": "你好", "tool_calls": []}}


@pytest.mark.asyncio
async def test_openrouter_step_marks_unparseable_tool_arguments():
    lines = [
        "data: "
        + json.dumps(
            {
                "choices": [
                    {
                        "delta": {
                            "tool_calls": [
                                {
                                    "index": 0,
                                    "id": "call_1",
                                    "function": {"name": "search_meals", "arguments": "{bad"},
                                }
                            ]
                        }
                    }
                ]
            }
        ),
        "data: [DONE]",
    ]
    llm = OpenRouterStepLlm(client=FakeStreamClient(lines), tools=[])

    step = await llm.next({"message": "推荐鸡肉", "tool_results": []})

    assert step["tool_calls"][0]["arguments"] == {"__invalid_json__": "{bad"}


@pytest.mark.asyncio
async def test_openrouter_messages_include_locale_instruction_after_tool_results():
    lines = ["data: [DONE]"]
    client = FakeStreamClient(lines)
    llm = OpenRouterStepLlm(client=client, tools=[])

    events = [
        event
        async for event in llm.stream_step(
            {
                "message": "我想吃鸡肉",
                "detectedLocale": "zh-CN",
                "tool_results": [{"name": "search_meals", "status": "success", "resultCount": 1}],
            }
        )
    ]

    assert events[-1]["type"] == "step"
    assert "Output locale: zh-CN" in client.messages[0]["content"]
    assert "Final reply must use zh-CN" in client.messages[-1]["content"]
