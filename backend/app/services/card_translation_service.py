import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, StrictStr, ValidationError

from app.core.logging import get_logger, log_event
from app.domain.card_localization import localize_cards as template_localize_cards
from app.domain.models import Card, IngredientItem
from app.services.openrouter_client import _parse_stream_payload

MAX_LOCALIZED_TEXT_LENGTH = 1000
PARTIAL_TRANSLATION_WARNING = "部分卡片翻译未通过校验，已保留原始内容"
TRANSLATION_UNAVAILABLE_WARNING = "卡片翻译暂不可用，已保留原始内容"


class PatchIngredientItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: StrictStr
    measure: StrictStr | None = None


class CardTranslationPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: StrictStr
    localizedTitle: StrictStr | None = None
    localizedSummary: StrictStr | None = None
    localizedIngredients: list[PatchIngredientItem] | None = None
    localizedInstructions: list[StrictStr] | None = None
    localizedCategory: StrictStr | None = None
    localizedCountry: StrictStr | None = None
    localizedAlcoholic: StrictStr | None = None
    localizedGlass: StrictStr | None = None


class CardPatchTranslator(Protocol):
    async def translate(self, cards: list[Card], locale: str, include_instructions: bool) -> list[dict[str, Any]]:
        ...


@dataclass
class CardTranslationResult:
    cards: list[Card]
    warnings: list[str]


class CardTranslationService:
    def __init__(
        self,
        translator: CardPatchTranslator | None = None,
        settings: Any | None = None,
        logger: logging.Logger | None = None,
    ):
        self.translator = translator
        self.settings = settings
        self.logger = logger or get_logger(__name__)

    async def localize_cards(self, cards: list[Card], locale: str, include_instructions: bool = False) -> CardTranslationResult:
        started = time.perf_counter()
        localized_cards = template_localize_cards(cards, locale, include_instructions)
        if not localized_cards:
            return CardTranslationResult(cards=[], warnings=[])

        if self.translator is None or _should_skip_translation(locale):
            self._log_finished(started, locale, len(localized_cards), translation_calls=0, skipped_count=len(localized_cards), failed_count=0)
            return CardTranslationResult(cards=localized_cards, warnings=[])

        try:
            patches = await self.translator.translate(localized_cards, locale, include_instructions)
        except Exception as exc:
            log_event(
                self.logger,
                "card_translation_failed",
                settings=self.settings,
                fields={"detectedLocale": locale, "cardCount": len(localized_cards), "errorType": type(exc).__name__, "error": str(exc)},
                level=logging.WARNING,
                exc_info=bool(getattr(self.settings, "log_stack_trace", False)),
            )
            return CardTranslationResult(cards=localized_cards, warnings=[TRANSLATION_UNAVAILABLE_WARNING])

        patched_cards, failed_count = _merge_valid_patches(localized_cards, patches, include_instructions)
        self._log_finished(
            started,
            locale,
            len(localized_cards),
            translation_calls=1,
            skipped_count=0,
            failed_count=failed_count,
        )
        warnings = [PARTIAL_TRANSLATION_WARNING] if failed_count else []
        return CardTranslationResult(cards=patched_cards, warnings=warnings)

    def _log_finished(
        self,
        started: float,
        locale: str,
        card_count: int,
        translation_calls: int,
        skipped_count: int,
        failed_count: int,
    ) -> None:
        log_event(
            self.logger,
            "card_translation_finished",
            settings=self.settings,
            fields={
                "detectedLocale": locale,
                "cardCount": card_count,
                "translationCallCount": translation_calls,
                "skippedCount": skipped_count,
                "patchFailedCount": failed_count,
                "durationMs": int((time.perf_counter() - started) * 1000),
            },
        )


class OpenRouterCardTranslator:
    def __init__(self, client: Any):
        self.client = client

    async def translate(self, cards: list[Card], locale: str, include_instructions: bool) -> list[dict[str, Any]]:
        content_parts: list[str] = []
        async for line in self.client.stream_chat(_build_translation_messages(cards, locale, include_instructions), tools=[]):
            payload = _parse_stream_payload(line)
            if payload is None:
                continue
            for choice in payload.get("choices", []):
                delta = choice.get("delta") or {}
                if content := delta.get("content"):
                    content_parts.append(str(content))
        return _parse_translation_json("".join(content_parts))


