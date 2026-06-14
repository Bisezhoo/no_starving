from typing import Any, Literal

from pydantic import BaseModel, Field


class IngredientItem(BaseModel):
    name: str
    measure: str | None = None


class MealCard(BaseModel):
    type: str = "meal"
    id: str
    detailLevel: str
    title: str
    localizedTitle: str | None = None
    localizedLanguage: str | None = None
    imageUrl: str
    category: str | None = None
    country: str | None = None
    tags: list[str] = Field(default_factory=list)
    ingredients: list[IngredientItem] = Field(default_factory=list)
    instructions: list[str] | None = None
    localizedSummary: str | None = None
    localizedInstructions: list[str] | None = None
    matchReasons: list[str] | None = None
    sourceUrl: str | None = None
    youtubeUrl: str | None = None


class CocktailCard(BaseModel):
    type: str = "cocktail"
    id: str
    detailLevel: str
    title: str
    localizedTitle: str | None = None
    localizedLanguage: str | None = None
    imageUrl: str
    category: str | None = None
    alcoholic: str | None = None
    glass: str | None = None
    tags: list[str] = Field(default_factory=list)
    ingredients: list[IngredientItem] = Field(default_factory=list)
    instructions: list[str] | None = None
    localizedSummary: str | None = None
    localizedInstructions: list[str] | None = None
    matchReasons: list[str] | None = None


Card = MealCard | CocktailCard


class TasteProfile(BaseModel):
    dietaryRestrictions: list[str] = Field(default_factory=list)
    likedIngredients: list[str] = Field(default_factory=list)
    dislikedIngredients: list[str] = Field(default_factory=list)
    preferredCuisines: list[str] = Field(default_factory=list)
    flavorPreferences: list[str] = Field(default_factory=list)
    allowAlcohol: bool | None = None


class RecommendationRecord(BaseModel):
    itemType: str
    itemId: str
    title: str
    recommendedAt: str
    mainIngredients: list[str] = Field(default_factory=list)
    category: str | None = None
    cuisine: str | None = None
    matchReasons: list[str] = Field(default_factory=list)


class ToolCallSummary(BaseModel):
    id: str
    name: str
    status: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    durationMs: int | None = None
    resultCount: int | None = None
    error: str | None = None


class AgentMemoryCandidate(BaseModel):
    type: str
    id: str
    title: str
    rank: int
    detailLevel: str
    mainIngredients: list[str] = Field(default_factory=list)
    category: str | None = None
    cuisine: str | None = None


class AgentMemory(BaseModel):
    updatedAt: str | None = None
    conversationSummary: str = ""
    recentTurns: list[dict[str, str]] = Field(default_factory=list)
    activeCandidates: list[AgentMemoryCandidate] = Field(default_factory=list)
    lastToolCalls: list[ToolCallSummary] = Field(default_factory=list)
    lastIntent: str | None = None


class UserChatHistoryMessage(BaseModel):
    role: Literal["user"]
    content: str
    createdAt: str


class AssistantChatHistoryMessage(BaseModel):
    role: Literal["assistant"]
    reply: str = ""
    cards: list[dict[str, Any]] = Field(default_factory=list)
    toolCalls: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    profileUpdates: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None
    createdAt: str


ChatHistoryMessage = UserChatHistoryMessage | AssistantChatHistoryMessage


class SseEvent(BaseModel):
    event: str
    data: dict[str, Any]


class ToolDataResult(BaseModel):
    status: str
    cards: list[Card] = Field(default_factory=list)
    resultCount: int = 0
    lookupCount: int = 0
    error: str | None = None
