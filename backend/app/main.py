from pathlib import Path

from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.core.config import Settings
from app.domain.models import SseEvent
from app.services.conversation_lock import ConversationLock
from app.services.default_agent import build_default_agent


def create_app(agent=None, settings: Settings | None = None, data_dir: Path | str | None = None) -> FastAPI:
    app = FastAPI(title="No Starving Recipe Assistant")
    app.state.startup_error = None
    app.state.settings = settings
    if agent is None:
        try:
            app.state.settings = settings or Settings()
            app.state.agent = build_default_agent(app.state.settings, data_dir=data_dir)
        except Exception as exc:
            app.state.startup_error = str(exc)
            app.state.agent = UnavailableAgent()
    else:
        app.state.agent = agent
    app.state.conversation_lock = ConversationLock()
    app.include_router(health_router)
    app.include_router(chat_router)
    return app


class UnavailableAgent:
    async def run(self, message: str):
        yield SseEvent(
            event="error",
            data={"code": "CONFIGURATION_ERROR", "message": "服务配置不可用，请检查后端启动参数"},
        )
        yield SseEvent(
            event="done",
            data={"reply": "", "cards": [], "toolCalls": [], "warnings": ["服务配置不可用"]},
        )


app = create_app()
