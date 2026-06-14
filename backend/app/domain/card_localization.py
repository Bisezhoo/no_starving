from app.domain.models import Card


ZH_INSTRUCTION_HINTS = ("怎么做", "做法", "步骤", "详细", "教程")
EN_INSTRUCTION_HINTS = ("how to", "cook", "make", "instruction", "step", "detail")


def should_localize_instructions(message: str) -> bool:
    lowered = message.lower()
    return any(hint in message for hint in ZH_INSTRUCTION_HINTS) or any(hint in lowered for hint in EN_INSTRUCTION_HINTS)


def localize_cards(cards: list[Card], locale: str, include_instructions: bool = False) -> list[Card]:
    return [_localize_card(card, locale, include_instructions) for card in cards]


def _localize_card(card: Card, locale: str, include_instructions: bool) -> Card:
    localized = card.model_copy(deep=True)
    localized.localizedLanguage = locale
    localized.localizedSummary = _summary(localized, locale)
    if include_instructions and localized.instructions:
        localized.localizedInstructions = _instructions(localized.instructions, locale)
    return localized


def _summary(card: Card, locale: str) -> str:
    if locale == "zh-CN":
        return _zh_summary(card)
    return _en_summary(card)


def _zh_summary(card: Card) -> str:
    ingredients = _join_names([ingredient.name for ingredient in card.ingredients[:5]], "、") or "外部 API 返回的配料"
    if card.type == "cocktail":
        details = _join_names([getattr(card, "category", None), getattr(card, "alcoholic", None), getattr(card, "glass", None)], "、")
        prefix = f"{details}饮品" if details else "饮品"
        return f"推荐 {card.title}：这是一款{prefix}，主要配料包括 {ingredients}。"

    details = _join_names([getattr(card, "country", None), getattr(card, "category", None)], "、")
    prefix = f"{details}菜谱" if details else "菜谱"
    return f"推荐 {card.title}：这是一道{prefix}，主要食材包括 {ingredients}。"


def _en_summary(card: Card) -> str:
    ingredients = _join_names([ingredient.name for ingredient in card.ingredients[:5]], ", ") or "the listed ingredients"
    if card.type == "cocktail":
        details = _join_names([getattr(card, "category", None), getattr(card, "alcoholic", None), getattr(card, "glass", None)], ", ")
        suffix = f" ({details})" if details else ""
        return f"Recommended {card.title}{suffix}. Main ingredients: {ingredients}."

    details = _join_names([getattr(card, "country", None), getattr(card, "category", None)], ", ")
    suffix = f" ({details})" if details else ""
    return f"Recommended {card.title}{suffix}. Main ingredients: {ingredients}."


def _instructions(instructions: list[str], locale: str) -> list[str]:
    if locale == "zh-CN":
        return [f"步骤 {index}：{instruction}" for index, instruction in enumerate(instructions, start=1)]
    return [f"Step {index}: {instruction}" for index, instruction in enumerate(instructions, start=1)]


def _join_names(values: list[str | None], separator: str) -> str:
    return separator.join(value for value in values if value)
