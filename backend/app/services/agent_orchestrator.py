import json
from datetime import UTC, datetime
from typing import Any, AsyncIterator
from uuid import uuid4

from app.domain.card_localization import localize_cards, should_localize_instructions
from app.domain.language import detect_locale
from app.domain.models import AgentMemory, AgentMemoryCandidate, Card, SseEvent, ToolCallSummary
from app.domain.recommendation import append_history, rank_recommendations
from app.domain.taste_profile import merge_profile_from_message
from app.services.conversation_state import ConversationState


class AgentOrchestrator:
    def __init__(
        self,
        llm: Any,
        tool_runner: Any,
        memory_store: Any | None = None,
        max_tool_calls: int = 6,
        max_llm_steps: int = 4,
    ):
        self.llm = llm
        self.tool_runner = tool_runner
        self.memory_store = memory_store
        self.max_tool_calls = max_tool_calls
        self.max_llm_steps = max_llm_steps

    async def run(self, message: str) -> AsyncIterator[SseEvent]:
        request_id = f"req_{uuid4().hex[:12]}"
        detected_locale = detect_locale(message)
        warnings: list[str] = []
        state = await self._load_state()
        profile, profile_patch = merge_profile_from_message(state.profile, message)
        history = list(state.history)
        memory = state.memory
        displayed_cards: list[Card] = []
        tool_summaries: list[dict[str, Any]] = []
        include_localized_instructions = should_localize_instructions(message)
        context: dict[str, Any] = {
            "message": message,
            "detectedLocale": detected_locale,
            "profile": profile.model_dump(mode="json"),
            "memory": memory.model_dump(mode="json"),
            "tool_results": [],
        }
        result_cache: dict[tuple[str, str], Any] = {}
        tool_call_count = 0
        llm_step_count = 0

        yield SseEvent(event="meta", data={"requestId": request_id, "detectedLocale": detected_locale})
        if profile_patch:
            yield SseEvent(event="profile_update", data={"patch": profile_patch, "reason": "user_message"})

        while llm_step_count < self.max_llm_steps:
            if hasattr(self.llm, "stream_step"):
                step = None
                async for llm_event in self.llm.stream_step(context):
                    if llm_event["type"] == "delta":
                        yield SseEvent(event="delta", data={"text": llm_event["text"]})
                    elif llm_event["type"] == "step":
                        step = llm_event["step"]
                step = step or {"reply": "", "tool_calls": []}
            else:
                step = await self.llm.next(context)
                if text := step.get("delta"):
                    yield SseEvent(event="delta", data={"text": text})
            llm_step_count += 1

            tool_calls = step.get("tool_calls") or []
            if not tool_calls:
                yield await self._build_done_event(
                    reply=step.get("reply", ""),
                    cards=displayed_cards,
                    tool_summaries=tool_summaries,
                    warnings=warnings,
                    profile=profile,
                    history=history,
                    memory=memory,
                    message=message,
                    detected_locale=detected_locale,
                )
                return

            for call in tool_calls:
                if tool_call_count >= self.max_tool_calls:
                    warnings.append("已达 Tool 调用上限")
                    yield await self._build_done_event(
                        reply="",
                        cards=displayed_cards,
                        tool_summaries=tool_summaries,
                        warnings=warnings,
                        profile=profile,
                        history=history,
                        memory=memory,
                        message=message,
                        detected_locale=detected_locale,
                    )
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
                        "arguments": arguments,
                        "durationMs": 0,
                        "resultCount": getattr(cached_result, "resultCount", 0),
                    }
                    if cached_cards := getattr(cached_result, "cards", []):
                        data["cards"] = _dump_cards(cached_cards)
                    context["tool_results"].append(data)
                    tool_summaries.append(data)
                    yield SseEvent(event="tool_result", data=data)
                    ranked_cards = _rank_new_cards(cached_cards, profile, history, displayed_cards)
                    if ranked_cards:
                        displayed_cards.extend(localize_cards(ranked_cards, detected_locale, include_localized_instructions))
                        yield SseEvent(event="card", data={"cards": _dump_cards(displayed_cards)})
                    continue

                result = await self.tool_runner.run(tool_name, arguments, request_id, retry_of=call.get("retryOf"))
                tool_call_count += 1
                result_cache[cache_key] = result
                data = _tool_result_data(result, call_id, tool_name, arguments)
                context["tool_results"].append(data)
                tool_summaries.append(data)
                yield SseEvent(event="tool_result", data=data)
                ranked_cards = _rank_new_cards(getattr(result, "cards", []), profile, history, displayed_cards)
                if ranked_cards:
                    displayed_cards.extend(localize_cards(ranked_cards, detected_locale, include_localized_instructions))
                    yield SseEvent(event="card", data={"cards": _dump_cards(displayed_cards)})

        warnings.append("已达 LLM 推理步数上限")
        yield await self._build_done_event(
            reply="",
            cards=displayed_cards,
            tool_summaries=tool_summaries,
            warnings=warnings,
            profile=profile,
            history=history,
            memory=memory,
            message=message,
            detected_locale=detected_locale,
        )

    async def _load_state(self) -> ConversationState:
        if self.memory_store is None:
            return ConversationState()
        return ConversationState(
            profile=await self.memory_store.load_profile(),
            history=await self.memory_store.load_history(),
            memory=await self.memory_store.load_agent_memory(),
        )

    async def _build_done_event(
        self,
        reply: str,
        cards: list[Card],
        tool_summaries: list[dict[str, Any]],
        warnings: list[str],
        profile: Any,
        history: Any,
        memory: AgentMemory,
        message: str,
        detected_locale: str,
    ) -> SseEvent:
        persist_warnings = await self._persist_state(profile, history, memory, message, reply, cards, tool_summaries)
        return SseEvent(
            event="done",
            data={
                "reply": reply,
                "cards": _dump_cards(cards),
                "toolCalls": tool_summaries,
                "warnings": warnings + persist_warnings,
                "detectedLocale": detected_locale,
            },
        )

    async def _persist_state(
        self,
        profile: Any,
        history: Any,
        memory: AgentMemory,
        message: str,
        reply: str,
        cards: list[Card],
        tool_summaries: list[dict[str, Any]],
    ) -> list[str]:
        if self.memory_store is None:
            return []
        updated_history = append_history(history, cards)
        updated_memory = _update_memory(memory, message, reply, cards, tool_summaries)
        return await self.memory_store.save_all(profile, updated_history, updated_memory)


