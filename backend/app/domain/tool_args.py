import re
from typing import Any

from pydantic import BaseModel


TERM_MAP = {
    "鸡肉": "chicken",
    "牛肉": "beef",
    "猪肉": "pork",
    "鸡蛋": "egg",
    "番茄": "tomato",
    "西红柿": "tomato",
    "意大利面": "pasta",
    "素食": "Vegetarian",
    "纯素": "Vegan",
    "日本": "Japanese",
    "日式": "Japanese",
    "印度": "Indian",
}

MEAL_CATEGORIES = {
    "Beef",
    "Breakfast",
    "Chicken",
    "Dessert",
    "Goat",
    "Lamb",
    "Miscellaneous",
    "Pasta",
    "Pork",
    "Seafood",
    "Side",
    "Starter",
    "Vegan",
    "Vegetarian",
}

MEAL_AREAS = {
    "American",
    "British",
    "Canadian",
    "Chinese",
    "Croatian",
    "Dutch",
    "Egyptian",
    "Filipino",
    "French",
    "Greek",
    "Indian",
    "Irish",
    "Italian",
    "Jamaican",
    "Japanese",
    "Kenyan",
    "Malaysian",
    "Mexican",
    "Moroccan",
    "Polish",
    "Portuguese",
    "Russian",
    "Spanish",
    "Thai",
    "Tunisian",
    "Turkish",
    "Ukrainian",
    "Uruguayan",
    "Vietnamese",
}

ID_SOURCES = {"candidate_card", "tool_result", "external_api"}


class NormalizedToolArg(BaseModel):
    value: str
    sourceText: str
    source: str
    confidence: str


class ToolValidationError(Exception):
    def __init__(self, field: str, reason: str, retryable: bool, allowed_values: list[str] | None = None):
        super().__init__(reason)
        self.field = field
        self.reason = reason
        self.retryable = retryable
        self.allowed_values = allowed_values or []


def normalize_user_terms(raw_args: dict[str, str], source: str) -> dict[str, NormalizedToolArg]:
    normalized: dict[str, NormalizedToolArg] = {}
    for field, raw_value in raw_args.items():
        value = _clean(raw_value)
        if not value or value in {"随便推荐", "随便", "随机"}:
            continue
        mapped = TERM_MAP.get(value, value)
        normalized[field] = NormalizedToolArg(
            value=mapped,
            sourceText=value,
            source=source,
            confidence="high" if mapped != value else "medium",
        )
    return normalized


def validate_search_meals_args(args: dict[str, Any]) -> dict[str, Any]:
    validated = _base_search_args(args, allowed_fields={"query", "ingredient", "category", "area", "limit", "recommendationMode"})
    if category := validated.get("category"):
        if category not in MEAL_CATEGORIES:
            raise ToolValidationError("category", "category must come from TheMealDB allowlist", True, sorted(MEAL_CATEGORIES))
    if area := validated.get("area"):
        if area not in MEAL_AREAS:
            raise ToolValidationError("area", "area must come from TheMealDB allowlist", True, sorted(MEAL_AREAS))
    return validated


def validate_search_cocktails_args(args: dict[str, Any]) -> dict[str, Any]:
    return _base_search_args(args, allowed_fields={"query", "ingredient", "limit", "allowAlcohol", "recommendationMode"})


def validate_get_meal_detail_args(args: dict[str, Any]) -> dict[str, Any]:
    return _validate_id_args(args, "idMeal")


def validate_get_cocktail_detail_args(args: dict[str, Any]) -> dict[str, Any]:
    return _validate_id_args(args, "idDrink")


def _base_search_args(args: dict[str, Any], allowed_fields: set[str]) -> dict[str, Any]:
    _reject_invalid_json_args(args)
    validated: dict[str, Any] = {}
    for field, value in args.items():
        if field not in allowed_fields:
            continue
        if field in {"query", "ingredient", "category", "area"}:
            text = _unwrap_arg(value)
            if not text:
                continue
            if field in {"query", "ingredient"} and _has_cjk(text):
                raise ToolValidationError(field, f"{field} must be normalized to English before calling external API", True)
            if len(text) > 100:
                raise ToolValidationError(field, f"{field} length must be <= 100", True)
            validated[field] = text
        elif field == "limit":
            validated[field] = _validate_limit(value)
        else:
            validated[field] = value

    validated.setdefault("limit", 5)
    return validated


def _validate_id_args(args: dict[str, Any], id_field: str) -> dict[str, Any]:
    _reject_invalid_json_args(args)
    value = _clean(args.get(id_field))
    if not value or not value.isdigit() or len(value) > 20:
        raise ToolValidationError(id_field, f"{id_field} must be a non-empty numeric string up to 20 characters", True)

    source = _clean(args.get("source") or args.get(f"{id_field}Source"))
    if source not in ID_SOURCES:
        raise ToolValidationError(
            id_field,
            f"{id_field} must come from candidate_card, tool_result or external_api; candidate source is required",
            False,
            sorted(ID_SOURCES),
        )
    return {id_field: value, "source": source}


def _validate_limit(value: Any) -> int:
    try:
        limit = int(value)
    except (TypeError, ValueError):
        raise ToolValidationError("limit", "limit must be an integer from 1 to 10", True) from None
    if limit < 1 or limit > 10:
        raise ToolValidationError("limit", "limit must be an integer from 1 to 10", True)
    return limit


def _unwrap_arg(value: Any) -> str | None:
    if isinstance(value, NormalizedToolArg):
        return _clean(value.value)
    return _clean(value)


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _has_cjk(value: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", value))


def _reject_invalid_json_args(args: dict[str, Any]) -> None:
    if "__invalid_json__" in args:
        raise ToolValidationError("arguments", "tool arguments must be valid JSON", True)