def _merge_valid_patches(cards: list[Card], raw_patches: Any, include_instructions: bool) -> tuple[list[Card], int]:
    if not isinstance(raw_patches, list):
        return cards, len(cards)

    cards_by_id = {card.id: card for card in cards}
    applied_ids: set[str] = set()
    failed_count = 0
    for raw_patch in raw_patches:
        normalized_patch = _validate_patch(raw_patch, cards_by_id, include_instructions)
        if normalized_patch is None or normalized_patch["id"] in applied_ids:
            failed_count += 1
            continue
        applied_ids.add(normalized_patch["id"])
        _apply_patch(cards_by_id[normalized_patch["id"]], normalized_patch)
    return cards, failed_count


def _validate_patch(raw_patch: Any, cards_by_id: dict[str, Card], include_instructions: bool) -> dict[str, Any] | None:
    try:
        patch = CardTranslationPatch.model_validate(raw_patch)
    except ValidationError:
        return None

    if patch.id not in cards_by_id:
        return None

    card = cards_by_id[patch.id]
    normalized: dict[str, Any] = {"id": patch.id}
    for field_name in (
        "localizedTitle",
        "localizedSummary",
        "localizedCategory",
        "localizedCountry",
        "localizedAlcoholic",
        "localizedGlass",
    ):
        value = getattr(patch, field_name)
        if value is not None:
            cleaned = _clean_text(value)
            if cleaned is None:
                return None
            normalized[field_name] = cleaned

    if patch.localizedIngredients is not None:
        if len(patch.localizedIngredients) != len(card.ingredients):
            return None
        ingredients: list[IngredientItem] = []
        for ingredient in patch.localizedIngredients:
            name = _clean_text(ingredient.name)
            if name is None:
                return None
            measure = _clean_optional_text(ingredient.measure)
            ingredients.append(IngredientItem(name=name, measure=measure))
        normalized["localizedIngredients"] = ingredients

    if patch.localizedInstructions is not None:
        if not include_instructions or not card.instructions or len(patch.localizedInstructions) != len(card.instructions):
            return None
        instructions: list[str] = []
        for instruction in patch.localizedInstructions:
            cleaned = _clean_text(instruction)
            if cleaned is None:
                return None
            instructions.append(cleaned)
        normalized["localizedInstructions"] = instructions

    return normalized


def _apply_patch(card: Card, patch: dict[str, Any]) -> None:
    for field_name, value in patch.items():
        if field_name != "id":
            setattr(card, field_name, value)


def _clean_text(value: str) -> str | None:
    cleaned = value.strip()
    if not cleaned or len(cleaned) > MAX_LOCALIZED_TEXT_LENGTH:
        return None
    return cleaned


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    return _clean_text(value)


def _should_skip_translation(locale: str) -> bool:
    return locale.lower().startswith("en")


def _build_translation_messages(cards: list[Card], locale: str, include_instructions: bool) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "Translate recipe card display fields. Return JSON only, with no markdown. "
                "Return an array of patches. Each patch must include id and may include only localizedTitle, "
                "localizedSummary, localizedIngredients, localizedInstructions, localizedCategory, localizedCountry, "
                "localizedAlcoholic, localizedGlass. Do not change facts, ids, original names, ingredient counts, or step counts."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {"targetLocale": locale, "includeInstructions": include_instructions, "cards": [_translation_payload(card, include_instructions) for card in cards]},
                ensure_ascii=False,
                separators=(",", ":"),
            ),
        },
    ]


def _translation_payload(card: Card, include_instructions: bool) -> dict[str, Any]:
    payload = {
        "id": card.id,
        "type": card.type,
        "title": card.title,
        "category": getattr(card, "category", None),
        "country": getattr(card, "country", None),
        "alcoholic": getattr(card, "alcoholic", None),
        "glass": getattr(card, "glass", None),
        "ingredients": [ingredient.model_dump(mode="json") for ingredient in card.ingredients],
        "localizedSummary": card.localizedSummary,
    }
    if include_instructions:
        payload["instructions"] = card.instructions or []
    return payload


def _parse_translation_json(content: str) -> list[dict[str, Any]]:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    parsed = json.loads(text)
    if isinstance(parsed, dict) and isinstance(parsed.get("patches"), list):
        parsed = parsed["patches"]
    if not isinstance(parsed, list):
        raise ValueError("translation response must be a JSON array")
    return parsed
