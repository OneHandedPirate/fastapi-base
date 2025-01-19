from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings
from src.db.mixins.postgres import UUIDPkMixin, CreatedAtMixin, UpdatedAtMixin


class Base(UUIDPkMixin, DeclarativeBase, CreatedAtMixin, UpdatedAtMixin):
    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )
