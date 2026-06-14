from app.domain.card_localization import localize_cards, should_localize_instructions
from app.domain.models import MealCard


def test_localize_cards_adds_summary_and_instruction_when_requested():
    card = MealCard(
        id="meal_1",
        detailLevel="detail",
        title="Chicken Rice",
        imageUrl="https://img.example/chicken-rice.jpg",
        category="Chicken",
        country="Japanese",
        ingredients=[{"name": "chicken"}, {"name": "rice"}],
        instructions=["Cook chicken with rice until tender."],
    )

    localized = localize_cards([card], "zh-CN", include_instructions=True)[0]

    assert localized.localizedLanguage == "zh-CN"
    assert "Chicken Rice" in localized.localizedSummary
    assert localized.localizedInstructions == ["步骤 1：Cook chicken with rice until tender."]
    assert localized.instructions == ["Cook chicken with rice until tender."]


def test_should_localize_instructions_detects_detail_intent():
    assert should_localize_instructions("第一个怎么做") is True
    assert should_localize_instructions("How do I make the first one?") is True
    assert should_localize_instructions("我想吃鸡肉") is False
