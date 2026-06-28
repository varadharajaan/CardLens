"""Offset-based pagination request params and a generic page response envelope."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")

MAX_PAGE_SIZE = 100


class PageParams:
    """FastAPI dependency carrying validated pagination parameters."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="1-based page number"),
        size: int = Query(20, ge=1, le=MAX_PAGE_SIZE, description="page size"),
    ) -> None:
        self.page = page
        self.size = size

    @property
    def offset(self) -> int:
        """Zero-based row offset for the current page."""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Row limit for the current page."""
        return self.size


class Page(BaseModel, Generic[T]):
    """A single page of results plus the metadata needed to render pagination controls."""

    items: list[T]
    page: int
    size: int
    total: int

    @classmethod
    def create(cls, items: Sequence[T], total: int, params: PageParams) -> Page[T]:
        """Build a page envelope from a slice of items and the total row count."""
        return cls(items=list(items), page=params.page, size=params.size, total=total)
