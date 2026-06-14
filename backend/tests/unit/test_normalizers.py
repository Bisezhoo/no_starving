from app.domain.normalizers import is_empty_result, normalize_cocktail, normalize_meal


def test_meal_normalizer_pairs_ingredients_and_trims_fields():
    raw = {
        "idMeal": "52795",
        "strMeal": " Chicken Handi ",
        "strMealThumb": "https://img.example/meal.jpg",
        "strCategory": "Chicken",
        "strCountry": "India",
        "strArea": None,
        "strIngredient1": " Chicken ",
        "strMeasure1": " 1 kg ",
        "strIngredient2": "",
        "strMeasure2": "ignored",
        "strIngredient3": "Tomato",
        "strMeasure3": "",
        "strInstructions": "Step one.\r\nStep two.",
        "strTags": "Spicy, Meat",
        "strSource": "https://source.example",
        "strYoutube": "",
    }
    card = normalize_meal(raw, detail_level="detail")
    assert card.title == "Chicken Handi"
    assert card.country == "India"
    assert card.ingredients[0].name == "Chicken"
    assert card.ingredients[0].measure == "1 kg"
    assert card.ingredients[1].name == "Tomato"
    assert card.instructions == ["Step one.", "Step two."]
    assert card.tags == ["Spicy", "Meat"]


def test_cocktail_no_data_found_is_only_top_level_empty():
    assert is_empty_result({"drinks": "no data found"}, "drinks") is True
    card = normalize_cocktail(
        {
            "idDrink": "11007",
            "strDrink": "Margarita",
            "strDrinkThumb": "https://img.example/drink.jpg",
            "strCategory": "Ordinary Drink",
            "strAlcoholic": "Alcoholic",
            "strGlass": "Cocktail glass",
            "strInstructions": "no data found",
            "strIngredient1": "Tequila",
            "strMeasure1": "1 1/2 oz",
        },
        detail_level="detail",
    )
    assert card.instructions == ["no data found"]
