import pytest

from app.services.conversation_lock import ConversationLock


@pytest.mark.asyncio
async def test_lock_releases_after_exception():
    lock = ConversationLock()
    try:
        async with lock.acquire("req_1"):
            assert lock.is_locked is True
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert lock.is_locked is False
