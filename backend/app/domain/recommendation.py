from collections import Counter
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.domain.models import Card, CocktailCard, RecommendationRecord, TasteProfile


class RecommendationExplanation(BaseModel):
    reasons: list[str] = Field(default_factory=list)


def rank_recommendations(
    cards: list[Card],
    profile: TasteProfile,
    history: list[RecommendationRecord],
) -> tuple[list[Card], RecommendationExplanation]:
    explanation = RecommendationExplanation()
    recent_ids = {record.itemId for record in history[-10:]}
    repeated_ingredients = _repeated_recent_values(history, "mainIngredients")
    repeated_categories = _repeated_recent_scalar(history, "category")
    repeated_cuisines = _repeated_recent_scalar(history, "cuisine")

    scored: list[tuple[int, int, Card]] = []
    for index, card in enumerate(cards):
        if card.id in recent_ids:
            _add_reason(explanation, "recent_item_hard_dedupe")
            continue
        if _hits_hard_filter(card, profile):
            _add_reason(explanation, "hard_filter")
            continue

        score = 0
        ingredients = _main_ingredients(card)
        if any(item in profile.likedIngredients for item in ingredients):
            score += 10
            _add_reason(explanation, "liked_ingredient_match")
        if any(item in repeated_ingredients for item in ingredients):
            score -= 8
            _add_reason(explanation, "recent_main_ingredient_downrank")
        if (category := (getattr(card, "category", None) or "").lower()) in repeated_categories:
            score -= 4
            _add_reason(explanation, "recent_category_downrank")
        if (cuisine := (getattr(card, "country", None) or "").lower()) in repeated_cuisines:
            score -= 4
            _add_reason(explanation, "recent_cuisine_downrank")

        scored.append((score, -index, card))

    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [item[2] for item in scored], explanation


def append_history(history: list[RecommendationRecord], displayed_cards: list[Card]) -> list[RecommendationRecord]:
    now = datetime.now(UTC).isoformat()
    new_records = [
        RecommendationRecord(
            itemType=card.type,
            itemId=card.id,
            title=card.title,
            recommendedAt=now,
            mainIngredients=_main_ingredients(card),
            category=getattr(card, "category", None),
            cuisine=getattr(card, "country", None),
            matchReasons=card.matchReasons or [],
        )
        for card in displayed_cards
    ]
    return (history + new_records)[-20:]


def _hits_hard_filter(card: Card, profile: TasteProfile) -> bool:
    ingredients = set(_main_ingredients(card))
    if ingredients.intersection(set(profile.dislikedIngredients)):
        return True
    if profile.allowAlcohol is False and isinstance(card, CocktailCard):
        return (card.alcoholic or "").strip().lower() == "alcoholic"
    if any(restriction.lower() in {"vegetarian", "vegan"} for restriction in profile.dietaryRestrictions):
        return _has_obvious_meat(ingredients)
    return False


def _main_ingredients(card: Card) -> list[str]:
    return [ingredient.name.strip().lower() for ingredient in card.ingredients if ingredient.name.strip()]


def _repeated_recent_values(history: list[RecommendationRecord], field: str) -> set[str]:
    values: list[str] = []
    for record in history[-3:]:
        values.extend(item.lower() for item in getattr(record, field))
    return {value for value, count in Counter(values).items() if count >= 2}


def _repeated_recent_scalar(history: list[RecommendationRecord], field: str) -> set[str]:
    values = [
        value.lower()
        for record in history[-3:]
        if (value := getattr(record, field)) is not None
    ]
    return {value for value, count in Counter(values).items() if count >= 2}


def _has_obvious_meat(ingredients: set[str]) -> bool:
    return bool(ingredients.intersection({"beef", "chicken", "pork", "lamb", "goat", "seafood", "fish", "shrimp"}))


def _add_reason(explanation: RecommendationExplanation, reason: str) -> None:
    if reason not in explanation.reasons:
        explanation.reasons.append(reason)
