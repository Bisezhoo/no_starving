from fastapi.responses import JSONResponse


class BusinessException(Exception):
    def __init__(self, code: int, message: str, data: dict | None = None):
        self.code = code
        self.message = message
        self.data = data or {}


def error_response(code: int, message: str, data: dict | None = None) -> JSONResponse:
    return JSONResponse(status_code=code, content={"code": code, "message": message, "data": data or {}})
