import asyncio
from contextlib import asynccontextmanager


class ConversationBusyError(Exception):
    pass


class ConversationLock:
    def __init__(self):
        self._lock = asyncio.Lock()
        self.request_id: str | None = None

    @property
    def is_locked(self) -> bool:
        return self._lock.locked()

    @asynccontextmanager
    async def acquire(self, request_id: str):
        if self._lock.locked():
            raise ConversationBusyError("current conversation is already processing")
        await self._lock.acquire()
        self.request_id = request_id
        try:
            yield self
        finally:
            self.request_id = None
            self._lock.release()
