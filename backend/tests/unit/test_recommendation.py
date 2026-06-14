from app.domain.models import MealCard, RecommendationRecord, TasteProfile
from app.domain.recommendation import rank_recommendations


def meal(item_id: str, title: str, ingredients: list[str], category: str = "Beef") -> MealCard:
    return MealCard(
        id=item_id,
        detailLevel="detail",
        title=title,
        imageUrl="https://img.example/x.jpg",
        category=category,
        country="US",
        tags=[],
        ingredients=[{"name": name} for name in ingredients],
    )


def test_disliked_ingredient_is_hard_filter():
    profile = TasteProfile(dislikedIngredients=["beef"])
    cards, explanation = rank_recommendations([meal("1", "Beef Pie", ["beef"])], profile, [])
    assert cards == []
    assert "hard_filter" in explanation.reasons


def test_recent_main_ingredient_is_soft_downranked():
    profile = TasteProfile()
    history = [
        RecommendationRecord(
            itemType="meal",
            itemId="old1",
            title="A",
            recommendedAt="2026-06-10T00:00:00Z",
            mainIngredients=["beef"],
            matchReasons=[],
        ),
        RecommendationRecord(
            itemType="meal",
            itemId="old2",
            title="B",
            recommendedAt="2026-06-11T00:00:00Z",
            mainIngredients=["beef"],
            matchReasons=[],
        ),
    ]
    cards, explanation = rank_recommendations(
        [meal("1", "Beef Pie", ["beef"]), meal("2", "Chicken Rice", ["chicken"], "Chicken")],
        profile,
        history,
    )
    assert cards[0].id == "2"
    assert "recent_main_ingredient_downrank" in explanation.reasons
