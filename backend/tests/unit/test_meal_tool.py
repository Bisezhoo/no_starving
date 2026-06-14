import pytest
import respx
from httpx import Response

from app.adapters.mealdb_client import MealDbClient
from app.tools.meal_tool import search_meals


@pytest.mark.asyncio
@respx.mock
async def test_search_meals_filter_limits_lookup_count():
    respx.get(
        "https://www.themealdb.com/api/json/v1/1/filter.php",
        params={"i": "chicken"},
    ).respond(
        200,
        json={
            "meals": [
                {"idMeal": "1", "strMeal": "A", "strMealThumb": "https://img/a.jpg", "strCountry": "US"},
                {"idMeal": "2", "strMeal": "B", "strMealThumb": "https://img/b.jpg", "strCountry": "US"},
            ]
        },
    )
    respx.get(
        "https://www.themealdb.com/api/json/v1/1/lookup.php",
        params={"i": "1"},
    ).mock(
        return_value=Response(
            200,
            json={
                "meals": [
                    {
                        "idMeal": "1",
                        "strMeal": "A",
                        "strMealThumb": "https://img/a.jpg",
                        "strIngredient1": "Chicken",
                        "strMeasure1": "1 kg",
                        "strInstructions": "Cook.",
                    }
                ]
            },
        )
    )

    client = MealDbClient(base_url="https://www.themealdb.com/api/json/v1/1", timeout_seconds=8, trust_env=False)
    result = await search_meals(client, {"ingredient": "chicken", "limit": 1})

    assert len(result.cards) == 1
    assert result.lookupCount == 1
    assert result.cards[0].id == "1"
    assert result.cards[0].detailLevel == "detail"
