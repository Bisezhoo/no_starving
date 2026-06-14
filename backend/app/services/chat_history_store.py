import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app.core.logging import get_logger, log_event
from app.domain.models import AssistantChatHistoryMessage, ChatHistoryMessage, UserChatHistoryMessage


class ChatHistoryStore:
    HISTORY_FILE = "chat-history.json"
    MESSAGE_LIMIT = 60
    RETENTION_HOURS = 24

    def __init__(self, data_dir: Path | str, logger: logging.Logger | None = None):
        self.data_dir = Path(data_dir)
        self.logger = logger or get_logger(__name__)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def load_messages(self, now: datetime | None = None) -> list[ChatHistoryMessage]:
        data = self._read_json(self.data_dir / self.HISTORY_FILE, [])
        if not isinstance(data, list):
            return []
        messages: list[ChatHistoryMessage] = []
        for item in data:
            message = self._parse_message(item)
            if message is not None:
                messages.append(message)
        return self._trim(messages, now or datetime.now(UTC))

    async def append_messages(
        self,
        messages: list[ChatHistoryMessage],
        now: datetime | None = None,
    ) -> list[str]:
        warnings: list[str] = []
        current = await self.load_messages(now=now)
        trimmed = self._trim([*current, *messages], now or datetime.now(UTC))
        payload = [message.model_dump(mode="json") for message in trimmed]
        try:
            self._atomic_write(self.data_dir / self.HISTORY_FILE, payload)
        except Exception as exc:
            warnings.append(f"{self.HISTORY_FILE} 持久化失败: {exc}")
            log_event(
                self.logger,
                "chat_history_write_failed",
                fields={"fileName": self.HISTORY_FILE, "errorType": type(exc).__name__, "error": str(exc)},
                level=logging.ERROR,
            )
        return warnings

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            log_event(
                self.logger,
                "chat_history_read_failed",
                fields={"fileName": path.name, "errorType": type(exc).__name__, "error": str(exc)},
                level=logging.WARNING,
            )
            return default

    def _parse_message(self, item: Any) -> ChatHistoryMessage | None:
        if not isinstance(item, dict):
            return None
        try:
            if item.get("role") == "user":
                return UserChatHistoryMessage.model_validate(item)
            if item.get("role") == "assistant":
                return AssistantChatHistoryMessage.model_validate(item)
        except Exception:
            return None
        return None

    def _trim(self, messages: list[ChatHistoryMessage], now: datetime) -> list[ChatHistoryMessage]:
        cutoff = now - timedelta(hours=self.RETENTION_HOURS)
        recent = [
            message
            for message in messages
            if (created_at := self._parse_created_at(message.createdAt)) is not None and created_at >= cutoff
        ]
        return recent[-self.MESSAGE_LIMIT :]

    def _parse_created_at(self, value: str) -> datetime | None:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)

    def _atomic_write(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_name(f"{path.name}.tmp")
        temp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temp_path.replace(path)
