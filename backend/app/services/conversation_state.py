from app.domain.models import AgentMemory, RecommendationRecord, TasteProfile


class ConversationState:
    def __init__(
        self,
        profile: TasteProfile | None = None,
        history: list[RecommendationRecord] | None = None,
        memory: AgentMemory | None = None,
    ):
        self.profile = profile or TasteProfile()
        self.history = history or []
        self.memory = memory or AgentMemory()
