import contextlib
from uuid import UUID
from typing import TypeVar, Protocol, Self, Type, Generic, NoReturn

import sqlalchemy as sa
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.pagination import SQLAlchemyModelPaginator
from src.core.repositories.exceptions import RepositoryException
from src.core.repositories.sqla.exceptions import (
    SQLARepositoryObjectNotFoundError,
    BaseSQLAlRepositoryException,
)
from src.core.schemas import UpdateBaseModel, PaginationSchema, PaginatedResponseSchema
from src.core.utils.exceptions import ModelObjectNotFoundException
from src.db.base import Base
from sqlalchemy.exc import (
    OperationalError,
    IntegrityError,
    DataError,
    TimeoutError,
    ProgrammingError,
    InternalError,
    StatementError,
    DBAPIError,
    SQLAlchemyError,
)
from src.core.repositories.sqla.exceptions import (
    SQLARepositoryConnectionError,
    SQLARepositoryIntegrityError,
    SQLARepositoryDataError,
    SQLARepositoryOperationalError,
    SQLARepositoryTimeoutError,
    SQLARepositoryQueryError,
    SQLARepositoryInternalError,
)


ModelType = TypeVar("ModelType", bound=Base, covariant=True)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=UpdateBaseModel)


class SQLAlchemyBaseRepositoryProtocol(
    Protocol[ModelType, ReadSchemaType, CreateSchemaType, UpdateSchemaType]
):
    async def get(self: Self, id: UUID) -> ReadSchemaType | NoReturn: ...

    async def get_or_none(self: Self, id: UUID) -> ReadSchemaType | None | NoReturn: ...

    async def get_by_ids(
        self: Self, ids: list[UUID]
    ) -> list[ReadSchemaType] | NoReturn: ...

    async def create(
        self: Self, create_object: CreateSchemaType
    ) -> ReadSchemaType | NoReturn: ...

    async def bulk_create(
        self: Self, create_objects: list[CreateSchemaType]
    ) -> list[ReadSchemaType] | NoReturn: ...

    async def update(
        self: Self, update_object: UpdateSchemaType
    ) -> ReadSchemaType | NoReturn: ...

    async def bulk_update(
        self: Self, update_objects: list[UpdateSchemaType]
    ) -> None | NoReturn: ...

    async def delete(self: Self, id: UUID) -> bool: ...


