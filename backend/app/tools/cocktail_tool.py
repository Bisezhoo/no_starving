from typing import Any

from app.adapters.cocktaildb_client import CocktailDbClient
from app.domain.models import CocktailCard, ToolDataResult
from app.domain.normalizers import is_empty_result, normalize_cocktail


async def search_cocktails(client: CocktailDbClient, args: dict[str, Any]) -> ToolDataResult:
    limit = _limit(args)
    allow_alcohol = args.get("allowAlcohol")
    if ingredient := args.get("ingredient"):
        payload = await client.filter_by_ingredient(str(ingredient))
        return await _normalize_filter_results(client, payload, limit, allow_alcohol)
    if query := args.get("query"):
        payload = await client.search(str(query))
        return _normalize_detail_results(payload, limit, allow_alcohol)

    payload = await client.random()
    return _normalize_detail_results(payload, limit, allow_alcohol)


async def _normalize_filter_results(
    client: CocktailDbClient,
    payload: dict[str, Any],
    limit: int,
    allow_alcohol: bool | None,
) -> ToolDataResult:
    if is_empty_result(payload, "drinks"):
        return ToolDataResult(status="empty", resultCount=0)

    cards: list[CocktailCard] = []
    lookup_count = 0
    for summary in _dedupe(payload.get("drinks", []), "idDrink")[:limit]:
        drink_id = summary.get("idDrink")
        if not drink_id:
            continue
        lookup_count += 1
        detail_payload = await client.lookup(str(drink_id))
        if is_empty_result(detail_payload, "drinks"):
            continue
        detail = detail_payload.get("drinks", [summary])[0]
        card = normalize_cocktail(detail, "detail")
        if _is_allowed_by_alcohol(card, allow_alcohol):
            cards.append(card)

    status = "success" if cards else "empty"
    return ToolDataResult(status=status, cards=cards, resultCount=len(cards), lookupCount=lookup_count)


def _normalize_detail_results(payload: dict[str, Any], limit: int, allow_alcohol: bool | None) -> ToolDataResult:
    if is_empty_result(payload, "drinks"):
        return ToolDataResult(status="empty", resultCount=0)

    cards = [
        card
        for raw in _dedupe(payload.get("drinks", []), "idDrink")[:limit]
        if _is_allowed_by_alcohol(card := normalize_cocktail(raw, "detail"), allow_alcohol)
    ]
    status = "success" if cards else "empty"
    return ToolDataResult(status=status, cards=cards, resultCount=len(cards))


def _is_allowed_by_alcohol(card: CocktailCard, allow_alcohol: bool | None) -> bool:
    if allow_alcohol is False:
        return (card.alcoholic or "").strip().lower() != "alcoholic"
    return True


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