def _args_hash(arguments: dict[str, Any]) -> str:
    return json.dumps(arguments, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _tool_result_data(result: Any, call_id: str, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    data = {
        "id": getattr(result, "id", call_id),
        "name": getattr(result, "name", tool_name),
        "status": getattr(result, "status", "failed"),
        "arguments": getattr(result, "arguments", arguments),
        "durationMs": getattr(result, "durationMs", 0),
        "resultCount": getattr(result, "resultCount", 0),
    }
    if cards := getattr(result, "cards", []):
        data["cards"] = _dump_cards(cards)
    if error := getattr(result, "error", None):
        data["error"] = error
    if validation_error := getattr(result, "validationError", None):
        data["validationError"] = validation_error
    return data


def _rank_new_cards(cards: list[Card], profile: Any, history: Any, displayed_cards: list[Card]) -> list[Card]:
    if not cards:
        return []
    ranked_cards, explanation = rank_recommendations(cards, profile, history)
    displayed_ids = {card.id for card in displayed_cards}
    new_cards = [card for card in ranked_cards if card.id not in displayed_ids]
    if explanation.reasons:
        for card in new_cards:
            card.matchReasons = explanation.reasons
    return new_cards


def _dump_cards(cards: list[Card]) -> list[dict[str, Any]]:
    return [card.model_dump(mode="json") for card in cards]


def _update_memory(
    memory: AgentMemory,
    message: str,
    reply: str,
    cards: list[Card],
    tool_summaries: list[dict[str, Any]],
) -> AgentMemory:
    now = datetime.now(UTC).isoformat()
    updated = memory.model_copy(deep=True)
    updated.updatedAt = now
    updated.conversationSummary = _conversation_summary(cards, tool_summaries)
    recent_turns = list(updated.recentTurns)
    recent_turns.append({"role": "user", "content": _summarize_user_message(message), "createdAt": now})
    if reply:
        recent_turns.append({"role": "assistant", "content": _truncate(reply, 240), "createdAt": now})
    updated.recentTurns = recent_turns[-20:]
    updated.activeCandidates = [
        AgentMemoryCandidate(
            type=card.type,
            id=card.id,
            title=card.title,
            rank=index + 1,
            detailLevel=card.detailLevel,
            mainIngredients=[ingredient.name for ingredient in card.ingredients[:5]],
            category=getattr(card, "category", None),
            cuisine=getattr(card, "country", None),
        )
        for index, card in enumerate(cards[:10])
    ]
    updated.lastToolCalls = [ToolCallSummary.model_validate(summary) for summary in tool_summaries[-6:]]
    updated.lastIntent = "recipe_or_drink_recommendation" if tool_summaries or cards else "conversation"
    return updated


def _conversation_summary(cards: list[Card], tool_summaries: list[dict[str, Any]]) -> str:
    if cards:
        titles = "、".join(card.title for card in cards[:3])
        return f"最近一次推荐了 {len(cards)} 个候选：{titles}"
    if tool_summaries:
        return "最近一次请求调用了工具，但没有形成可展示候选"
    return "最近一次请求未调用工具"


def _summarize_user_message(message: str) -> str:
    if "不喝酒" in message or "不要酒精" in message or "无酒精" in message:
        return "用户表达了无酒精偏好"
    if "喜欢" in message or "想吃" in message:
        return "用户表达了食材或口味偏好"
    return "用户发起了一次推荐或问答请求"


def _truncate(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[:limit]
