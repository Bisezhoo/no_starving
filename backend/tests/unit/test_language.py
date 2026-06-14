from app.domain.language import detect_locale


def test_detect_chinese_and_mixed_language():
    assert detect_locale("我想吃 chicken，配什么 drink") == "zh-CN"
    assert detect_locale("I want a light chicken dinner") == "en-US"
