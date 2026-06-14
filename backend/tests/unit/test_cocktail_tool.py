import pytest
import respx

from app.adapters.cocktaildb_client import CocktailDbClient
from app.tools.cocktail_tool import search_cocktails


@pytest.mark.asyncio
@respx.mock
async def test_search_cocktails_filters_alcohol_when_user_says_no():
    respx.get(
        "https://www.thecocktaildb.com/api/json/v1/1/search.php",
        params={"s": "lemon"},
    ).respond(
        200,
        json={
            "drinks": [
                {
                    "idDrink": "11007",
                    "strDrink": "Margarita",
                    "strDrinkThumb": "https://img/m.jpg",
                    "strAlcoholic": "Alcoholic",
                },
                {
                    "idDrink": "12720",
                    "strDrink": "Lemonade",
                    "strDrinkThumb": "https://img/l.jpg",
                    "strAlcoholic": "Non alcoholic",
                },
            ]
        },
    )

    client = CocktailDbClient(base_url="https://www.thecocktaildb.com/api/json/v1/1", timeout_seconds=8, trust_env=False)
    result = await search_cocktails(client, {"query": "lemon", "allowAlcohol": False, "limit": 5})

    assert [card.title for card in result.cards] == ["Lemonade"]
