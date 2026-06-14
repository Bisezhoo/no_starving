import inspect
import time
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field

from app.domain.models import Card, ToolDataResult
from app.domain.tool_args import ToolValidationError


class ToolRunResult(BaseModel):
    id: str
    name: str
    status: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    cards: list[Card] = Field(default_factory=list)
    resultCount: int = 0
    lookupCount: int = 0
    durationMs: int = 0
    error: str | None = None
    retryOf: str | None = None
    validationError: dict[str, Any] | None = None


class ToolRunner:
    def __init__(
        self,
        tools: dict[str, Callable] | None = None,
        validators: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] | None = None,
    ):
        self.tools = tools or {}
        self.validators = validators or {}
        self._counter = 0

    async def run(
        self,
        tool_name: str,
        raw_args: dict[str, Any],
        request_id: str,
        retry_of: str | None = None,
    ) -> ToolRunResult:
        self._counter += 1
        tool_id = f"{request_id}_tool_{self._counter}"
        started = time.perf_counter()

        validator = self.validators.get(tool_name, lambda args: args)
        try:
            args = validator(raw_args)
        except ToolValidationError as exc:
            return ToolRunResult(
                id=tool_id,
                name=tool_name,
                status="validation_failed",
                arguments=raw_args,
                retryOf=retry_of,
                durationMs=_duration_ms(started),
                validationError={
                    "field": exc.field,
                    "reason": exc.reason,
                    "retryable": exc.retryable,
                    "allowedValues": exc.allowed_values,
                },
            )

        tool = self.tools.get(tool_name)
        if tool is None:
            return ToolRunResult(
                id=tool_id,
                name=tool_name,
                status="failed",
                arguments=args,
                retryOf=retry_of,
                durationMs=_duration_ms(started),
                error=f"unknown tool: {tool_name}",
            )

        try:
            result = tool(args)
            if inspect.isawaitable(result):
                result = await result
            if not isinstance(result, ToolDataResult):
                raise TypeError("tool must return ToolDataResult")
            return ToolRunResult(
                id=tool_id,
                name=tool_name,
                status=result.status,
                arguments=args,
                cards=result.cards,
                resultCount=result.resultCount,
                lookupCount=result.lookupCount,
                retryOf=retry_of,
                durationMs=_duration_ms(started),
                error=result.error,
            )
        except Exception as exc:
            return ToolRunResult(
                id=tool_id,
                name=tool_name,
                status="failed",
                arguments=args,
                retryOf=retry_of,
                durationMs=_duration_ms(started),
                error=str(exc),
            )


def _duration_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)
