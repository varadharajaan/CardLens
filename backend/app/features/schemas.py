"""Feature catalog DTOs."""

from __future__ import annotations

from pydantic import BaseModel


class FeatureRead(BaseModel):
    """A CardLens product feature surface from the autonomous build prompt."""

    id: int
    slug: str
    title: str
    status: str
    summary: str
    metrics: list[str]


class FeatureList(BaseModel):
    """All feature surfaces plus high-level coverage counts."""

    items: list[FeatureRead]
    live: int
    mvp: int
    framework: int
