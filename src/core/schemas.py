from typing import TypeVar, Generic
from uuid import UUID

from pydantic import BaseModel, PositiveInt


PaginationItem = TypeVar("PaginationItem", bound=BaseModel)


class UpdateBaseModel(BaseModel):
    id: UUID


class PaginationSchema(BaseModel):
    page: PositiveInt
    page_size: PositiveInt


class PaginatedResponseSchema(PaginationSchema, Generic[PaginationItem]):
    total_pages: PositiveInt
    total_items: PositiveInt
    items: list[PaginationItem]
