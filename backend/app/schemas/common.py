from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Envoltorio estandar de paginacion para todos los endpoints GET list."""

    items: list[T]
    total: int
    skip: int
    limit: int
