from typing import Literal, Optional

from pydantic import BaseModel


class GeneralHeathCheckResponse(BaseModel):
    status: str = "OK"


class ServiceHealthcheckResponseSchema(BaseModel):
    name: str
    status: Literal["OK", "ERROR"]
    response_time: float
    error_message: Optional[str] = None


class ServiceStatusResponseSchema(BaseModel):
    result: list[ServiceHealthcheckResponseSchema]
