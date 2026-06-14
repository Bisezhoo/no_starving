from app.core.config import Settings


def make_settings(**overrides):
    return Settings(
        OPENROUTER_API_KEY="sk-test",
        OPENROUTER_MODEL="deepseek/deepseek-chat",
        _env_file=None,
        **overrides,
    )


def test_default_agent_budget_and_log_switches():
    settings = make_settings()
    assert settings.agent_max_tool_calls == 6
    assert settings.agent_max_llm_steps == 4
    assert settings.log_full_user_message is False
    assert settings.log_sensitive_external_headers is False
    assert settings.outbound_http_proxy is None
    assert settings.outbound_http_trust_env is True


def test_outbound_http_proxy_can_be_configured():
    settings = make_settings(
        OUTBOUND_HTTP_PROXY="http://127.0.0.1:7890",
        OUTBOUND_HTTP_TRUST_ENV=False,
    )

    assert settings.outbound_http_proxy == "http://127.0.0.1:7890"
    assert settings.outbound_http_trust_env is False


def test_blank_outbound_http_proxy_is_ignored():
    settings = make_settings(OUTBOUND_HTTP_PROXY="  ")

    assert settings.outbound_http_proxy is None


def test_openrouter_key_is_required():
    try:
        Settings(OPENROUTER_API_KEY="", OPENROUTER_MODEL="deepseek/deepseek-chat", _env_file=None)
    except ValueError as exc:
        assert "OPENROUTER_API_KEY" in str(exc)
    else:
        raise AssertionError("empty OpenRouter key must fail")
