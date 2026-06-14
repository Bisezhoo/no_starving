import json
import logging
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, AsyncIterator

import httpx

from app.core.logging import get_logger, log_event

_PROMPTS_PATH = Path(__file__).resolve().parents[1] / "core" / "prompts.json"


@lru_cache(maxsize=1)
def _load_prompts() -> dict[str, str]:
    return json.loads(_PROMPTS_PATH.read_text(encoding="utf-8"))


class OpenRouterClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        timeout_seconds: float = 30,
        proxy: str | None = None,
        trust_env: bool = True,
        settings: Any | None = None,
        logger: logging.Logger | None = None,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout_seconds = timeout_seconds
        self.proxy = proxy
        self.trust_env = trust_env
        self.settings = settings
        self.logger = logger or get_logger(__name__)

    async def stream_chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> AsyncIterator[str]:
        started = time.perf_counter()
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
        log_event(
            self.logger,
            "openrouter_request_started",
            settings=self.settings,
            fields={
                "model": self.model,
                "baseUrl": self.base_url,
                "messageCount": len(messages),
                "toolCount": len(tools),
                "headers": headers,
            },
        )
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            proxy=self.proxy,
            trust_env=self.trust_env,
        ) as client:
            try:
                async with client.stream("POST", "chat/completions", headers=headers, json=payload) as response:
                    response.raise_for_status()
                    log_event(
                        self.logger,
                        "openrouter_request_finished",
                        settings=self.settings,
                        fields={
                            "model": self.model,
                            "statusCode": getattr(response, "status_code", None),
                            "durationMs": _duration_ms(started),
                        },
                    )
                    async for line in response.aiter_lines():
                        if line:
                            yield line
            except Exception as exc:
                log_event(
                    self.logger,
                    "openrouter_request_failed",
                    settings=self.settings,
                    fields={"model": self.model, "errorType": type(exc).__name__, "error": str(exc), "durationMs": _duration_ms(started)},
                    level=logging.ERROR,
                    exc_info=bool(getattr(self.settings, "log_stack_trace", False)),
                )
                raise


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
    prompts = _load_prompts()
    system_prompt = prompts["system_prompt"]
    detected_locale = str(context.get("detectedLocale") or "").strip()
    if detected_locale:
        system_prompt += f"\nOutput locale: {detected_locale}. Use this locale for every natural-language reply, explanation, warning, and follow-up question."
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
        locale_instruction = ""
        if detected_locale:
            locale_instruction = (
                f"Output locale: {detected_locale}\n"
                f"Final reply must use {detected_locale}. Explain tool results, empty results, validation failures, and next steps in this locale.\n"
            )
        messages.append(
            {
                "role": "user",
                "content": (
                    locale_instruction
                    + prompts["tool_results_prefix"] + "\n"
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


def _duration_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)
