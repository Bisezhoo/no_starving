from app.domain.tool_args import (
    NormalizedToolArg,
    ToolValidationError,
    normalize_user_terms,
    validate_get_meal_detail_args,
    validate_search_meals_args,
)


def test_chinese_ingredient_normalizes_to_english_with_source():
    args = normalize_user_terms({"ingredient": "鸡肉"}, source="user_message")
    assert args["ingredient"].value == "chicken"
    assert args["ingredient"].sourceText == "鸡肉"
    assert args["ingredient"].source == "user_message"


def test_non_english_query_is_rejected_before_external_api():
    try:
        validate_search_meals_args(
            {
                "query": NormalizedToolArg(
                    value="鸡肉",
                    sourceText="鸡肉",
                    source="user_message",
                    confidence="high",
                )
            }
        )
    except ToolValidationError as exc:
        assert exc.field == "query"
        assert exc.retryable is True
    else:
        raise AssertionError("Chinese query must not pass Tool validation")


def test_id_must_come_from_candidate_or_tool_result():
    try:
        validate_get_meal_detail_args({"idMeal": "52795", "source": "user_message"})
    except ToolValidationError as exc:
        assert exc.field == "idMeal"
        assert "candidate" in exc.reason
    else:
        raise AssertionError("LLM generated ID must be rejected")
