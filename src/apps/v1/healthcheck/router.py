from typing import Annotated

from fastapi import APIRouter, Depends

from src.apps.v1.healthcheck.schemas import (
    APIResponseSchema,
    ServiceStatusResponseSchema,
)
from src.apps.v1.healthcheck.use_cases import (
    HealthCheckUseCaseProtocol,
    get_healthcheck_use_case,
)


router = APIRouter(prefix="/healthcheck", tags=["healthcheck"])


@router.get("/status", response_model=APIResponseSchema)
async def get_status():
    """
    General API healthcheck endpoint.
    """
    return APIResponseSchema()


@router.get("/service-status", response_model=ServiceStatusResponseSchema)
async def check_services_statuses(
    healthcheck_use_case: Annotated[
        HealthCheckUseCaseProtocol, Depends(get_healthcheck_use_case)
    ],
) -> ServiceStatusResponseSchema:
    """
    Check service statuses.
    If error occurs additionally return error message.
    """
    return await healthcheck_use_case.check()
