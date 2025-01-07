from fastapi import APIRouter

from .healthcheck.router import router as healthcheck_router


router = APIRouter(
    prefix="/api/v1",
)

router.include_router(healthcheck_router)
