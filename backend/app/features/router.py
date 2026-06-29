"""Feature catalog endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.features.schemas import FeatureList, FeatureRead
from app.features.service import FeatureService

router = APIRouter(prefix="/features", tags=["features"])
_service = FeatureService()


@router.get("", response_model=FeatureList, summary="List CardLens feature surfaces")
def list_features() -> FeatureList:
    return _service.list_features()


@router.get("/{slug}", response_model=FeatureRead, summary="Get one CardLens feature surface")
def get_feature(slug: str) -> FeatureRead:
    return _service.get_feature(slug)
