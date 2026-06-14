from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def health():
    return {"code": 200, "message": "success", "data": {"status": "ok"}}
