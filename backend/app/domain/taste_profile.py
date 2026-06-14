from app.domain.models import TasteProfile


INGREDIENT_SIGNALS = {
    "牛肉": "beef",
    "鸡肉": "chicken",
    "香菜": "coriander",
}


def empty_profile() -> TasteProfile:
    return TasteProfile()


def merge_profile_from_message(profile: TasteProfile, message: str) -> tuple[TasteProfile, dict]:
    updated = profile.model_copy(deep=True)
    patch: dict = {}

    if any(signal in message for signal in ("不喝酒", "不要酒精", "无酒精", "不含酒精")):
        updated.allowAlcohol = False
        patch["allowAlcohol"] = False
    elif any(signal in message for signal in ("可以喝酒", "能喝酒")):
        updated.allowAlcohol = True
        patch["allowAlcohol"] = True

    for chinese, english in INGREDIENT_SIGNALS.items():
        if f"不吃{chinese}" in message or f"不要{chinese}" in message:
            _append_unique(updated.dislikedIngredients, english)
            patch["dislikedIngredients"] = updated.dislikedIngredients
        if f"喜欢{chinese}" in message or f"想吃{chinese}" in message:
            _append_unique(updated.likedIngredients, english)
            patch["likedIngredients"] = updated.likedIngredients

    if "清淡" in message:
        _append_unique(updated.flavorPreferences, "light")
        patch["flavorPreferences"] = updated.flavorPreferences

    return updated, patch


def _append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)
