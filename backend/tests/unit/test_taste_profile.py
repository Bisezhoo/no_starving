from app.domain.taste_profile import empty_profile, merge_profile_from_message


def test_no_alcohol_message_sets_hard_filter():
    profile, patch = merge_profile_from_message(empty_profile(), "今天不要酒精，推荐一杯清爽的")
    assert profile.allowAlcohol is False
    assert patch["allowAlcohol"] is False


def test_liked_and_disliked_ingredients_are_deduplicated():
    profile, _ = merge_profile_from_message(empty_profile(), "我不吃牛肉，喜欢鸡肉")
    assert profile.dislikedIngredients == ["beef"]
    assert profile.likedIngredients == ["chicken"]
