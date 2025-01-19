from typing import Any, Generic, Optional, Type, TypeVar
from uuid import UUID

from fastapi import HTTPException, status

from src.db.base import Base


ModelType = TypeVar("ModelType", bound=Base)


class ModelObjectNotFoundException(HTTPException, Generic[ModelType]):
    """
    Exception in case of model object not found
    """

    def __init__(
        self,
        model: Type[ModelType],
        model_id: UUID,
        headers: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unable to find the {model.__name__} with id {model_id}.",
            headers=headers,
        )
