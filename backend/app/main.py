from fastapi import FastAPI

from app.api.chat import PlaceholderAgent
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.services.conversation_lock import ConversationLock


def create_app(agent=None) -> FastAPI:
    app = FastAPI(title="No Starving Recipe Assistant")
    app.state.agent = agent or PlaceholderAgent()
    app.state.conversation_lock = ConversationLock()
    app.include_router(health_router)
    app.include_router(chat_router)
    return app


app = create_app()
