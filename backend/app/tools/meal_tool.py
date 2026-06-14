from typing import Any

from app.adapters.mealdb_client import MealDbClient
from app.domain.models import MealCard, ToolDataResult
from app.domain.normalizers import is_empty_result, normalize_meal


async def search_meals(client: MealDbClient, args: dict[str, Any]) -> ToolDataResult:
    limit = _limit(args)
    if ingredient := args.get("ingredient"):
        payload = await client.filter_by_ingredient(str(ingredient))
        return await _normalize_filter_results(client, payload, limit)
    if category := args.get("category"):
        payload = await client.filter_by_category(str(category))
        return await _normalize_filter_results(client, payload, limit)
    if area := args.get("area"):
        payload = await client.filter_by_area(str(area))
        return await _normalize_filter_results(client, payload, limit)
    if query := args.get("query"):
        payload = await client.search(str(query))
        return _normalize_detail_results(payload, limit)

    payload = await client.random()
    return _normalize_detail_results(payload, limit)


async def get_meal_detail(client: MealDbClient, args: dict[str, Any]) -> ToolDataResult:
    payload = await client.lookup(str(args["idMeal"]))
    return _normalize_detail_results(payload, 1)


async def _normalize_filter_results(client: MealDbClient, payload: dict[str, Any], limit: int) -> ToolDataResult:
    if is_empty_result(payload, "meals"):
        return ToolDataResult(status="empty", resultCount=0)

    cards: list[MealCard] = []
    lookup_count = 0
    for summary in _dedupe(payload.get("meals", []), "idMeal")[:limit]:
        meal_id = summary.get("idMeal")
        if not meal_id:
            continue
        lookup_count += 1
        detail_payload = await client.lookup(str(meal_id))
        if is_empty_result(detail_payload, "meals"):
            cards.append(normalize_meal(summary, "summary"))
            continue
        detail = detail_payload.get("meals", [summary])[0]
        cards.append(normalize_meal(detail, "detail"))

    status = "success" if cards else "empty"
    return ToolDataResult(status=status, cards=cards, resultCount=len(cards), lookupCount=lookup_count)


def _normalize_detail_results(payload: dict[str, Any], limit: int) -> ToolDataResult:
    if is_empty_result(payload, "meals"):
        return ToolDataResult(status="empty", resultCount=0)

    cards = [normalize_meal(raw, "detail") for raw in _dedupe(payload.get("meals", []), "idMeal")[:limit]]
    status = "success" if cards else "empty"
    return ToolDataResult(status=status, cards=cards, resultCount=len(cards))


def _dedupe(items: list[dict[str, Any]], id_field: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        item_id = str(item.get(id_field) or "")
        if not item_id or item_id in seen:
            continue
        seen.add(item_id)
        result.append(item)
    return result


def _limit(args: dict[str, Any]) -> int:
    return max(1, min(int(args.get("limit", 5)), 10))
