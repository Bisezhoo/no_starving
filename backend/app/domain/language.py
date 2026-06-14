def detect_locale(message: str) -> str:
    has_cjk = any("\u4e00" <= ch <= "\u9fff" for ch in message)
    return "zh-CN" if has_cjk else "en-US"
