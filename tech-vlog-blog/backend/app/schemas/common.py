from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "OK"
    data: Optional[T] = None


def ok(data: Any = None, message: str = "OK", code: int = 0) -> dict[str, Any]:
    return {"code": code, "message": message, "data": data}


def error(message: str = "Error", code: int = 1, data: Any = None) -> dict[str, Any]:
    return {"code": code, "message": message, "data": data}

