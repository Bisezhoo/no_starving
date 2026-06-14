import pytest

from app.domain.models import ToolDataResult
from app.domain.tool_args import ToolValidationError
from app.services.tool_runner import ToolRunner


@pytest.mark.asyncio
async def test_tool_runner_wraps_success_result():
    async def fake_tool(args):
        assert args["ingredient"] == "chicken"
        return ToolDataResult(status="success", cards=[], resultCount=0)

    runner = ToolRunner(
        tools={"search_meals": fake_tool},
        validators={"search_meals": lambda args: args},
    )

    result = await runner.run("search_meals", {"ingredient": "chicken"}, request_id="req_1")

    assert result.status == "success"
    assert result.resultCount == 0
    assert result.name == "search_meals"


@pytest.mark.asyncio
async def test_tool_runner_returns_validation_failed_without_calling_tool():
    called = False

    async def fake_tool(args):
        nonlocal called
        called = True
        return ToolDataResult(status="success", cards=[], resultCount=0)

    def fail_validation(args):
        raise ToolValidationError("query", "query must be English", True)

    runner = ToolRunner(
        tools={"search_meals": fake_tool},
        validators={"search_meals": fail_validation},
    )

    result = await runner.run("search_meals", {"query": "鸡肉"}, request_id="req_1")

    assert result.status == "validation_failed"
    assert result.validationError["field"] == "query"
    assert called is False
