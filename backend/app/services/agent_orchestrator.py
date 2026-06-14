import json
from typing import Any, AsyncIterator

from app.domain.models import SseEvent


class AgentOrchestrator:
    def __init__(self, llm: Any, tool_runner: Any, max_tool_calls: int = 6, max_llm_steps: int = 4):
        self.llm = llm
        self.tool_runner = tool_runner
        self.max_tool_calls = max_tool_calls
        self.max_llm_steps = max_llm_steps

    async def run(self, message: str) -> AsyncIterator[SseEvent]:
        request_id = "req_local"
        warnings: list[str] = []
        context: dict[str, Any] = {"message": message, "tool_results": []}
        result_cache: dict[tuple[str, str], Any] = {}
        tool_call_count = 0
        llm_step_count = 0

        yield SseEvent(event="meta", data={"requestId": request_id})

        while llm_step_count < self.max_llm_steps:
            step = await self.llm.next(context)
            llm_step_count += 1

            if text := step.get("delta"):
                yield SseEvent(event="delta", data={"text": text})

            tool_calls = step.get("tool_calls") or []
            if not tool_calls:
                yield SseEvent(event="done", data={"reply": step.get("reply", ""), "cards": [], "toolCalls": context["tool_results"], "warnings": warnings})
                return

            for call in tool_calls:
                if tool_call_count >= self.max_tool_calls:
                    warnings.append("已达 Tool 调用上限")
                    yield SseEvent(event="done", data={"reply": "", "cards": [], "toolCalls": context["tool_results"], "warnings": warnings})
                    return

                tool_name = call["name"]
                arguments = call.get("arguments", {})
                call_id = call.get("id", f"tool_call_{tool_call_count + 1}")
                cache_key = (tool_name, _args_hash(arguments))

                yield SseEvent(event="tool_call", data={"id": call_id, "name": tool_name, "arguments": arguments, "status": "started"})

                if cache_key in result_cache:
                    cached_result = result_cache[cache_key]
                    tool_call_count += 1
                    data = {
                        "id": call_id,
                        "name": tool_name,
                        "status": "cached",
                        "durationMs": 0,
                        "resultCount": getattr(cached_result, "resultCount", 0),
                    }
                    context["tool_results"].append(data)
                    yield SseEvent(event="tool_result", data=data)
                    continue

                result = await self.tool_runner.run(tool_name, arguments, request_id, retry_of=call.get("retryOf"))
                tool_call_count += 1
                result_cache[cache_key] = result
                data = _tool_result_data(result, call_id, tool_name)
                context["tool_results"].append(data)
                yield SseEvent(event="tool_result", data=data)

        warnings.append("已达 LLM 推理步数上限")
        yield SseEvent(event="done", data={"reply": "", "cards": [], "toolCalls": context["tool_results"], "warnings": warnings})


def _args_hash(arguments: dict[str, Any]) -> str:
    return json.dumps(arguments, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _tool_result_data(result: Any, call_id: str, tool_name: str) -> dict[str, Any]:
    data = {
        "id": getattr(result, "id", call_id),
        "name": getattr(result, "name", tool_name),
        "status": getattr(result, "status", "failed"),
        "durationMs": getattr(result, "durationMs", 0),
        "resultCount": getattr(result, "resultCount", 0),
    }
    if error := getattr(result, "error", None):
        data["error"] = error
    if validation_error := getattr(result, "validationError", None):
        data["validationError"] = validation_error
    return data
