import re
from typing import Any

from app.domain.models import CocktailCard, IngredientItem, MealCard


def clean_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "null":
        return None
    return text


def split_tags(value: object) -> list[str]:
    text = clean_text(value)
    if not text:
        return []
    return [tag for part in text.split(",") if (tag := part.strip())]


def split_instructions(value: object) -> list[str] | None:
    text = clean_text(value)
    if not text:
        return None

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if "\n" in normalized:
        parts = [part.strip() for part in normalized.split("\n")]
    else:
        parts = re.split(r"(?=\b(?:Step\s+\d+|STEP\s+\d+|\d+\.)\b)", normalized)

    cleaned = [part for part in parts if part]
    return cleaned or [text]


def extract_ingredients(raw: dict[str, Any], max_items: int) -> list[IngredientItem]:
    ingredients: list[IngredientItem] = []
    for index in range(1, max_items + 1):
        ingredient = clean_text(raw.get(f"strIngredient{index}"))
        measure = clean_text(raw.get(f"strMeasure{index}"))
        if not ingredient:
            continue
        ingredients.append(IngredientItem(name=ingredient, measure=measure))
    return ingredients


def is_empty_result(payload: dict[str, Any], root_key: str) -> bool:
    value = payload.get(root_key)
    if value is None:
        return True
    if root_key == "drinks" and isinstance(value, str) and value.strip().lower() == "no data found":
        return True
    return False


def normalize_meal(raw: dict[str, Any], detail_level: str) -> MealCard:
    country = clean_text(raw.get("strCountry")) or clean_text(raw.get("strArea"))
    return MealCard(
        id=clean_text(raw.get("idMeal")) or "",
        detailLevel=detail_level,
        title=clean_text(raw.get("strMeal")) or "",
        imageUrl=clean_text(raw.get("strMealThumb")) or "",
        category=clean_text(raw.get("strCategory")),
        country=country,
        tags=split_tags(raw.get("strTags")),
        ingredients=extract_ingredients(raw, 20),
        instructions=split_instructions(raw.get("strInstructions")),
        sourceUrl=clean_text(raw.get("strSource")),
        youtubeUrl=clean_text(raw.get("strYoutube")),
    )


def normalize_cocktail(raw: dict[str, Any], detail_level: str) -> CocktailCard:
    return CocktailCard(
        id=clean_text(raw.get("idDrink")) or "",
        detailLevel=detail_level,
        title=clean_text(raw.get("strDrink")) or "",
        imageUrl=clean_text(raw.get("strDrinkThumb")) or "",
        category=clean_text(raw.get("strCategory")),
        alcoholic=clean_text(raw.get("strAlcoholic")),
        glass=clean_text(raw.get("strGlass")),
        tags=split_tags(raw.get("strTags")),
        ingredients=extract_ingredients(raw, 15),
        instructions=split_instructions(raw.get("strInstructions")),
    )
