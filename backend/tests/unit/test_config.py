from app.core.config import Settings


def test_default_agent_budget_and_log_switches():
    settings = Settings(openrouter_api_key="sk-test", openrouter_model="deepseek/deepseek-chat")
    assert settings.agent_max_tool_calls == 6
    assert settings.agent_max_llm_steps == 4
    assert settings.log_full_user_message is False
    assert settings.log_sensitive_external_headers is False


def test_openrouter_key_is_required():
    try:
        Settings(openrouter_api_key="", openrouter_model="deepseek/deepseek-chat")
    except ValueError as exc:
        assert "OPENROUTER_API_KEY" in str(exc)
    else:
        raise AssertionError("empty OpenRouter key must fail")
