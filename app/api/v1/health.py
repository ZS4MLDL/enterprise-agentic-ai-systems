"""
/api/v1/health — health check with DB status (Module 04).
Returns degraded status if DB is unreachable rather than crashing.
"""
from fastapi import APIRouter
from app.db.session import check_db_connection
from app.config.settings import get_settings

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
def health():
    db_ok = check_db_connection()
    s = get_settings()
    return {
        "status": "ok" if db_ok else "degraded",
        "mode": s.MODE.value,
        "db": "connected" if db_ok else "unreachable",
    }