class BaseSQLAlchemyRepositoryImpl(
    Generic[ModelType, ReadSchemaType, CreateSchemaType, UpdateSchemaType]
):
    model_type: Type[ModelType]
    read_schema_type: Type[ReadSchemaType]

    def __init__(self: Self, session: AsyncSession):
        self.session = session

    async def get(self: Self, id: UUID) -> ReadSchemaType | NoReturn:
        try:
            async with self.session as session:
                stmt = sa.select(self.model_type).where(self.model_type.id == id)
                item = (await session.execute(stmt)).scalar_one_or_none()
                if item is None:
                    raise SQLARepositoryObjectNotFoundError(
                        f"{self.model_type.__name__} with id: {id} not found"
                    )

                return self.read_schema_type.model_validate(item, from_attributes=True)
        except Exception as e:
            self.handle_errors(e)

    async def get_or_none(self: Self, id: UUID) -> ReadSchemaType | None | NoReturn:
        try:
            with contextlib.suppress(ModelObjectNotFoundException):
                return await self.get(id)

            return None
        except Exception as e:
            self.handle_errors(e)

    async def get_by_ids(
        self: Self, ids: list[UUID]
    ) -> list[ReadSchemaType] | NoReturn:
        try:
            async with self.session as session:
                stmt = sa.select(self.model_type).where(self.model_type.id.in_(ids))
                items = (await session.execute(stmt)).scalars().all()

                return [
                    self.read_schema_type.model_validate(item, from_attributes=True)
                    for item in items
                ]
        except Exception as e:
            self.handle_errors(e)

    async def create(self: Self, data: CreateSchemaType) -> ReadSchemaType | NoReturn:
        try:
            async with self.session as session:
                stmt = (
                    sa.insert(self.model_type)
                    .values(**data.model_dump(exclude={"id"}))
                    .returning(self.model_type)
                )
                item = (await session.execute(stmt)).scalar_one()

                return self.read_schema_type.model_validate(item, from_attributes=True)
        except Exception as e:
            self.handle_errors(e)

    async def bulk_create(
        self: Self, data: list[CreateSchemaType]
    ) -> list[ReadSchemaType] | NoReturn:
        try:
            async with self.session as session:
                stmt = sa.insert(self.model_type).returning(self.model_type)
                items = (
                    await session.scalars(stmt, [x.model_dump() for x in data])
                ).all()

                return [
                    self.read_schema_type.model_validate(item, from_attributes=True)
                    for item in items
                ]
        except Exception as e:
            self.handle_errors(e)

    async def update(self: Self, data: UpdateSchemaType) -> ReadSchemaType | NoReturn:
        try:
            async with self.session as session:
                pk = data.id
                stmt = (
                    sa.update(self.model_type)
                    .where(self.model_type.id == pk)
                    .values(data.model_dump(exclude={"id"}, exclude_unset=True))
                )
                item = (await session.execute(stmt)).scalar_one()
                return self.read_schema_type.model_validate(item, from_attributes=True)
        except Exception as e:
            self.handle_errors(e)

    async def bulk_update(
        self: Self, data: list[UpdateSchemaType]
    ) -> list[ReadSchemaType] | NoReturn:
        try:
            async with self.session as session:
                stmt = sa.update(self.model_type).returning(self.model_type)
                items = (
                    await session.execute(
                        stmt, [x.model_dump(exclude_unset=True) for x in data]
                    )
                ).all()

                return [
                    self.read_schema_type.model_validate(item, from_attributes=True)
                    for item in items
                ]
        except Exception as e:
            self.handle_errors(e)

    async def delete(self: Self, id: UUID) -> None | NoReturn:
        try:
            async with self.session as session:
                stmt = sa.delete(self.model_type).where(self.model_type.id == id)
                await session.execute(stmt)
            return None
        except Exception as e:
            self.handle_errors(e)

    async def get_all_paginated(
        self: Self,
        pagination: PaginationSchema,
        model_paginator_type: Type[SQLAlchemyModelPaginator[ReadSchemaType]],
    ) -> PaginatedResponseSchema[ReadSchemaType] | NoReturn:
        try:
            stmt = sa.select(self.model_type)
            model_paginator = model_paginator_type(self.session)
            return await model_paginator.get_list(
                statement=stmt, page=pagination.page, page_size=pagination.page_size
            )
        except Exception as e:
            self.handle_errors(e)

    @staticmethod
    def handle_errors(e: Exception) -> NoReturn:
        if isinstance(e, OperationalError):
            raise SQLARepositoryOperationalError(f"Database operation error: {str(e)}")
        elif isinstance(e, SQLARepositoryObjectNotFoundError):
            raise e
        elif isinstance(e, IntegrityError):
            raise SQLARepositoryIntegrityError(f"Data integrity violation: {str(e)}")
        elif isinstance(e, DataError):
            raise SQLARepositoryDataError(f"Error in data or its structure: {str(e)}")
        elif isinstance(e, TimeoutError):
            raise SQLARepositoryTimeoutError(f"Query execution timeout: {str(e)}")
        elif isinstance(e, ProgrammingError):
            raise SQLARepositoryQueryError(f"Error executing the query: {str(e)}")
        elif isinstance(e, InternalError):
            raise SQLARepositoryInternalError(f"Internal error: {str(e)}")
        elif isinstance(e, StatementError):
            raise SQLARepositoryQueryError(f"Error in the statement: {str(e)}")
        elif isinstance(e, DBAPIError):
            raise SQLARepositoryConnectionError(f"Database connection error: {str(e)}")
        elif isinstance(e, SQLAlchemyError):
            raise BaseSQLAlRepositoryException(f"Database error: {str(e)}")
        elif isinstance(e, Exception):
            raise RepositoryException(f"Exception of unknown origin: {str(e)}")
