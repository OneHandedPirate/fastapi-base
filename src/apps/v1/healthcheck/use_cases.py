import asyncio
from typing import Protocol, Self, Annotated

from fastapi import Depends

from src.apps.v1.healthcheck.services import DBHealthCheckService
from src.apps.v1.healthcheck.services.protocols import BaseHealthCheckServiceProtocol
from src.apps.v1.healthcheck.schemas import (
    ServiceStatusResponseSchema,
)


class HealthCheckUseCaseProtocol(Protocol):
    async def check(self: Self) -> ServiceStatusResponseSchema: ...


class HealthCheckUseCaseImpl(HealthCheckUseCaseProtocol):
    def __init__(
        self,
        *services_to_check: BaseHealthCheckServiceProtocol,
    ) -> None:
        self.services_to_check = services_to_check

    async def check(self: Self) -> ServiceStatusResponseSchema:
        check_results = await asyncio.gather(
            *[service.execute() for service in self.services_to_check]
        )
        return ServiceStatusResponseSchema(result=check_results)


def get_healthcheck_use_case(
    db_check_service: Annotated[
        BaseHealthCheckServiceProtocol, Depends(DBHealthCheckService)
    ],
) -> HealthCheckUseCaseProtocol:
    return HealthCheckUseCaseImpl(db_check_service)
