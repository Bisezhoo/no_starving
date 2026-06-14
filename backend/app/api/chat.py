from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.errors import error_response
from app.core.sse import format_sse
from app.domain.models import AssistantChatHistoryMessage, UserChatHistoryMessage
from app.services.conversation_lock import ConversationBusyError

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatStreamRequest(BaseModel):
    message: str


@router.get("/history")
async def chat_history(request: Request):
    messages = await request.app.state.chat_history_store.load_messages()
    return {
        "code": 200,
        "message": "success",
        "data": {"messages": [message.model_dump(mode="json") for message in messages]},
    }


@router.post("/stream")
async def chat_stream(payload: ChatStreamRequest, request: Request):
    message = payload.message.strip()
    if not message:
        return error_response(400, "message 不能为空")
    if len(message) > 1000:
        return error_response(400, "message 长度不能超过 1000")

    lock_context = request.app.state.conversation_lock.acquire("req_http")
    try:
        await lock_context.__aenter__()
    except ConversationBusyError:
        return error_response(409, "当前已有请求处理中，请稍后再试")

    async def event_stream():
        done_data: dict[str, Any] | None = None
        error_data: dict[str, Any] | None = None
        profile_updates: list[dict[str, Any]] = []
        try:
            async for event in request.app.state.agent.run(message):
                if event.event == "done":
                    done_data = event.data
                elif event.event == "error":
                    error_data = event.data
                elif event.event == "profile_update":
                    profile_updates.append(event.data)
                yield format_sse(event.event, event.data)
        except Exception as exc:
            error_data = {"code": "CHAT_RUNTIME_ERROR", "message": str(exc)}
            yield format_sse("error", error_data)
        finally:
            if done_data is not None or error_data is not None:
                await _save_chat_history(request, message, done_data, error_data, profile_updates)
            await lock_context.__aexit__(None, None, None)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


async def _save_chat_history(
    request: Request,
    user_message: str,
    done_data: dict[str, Any] | None,
    error_data: dict[str, Any] | None,
    profile_updates: list[dict[str, Any]],
) -> None:
    created_at = datetime.now(UTC).isoformat()
    assistant = _build_assistant_history_message(done_data, error_data, profile_updates, created_at)
    messages = [
        UserChatHistoryMessage(role="user", content=user_message, createdAt=created_at),
        assistant,
    ]
    try:
        await request.app.state.chat_history_store.append_messages(messages)
    except Exception:
        return


def _build_assistant_history_message(
    done_data: dict[str, Any] | None,
    error_data: dict[str, Any] | None,
    profile_updates: list[dict[str, Any]],
    created_at: str,
) -> AssistantChatHistoryMessage:
    if done_data is None:
        return AssistantChatHistoryMessage(
            role="assistant",
            reply="",
            cards=[],
            toolCalls=[],
            warnings=[],
            profileUpdates=profile_updates,
            error=str((error_data or {}).get("message") or "请求失败"),
            createdAt=created_at,
        )
    return AssistantChatHistoryMessage(
        role="assistant",
        reply=str(done_data.get("reply") or ""),
        cards=list(done_data.get("cards") or []),
        toolCalls=list(done_data.get("toolCalls") or []),
        warnings=list(done_data.get("warnings") or []),
        profileUpdates=profile_updates,
        error=str(error_data.get("message")) if error_data and error_data.get("message") else None,
        createdAt=created_at,
    )
