from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.redis import redis_service

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Liveness probe returning 200 OK if service process is running."""
    return {"status": "ok", "service": "ai-english-tutor-backend"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def ready_check(db: AsyncSession = Depends(get_db)):
    """Readiness probe checking database and redis dependencies."""
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "degraded"

    redis_val = await redis_service.get("health_check_ping")
    redis_status = "ok" if redis_service._redis_client is not None else "in_memory_fallback"

    return {
        "status": "ready" if db_status == "ok" else "degraded",
        "database": db_status,
        "redis": redis_status,
    }
