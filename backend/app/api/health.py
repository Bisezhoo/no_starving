from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def health(request: Request):
    if getattr(request.app.state, "startup_error", None):
        return JSONResponse(
            status_code=503,
            content={"code": 503, "message": "service unavailable", "data": {"status": "unavailable", "reason": "configuration_error"}},
        )
    return {"code": 200, "message": "success", "data": {"status": "ok"}}
