from functools import partial
from pathlib import Path
from typing import Any

from app.adapters.cocktaildb_client import CocktailDbClient
from app.adapters.mealdb_client import MealDbClient
from app.core.config import Settings
from app.domain.tool_args import (
    validate_get_meal_detail_args,
    validate_search_cocktails_args,
    validate_search_meals_args,
)
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.card_translation_service import CardTranslationService, OpenRouterCardTranslator
from app.services.memory_store import MemoryStore
from app.services.openrouter_client import OpenRouterClient, OpenRouterStepLlm
from app.services.tool_runner import ToolRunner
from app.tools.cocktail_tool import search_cocktails
from app.tools.meal_tool import get_meal_detail, search_meals


def build_default_agent(settings: Settings, data_dir: Path | str | None = None) -> AgentOrchestrator:
    meal_client = MealDbClient(
        settings.mealdb_base_url,
        proxy=settings.outbound_http_proxy,
        trust_env=settings.outbound_http_trust_env,
    )
    cocktail_client = CocktailDbClient(
        settings.cocktaildb_base_url,
        proxy=settings.outbound_http_proxy,
        trust_env=settings.outbound_http_trust_env,
    )
    tool_runner = ToolRunner(
        tools={
            "search_meals": partial(search_meals, meal_client),
            "get_meal_detail": partial(get_meal_detail, meal_client),
            "search_cocktails": partial(search_cocktails, cocktail_client),
        },
        validators={
            "search_meals": validate_search_meals_args,
            "get_meal_detail": validate_get_meal_detail_args,
            "search_cocktails": validate_search_cocktails_args,
        },
        settings=settings,
    )
    openrouter = OpenRouterClient(
        api_key=settings.openrouter_api_key,
        model=settings.openrouter_model,
        base_url=settings.openrouter_base_url,
        proxy=settings.outbound_http_proxy,
        trust_env=settings.outbound_http_trust_env,
    )
    llm = OpenRouterStepLlm(client=openrouter, tools=_tool_specs())
    card_translation_service = CardTranslationService(
        translator=OpenRouterCardTranslator(openrouter),
        settings=settings,
    )
    store = MemoryStore(Path(data_dir) if data_dir is not None else _default_data_dir())
    return AgentOrchestrator(
        llm=llm,
        tool_runner=tool_runner,
        memory_store=store,
        settings=settings,
        card_translation_service=card_translation_service,
        max_tool_calls=settings.agent_max_tool_calls,
        max_llm_steps=settings.agent_max_llm_steps,
    )


def _default_data_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "data"


def _tool_specs() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "search_meals",
                "description": "Search meals from TheMealDB. Use English query or ingredient arguments.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "ingredient": {"type": "string"},
                        "category": {"type": "string"},
                        "area": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 10},
                    },
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_meal_detail",
                "description": "Load one meal detail by idMeal that came from a previous candidate or tool result.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "idMeal": {"type": "string"},
                        "source": {"type": "string", "enum": ["candidate_card", "tool_result", "external_api"]},
                    },
                    "required": ["idMeal", "source"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_cocktails",
                "description": "Search drinks from TheCocktailDB. Use allowAlcohol=false when the user says they do not drink alcohol.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "ingredient": {"type": "string"},
                        "allowAlcohol": {"type": "boolean"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 10},
                    },
                    "additionalProperties": False,
                },
            },
        },
    ]
