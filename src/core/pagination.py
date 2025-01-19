from typing import Type, Generic, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
import sqlalchemy as sa

from src.core.schemas import PaginatedResponseSchema, PaginationItem


class SQLAlchemyModelPaginator(Generic[PaginationItem]):
    pagination_item_type: Type[PaginationItem]

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def get_list(
        self, statement: Select[tuple[Any]], page: int, page_size: int
    ) -> PaginatedResponseSchema[PaginationItem]:
        offset = (page - 1) * page_size

        async with self.session as s:
            count = (
                await s.execute(
                    sa.select(sa.func.count()).select_from(statement.subquery())
                )
            ).scalar_one()

            statement_items = statement.limit(page_size).offset(offset)
            models = (await s.execute(statement_items)).scalars().all()

        total_pages = (count + page_size - 1) // page_size

        return PaginatedResponseSchema(
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_items=count,
            items=[self.pagination_item_type.model_validate(model) for model in models],
        )
