from fastapi import APIRouter

from app.schemas.common import ok

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return ok(data={"status": "up"})

