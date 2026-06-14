from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.errors import error_response
from app.core.sse import format_sse
from app.services.conversation_lock import ConversationBusyError

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatStreamRequest(BaseModel):
    message: str


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
        try:
            async for event in request.app.state.agent.run(message):
                yield format_sse(event.event, event.data)
        except Exception as exc:
            yield format_sse("error", {"code": "CHAT_RUNTIME_ERROR", "message": str(exc)})
        finally:
            await lock_context.__aexit__(None, None, None)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
