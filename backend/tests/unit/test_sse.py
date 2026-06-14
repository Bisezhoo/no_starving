from app.core.sse import format_sse


def test_format_sse_escapes_json_payload():
    event = format_sse("delta", {"text": "hello\nworld"})
    assert event.startswith("event: delta\n")
    assert 'data: {"text":"hello\\nworld"}' in event
    assert event.endswith("\n\n")
