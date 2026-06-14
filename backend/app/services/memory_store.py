import json
import logging
from pathlib import Path
from typing import Any

from app.core.logging import get_logger, log_event
from app.domain.models import AgentMemory, RecommendationRecord, TasteProfile


class MemoryStore:
    PROFILE_FILE = "taste-profile.json"
    HISTORY_FILE = "recommendation-history.json"
    MEMORY_FILE = "agent-memory.json"
    HISTORY_LIMIT = 20

    def __init__(self, data_dir: Path, logger: logging.Logger | None = None):
        self.data_dir = data_dir
        self.logger = logger or get_logger(__name__)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def load_profile(self) -> TasteProfile:
        data = self._read_json(self.data_dir / self.PROFILE_FILE, {})
        try:
            return TasteProfile.model_validate(data)
        except Exception:
            return TasteProfile()

    async def load_history(self) -> list[RecommendationRecord]:
        data = self._read_json(self.data_dir / self.HISTORY_FILE, [])
        if not isinstance(data, list):
            return []
        records: list[RecommendationRecord] = []
        for item in data[-self.HISTORY_LIMIT :]:
            try:
                records.append(RecommendationRecord.model_validate(item))
            except Exception:
                continue
        return records

    async def load_agent_memory(self) -> AgentMemory:
        data = self._read_json(self.data_dir / self.MEMORY_FILE, {})
        try:
            return AgentMemory.model_validate(data)
        except Exception:
            return AgentMemory()

    async def save_all(
        self,
        profile: TasteProfile,
        history: list[RecommendationRecord],
        memory: AgentMemory,
    ) -> list[str]:
        warnings: list[str] = []
        history_to_save = history[-self.HISTORY_LIMIT :]
        payloads = {
            self.PROFILE_FILE: profile.model_dump(mode="json"),
            self.HISTORY_FILE: [record.model_dump(mode="json") for record in history_to_save],
            self.MEMORY_FILE: memory.model_dump(mode="json"),
        }
        for file_name, payload in payloads.items():
            try:
                self._atomic_write(self.data_dir / file_name, payload)
            except Exception as exc:
                warnings.append(f"{file_name} 持久化失败: {exc}")
                log_event(
                    self.logger,
                    "memory_store_write_failed",
                    fields={"fileName": file_name, "errorType": type(exc).__name__, "error": str(exc)},
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
                "memory_store_read_failed",
                fields={"fileName": path.name, "errorType": type(exc).__name__, "error": str(exc)},
                level=logging.WARNING,
            )
            return default

    def _atomic_write(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_name(f"{path.name}.tmp")
        temp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temp_path.replace(path)
