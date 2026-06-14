import json
import logging

from app.core.config import Settings
from app.core.logging import log_event, mask_secret, summarize_sensitive_text


def test_sensitive_text_is_summarized_by_default():
    settings = Settings(
        openrouter_api_key="sk-test",
        openrouter_model="deepseek/deepseek-chat",
        log_full_user_message=False,
    )

    summary = summarize_sensitive_text("我想吃牛肉", allow_full=settings.log_full_user_message)

    assert summary == {"present": True, "length": 5}


def test_log_event_does_not_emit_full_user_message_or_source_text_by_default(caplog):
    settings = Settings(
        openrouter_api_key="sk-test",
        openrouter_model="deepseek/deepseek-chat",
        log_full_user_message=False,
        log_full_source_text=False,
    )
    logger = logging.getLogger("tests.logging.default")

    with caplog.at_level(logging.INFO, logger=logger.name):
        log_event(
            logger,
            "chat_request",
            settings=settings,
            fields={
                "userMessage": "我想吃牛肉",
                "sourceText": "牛肉",
                "requestId": "req_1",
            },
        )

    payload = json.loads(caplog.records[0].message)
    assert payload["event"] == "chat_request"
    assert payload["userMessage"] == {"present": True, "length": 5}
    assert payload["sourceText"] == {"present": True, "length": 2}
    assert "我想吃牛肉" not in caplog.text
    assert "牛肉" not in caplog.text


def test_log_event_honors_individual_sensitive_switches(caplog):
    settings = Settings(
        openrouter_api_key="sk-test",
        openrouter_model="deepseek/deepseek-chat",
        log_full_user_message=True,
        log_full_source_text=False,
    )
    logger = logging.getLogger("tests.logging.switch")

    with caplog.at_level(logging.INFO, logger=logger.name):
        log_event(
            logger,
            "chat_request",
            settings=settings,
            fields={"userMessage": "我想吃牛肉", "sourceText": "牛肉"},
        )

    payload = json.loads(caplog.records[0].message)
    assert payload["userMessage"] == "我想吃牛肉"
    assert payload["sourceText"] == {"present": True, "length": 2}


def test_api_key_and_authorization_are_always_masked_even_when_sensitive_headers_enabled(caplog):
    settings = Settings(
        openrouter_api_key="sk-or-v1-secret",
        openrouter_model="deepseek/deepseek-chat",
        log_sensitive_external_headers=True,
    )
    logger = logging.getLogger("tests.logging.headers")

    with caplog.at_level(logging.INFO, logger=logger.name):
        log_event(
            logger,
            "external_request",
            settings=settings,
            fields={
                "apiKey": "sk-or-v1-secret",
                "headers": {"Authorization": "Bearer sk-or-v1-secret", "Content-Type": "application/json"},
            },
        )

    payload = json.loads(caplog.records[0].message)
    assert payload["apiKey"] == mask_secret("sk-or-v1-secret")
    assert payload["headers"]["Authorization"] == "Bearer " + mask_secret("sk-or-v1-secret")
    assert payload["headers"]["Content-Type"] == "application/json"
    assert "sk-or-v1-secret" not in caplog.text
