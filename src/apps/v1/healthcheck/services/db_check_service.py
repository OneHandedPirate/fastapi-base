import time
from typing import Annotated, Self, Literal


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from fastapi import Depends

from src.apps.v1.healthcheck.schemas import ServiceHealthcheckResponseSchema
from src.apps.v1.healthcheck.services.protocols import BaseHealthCheckServiceProtocol
from src.db.db_service import db_service


class DBHealthCheckService(BaseHealthCheckServiceProtocol):
    def __init__(
        self: Self,
        db_session: Annotated[AsyncSession, Depends(db_service.get_async_session)],
    ) -> None:
        self.db_session = db_session

    async def execute(self: Self) -> ServiceHealthcheckResponseSchema:
        error_message: str | None = None
        start: float = time.perf_counter()
        status: Literal["OK", "ERROR"] = "OK"
        try:
            await self.db_session.execute(text("SELECT 1"))
        except Exception as e:
            status = "ERROR"
            error_message = str(e)
        finally:
            elapsed_time: float = round(time.perf_counter() - start, 5)

        return ServiceHealthcheckResponseSchema(
            name="db",
            status=status,
            response_time=elapsed_time,
            error_message=error_message,
        )
