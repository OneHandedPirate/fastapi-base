from typing import Protocol, Self

from src.apps.v1.healthcheck.schemas import ServiceHealthcheckResponseSchema


class BaseHealthCheckServiceProtocol(Protocol):
    async def execute(self: Self) -> ServiceHealthcheckResponseSchema: ...
