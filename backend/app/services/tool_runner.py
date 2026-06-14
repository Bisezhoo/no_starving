import inspect
import logging
import time
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger, log_event, summarize_tool_arguments
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
        settings: Any | None = None,
        logger: logging.Logger | None = None,
    ):
        self.tools = tools or {}
        self.validators = validators or {}
        self.settings = settings
        self.logger = logger or get_logger(__name__)
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
            result = ToolRunResult(
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
            self._log_result(result, request_id)
            return result

        tool = self.tools.get(tool_name)
        if tool is None:
            result = ToolRunResult(
                id=tool_id,
                name=tool_name,
                status="failed",
                arguments=args,
                retryOf=retry_of,
                durationMs=_duration_ms(started),
                error=f"unknown tool: {tool_name}",
            )
            self._log_result(result, request_id)
            return result

        try:
            result = tool(args)
            if inspect.isawaitable(result):
                result = await result
            if not isinstance(result, ToolDataResult):
                raise TypeError("tool must return ToolDataResult")
            run_result = ToolRunResult(
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
            self._log_result(run_result, request_id)
            return run_result
        except Exception as exc:
            result = ToolRunResult(
                id=tool_id,
                name=tool_name,
                status="failed",
                arguments=args,
                retryOf=retry_of,
                durationMs=_duration_ms(started),
                error=str(exc),
            )
            self._log_result(result, request_id)
            return result

    def _log_result(self, result: ToolRunResult, request_id: str) -> None:
        log_event(
            self.logger,
            "tool_run_finished",
            settings=self.settings,
            fields={
                "requestId": request_id,
                "toolId": result.id,
                "name": result.name,
                "status": result.status,
                "arguments": summarize_tool_arguments(result.arguments, self.settings),
                "durationMs": result.durationMs,
                "resultCount": result.resultCount,
                "lookupCount": result.lookupCount,
                "retryOf": result.retryOf,
                "error": result.error,
                "validationError": result.validationError,
            },
        )


def _duration_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)
