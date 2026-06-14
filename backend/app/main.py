from pathlib import Path

from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.core.config import Settings
from app.core.logging import get_logger, log_event
from app.domain.models import SseEvent
from app.services.chat_history_store import ChatHistoryStore
from app.services.conversation_lock import ConversationLock
from app.services.default_agent import build_default_agent

logger = get_logger(__name__)


def create_app(agent=None, settings: Settings | None = None, data_dir: Path | str | None = None) -> FastAPI:
    app = FastAPI(title="No Starving Recipe Assistant")
    app.state.startup_error = None
    app.state.settings = settings
    app.state.chat_history_store = ChatHistoryStore(_resolve_data_dir(data_dir))
    if agent is None:
        try:
            app.state.settings = settings or Settings()
            _log_startup(app.state.settings)
            app.state.agent = build_default_agent(app.state.settings, data_dir=data_dir)
        except Exception as exc:
            app.state.startup_error = str(exc)
            log_event(
                logger,
                "app_startup_failed",
                settings=app.state.settings,
                fields={"errorType": type(exc).__name__, "error": str(exc), "logSwitches": _log_switches(app.state.settings)},
            )
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


def _resolve_data_dir(data_dir: Path | str | None) -> Path:
    if data_dir is not None:
        return Path(data_dir)
    return Path(__file__).resolve().parents[1] / "data"


def _log_startup(settings: Settings) -> None:
    log_event(
        logger,
        "app_startup",
        settings=settings,
        fields={
            "openrouterModel": settings.openrouter_model,
            "openrouterBaseUrl": settings.openrouter_base_url,
            "mealdbBaseUrl": settings.mealdb_base_url,
            "cocktaildbBaseUrl": settings.cocktaildb_base_url,
            "agentMaxToolCalls": settings.agent_max_tool_calls,
            "agentMaxLlmSteps": settings.agent_max_llm_steps,
            "logSwitches": _log_switches(settings),
        },
    )


def _log_switches(settings: Settings | None) -> dict[str, bool]:
    if settings is None:
        return {}
    return {
        "logFullSystemPrompt": settings.log_full_system_prompt,
        "logFullUserMessage": settings.log_full_user_message,
        "logFullSourceText": settings.log_full_source_text,
        "logSensitiveExternalHeaders": settings.log_sensitive_external_headers,
        "logStackTrace": settings.log_stack_trace,
    }


app = create_app()
