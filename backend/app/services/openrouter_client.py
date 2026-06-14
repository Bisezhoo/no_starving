import json
from typing import Any, AsyncIterator

import httpx


class OpenRouterClient:
    def __init__(self, api_key: str, model: str, base_url: str, timeout_seconds: float = 30):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout_seconds = timeout_seconds

    async def stream_chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> AsyncIterator[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "stream": True,
        }
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds, trust_env=False) as client:
            async with client.stream("POST", "chat/completions", headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        yield line


class OpenRouterStepLlm:
    def __init__(self, client: OpenRouterClient, tools: list[dict[str, Any]]):
        self.client = client
        self.tools = tools

    async def next(self, context: dict[str, Any]) -> dict[str, Any]:
        content_parts: list[str] = []
        final_step: dict[str, Any] | None = None
        async for event in self.stream_step(context):
            if event["type"] == "delta":
                content_parts.append(event["text"])
            elif event["type"] == "step":
                final_step = event["step"]
        if final_step is None:
            reply = "".join(content_parts)
            return {"delta": reply, "reply": reply, "tool_calls": []}
        final_step["delta"] = "".join(content_parts)
        return final_step

    async def stream_step(self, context: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        content_parts: list[str] = []
        tool_call_deltas: dict[int, dict[str, str]] = {}

        async for line in self.client.stream_chat(_build_messages(context), self.tools):
            payload = _parse_stream_payload(line)
            if payload is None:
                continue
            for choice in payload.get("choices", []):
                delta = choice.get("delta") or {}
                if content := delta.get("content"):
                    text = str(content)
                    content_parts.append(text)
                    yield {"type": "delta", "text": text}
                for tool_call_delta in delta.get("tool_calls") or []:
                    _merge_tool_call_delta(tool_call_deltas, tool_call_delta)

        reply = "".join(content_parts)
        yield {"type": "step", "step": {"reply": reply, "tool_calls": _finalize_tool_calls(tool_call_deltas)}}


def _build_messages(context: dict[str, Any]) -> list[dict[str, str]]:
    system_prompt = (
        "You are a recipe assistant. Reply in the user's language. "
        "Use tools for recipe or drink lookup. Tool query and ingredient arguments must be English. "
        "Do not invent meal or drink IDs; IDs must come from tool results or candidate cards."
    )
    profile = context.get("profile")
    memory = context.get("memory")
    if profile or memory:
        system_prompt += "\nCurrent lightweight profile and memory:\n"
        system_prompt += json.dumps({"profile": profile, "memory": memory}, ensure_ascii=False, separators=(",", ":"))

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": str(context.get("message") or "")},
    ]
    if tool_results := context.get("tool_results"):
        messages.append(
            {
                "role": "user",
                "content": (
                    "Tool results are available as JSON. Use only these results for concrete recipe/drink facts:\n"
                    + json.dumps(tool_results, ensure_ascii=False, separators=(",", ":"))
                ),
            }
        )
    return messages


def _parse_stream_payload(line: str) -> dict[str, Any] | None:
    data = line.strip()
    if not data or data.startswith(":"):
        return None
    if data.startswith("data:"):
        data = data[5:].strip()
    if data == "[DONE]":
        return None
    try:
        payload = json.loads(data)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _merge_tool_call_delta(tool_calls: dict[int, dict[str, str]], delta: dict[str, Any]) -> None:
    index = int(delta.get("index", len(tool_calls)))
    item = tool_calls.setdefault(index, {"id": "", "name": "", "arguments": ""})
    if tool_call_id := delta.get("id"):
        item["id"] = str(tool_call_id)
    function_delta = delta.get("function") or {}
    if name := function_delta.get("name"):
        item["name"] += str(name)
    if arguments := function_delta.get("arguments"):
        item["arguments"] += str(arguments)


def _finalize_tool_calls(tool_call_deltas: dict[int, dict[str, str]]) -> list[dict[str, Any]]:
    tool_calls: list[dict[str, Any]] = []
    for index in sorted(tool_call_deltas):
        item = tool_call_deltas[index]
        name = item["name"].strip()
        if not name:
            continue
        raw_arguments = item["arguments"].strip()
        try:
            arguments = json.loads(raw_arguments) if raw_arguments else {}
        except json.JSONDecodeError:
            arguments = {"__invalid_json__": raw_arguments}
        if not isinstance(arguments, dict):
            arguments = {"__invalid_json__": raw_arguments}
        tool_calls.append(
            {
                "id": item["id"] or f"call_{index + 1}",
                "name": name,
                "arguments": arguments,
            }
        )
    return tool_calls
