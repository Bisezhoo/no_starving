import pytest

from app.domain.models import MealCard
from app.services.card_translation_service import CardTranslationService


class RecordingTranslator:
    def __init__(self, patches=None, error: Exception | None = None):
        self.patches = patches or []
        self.error = error
        self.calls = []

    async def translate(self, cards, locale, include_instructions):
        self.calls.append({"cards": cards, "locale": locale, "include_instructions": include_instructions})
        if self.error:
            raise self.error
        return self.patches


def meal_card(card_id: str = "meal_1") -> MealCard:
    return MealCard(
        id=card_id,
        detailLevel="detail",
        title="Chicken Rice",
        imageUrl="https://img.example/chicken-rice.jpg",
        category="Chicken",
        country="Japanese",
        ingredients=[{"name": "chicken", "measure": "1 cup"}, {"name": "rice"}],
        instructions=["Cook chicken.", "Serve with rice."],
    )


@pytest.mark.asyncio
async def test_same_output_language_skips_llm_translation():
    translator = RecordingTranslator(patches=[{"id": "meal_1", "localizedTitle": "鸡肉饭"}])
    service = CardTranslationService(translator=translator)

    result = await service.localize_cards([meal_card()], "en-US", include_instructions=True)

    assert translator.calls == []
    assert result.warnings == []
    assert result.cards[0].localizedLanguage == "en-US"
    assert result.cards[0].localizedTitle is None
    assert result.cards[0].localizedInstructions == ["Step 1: Cook chicken.", "Step 2: Serve with rice."]


@pytest.mark.asyncio
async def test_applies_valid_translation_patch_without_overwriting_original_fields():
    translator = RecordingTranslator(
        patches=[
            {
                "id": "meal_1",
                "localizedTitle": "鸡肉饭",
                "localizedSummary": "适合想吃鸡肉的晚餐。",
                "localizedCategory": "鸡肉",
                "localizedCountry": "日式",
                "localizedIngredients": [{"name": "鸡肉", "measure": "1 杯"}, {"name": "米饭"}],
                "localizedInstructions": ["烹饪鸡肉。", "配米饭食用。"],
            }
        ]
    )
    service = CardTranslationService(translator=translator)

    result = await service.localize_cards([meal_card()], "zh-CN", include_instructions=True)

    assert result.warnings == []
    card = result.cards[0]
    assert card.title == "Chicken Rice"
    assert card.ingredients[0].name == "chicken"
    assert card.instructions == ["Cook chicken.", "Serve with rice."]
    assert card.localizedLanguage == "zh-CN"
    assert card.localizedTitle == "鸡肉饭"
    assert card.localizedSummary == "适合想吃鸡肉的晚餐。"
    assert card.localizedCategory == "鸡肉"
    assert card.localizedCountry == "日式"
    assert [ingredient.name for ingredient in card.localizedIngredients] == ["鸡肉", "米饭"]
    assert card.localizedInstructions == ["烹饪鸡肉。", "配米饭食用。"]


@pytest.mark.asyncio
async def test_discards_invalid_patch_but_keeps_valid_patch_for_other_cards():
    translator = RecordingTranslator(
        patches=[
            {
                "id": "meal_1",
                "localizedIngredients": [{"name": "鸡肉"}],
            },
            {
                "id": "meal_2",
                "localizedTitle": "番茄饭",
                "localizedIngredients": [{"name": "番茄", "measure": "1 个"}, {"name": "米饭"}],
            },
        ]
    )
    service = CardTranslationService(translator=translator)

    result = await service.localize_cards([meal_card("meal_1"), meal_card("meal_2")], "zh-CN")

    assert result.cards[0].localizedTitle is None
    assert result.cards[0].localizedIngredients is None
    assert result.cards[1].localizedTitle == "番茄饭"
    assert [ingredient.name for ingredient in result.cards[1].localizedIngredients] == ["番茄", "米饭"]
    assert result.warnings == ["部分卡片翻译未通过校验，已保留原始内容"]


@pytest.mark.asyncio
async def test_translation_error_falls_back_to_template_localization():
    translator = RecordingTranslator(error=RuntimeError("translator unavailable"))
    service = CardTranslationService(translator=translator)

    result = await service.localize_cards([meal_card()], "zh-CN", include_instructions=True)

    assert result.cards[0].localizedLanguage == "zh-CN"
    assert "Chicken Rice" in result.cards[0].localizedSummary
    assert result.cards[0].localizedTitle is None
    assert result.cards[0].localizedInstructions == ["步骤 1：Cook chicken.", "步骤 2：Serve with rice."]
    assert result.warnings == ["卡片翻译暂不可用，已保留原始内容"]
