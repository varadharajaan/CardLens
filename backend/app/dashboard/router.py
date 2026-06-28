"""Dashboard aggregation HTTP endpoints (read-only)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dashboard.schemas import AnomalyList, DashboardOverview, MilestoneList, RewardsSummary
from app.dashboard.service import DashboardService
from app.shared.constants.api_paths import ApiPaths
from app.shared.database.session import get_db
from app.shared.security.deps import get_current_user_id

router = APIRouter(tags=["dashboard"])


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    """Provide a request-scoped :class:`DashboardService`."""
    return DashboardService(db)


@router.get(
    ApiPaths.DASHBOARD_OVERVIEW,
    response_model=DashboardOverview,
    summary="Portfolio overview",
)
def get_overview(
    user_id: UUID = Depends(get_current_user_id),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardOverview:
    """Return a single-call portfolio summary with dues aggregated per billing group."""
    return service.overview(user_id)


@router.get(ApiPaths.REWARDS_SUMMARY, response_model=RewardsSummary, summary="Rewards summary")
def get_rewards_summary(
    user_id: UUID = Depends(get_current_user_id),
    service: DashboardService = Depends(get_dashboard_service),
) -> RewardsSummary:
    """Return portfolio-wide reward totals with a per-format breakdown."""
    return service.rewards_summary(user_id)


@router.get(ApiPaths.MILESTONES, response_model=MilestoneList, summary="Reward milestones")
def get_milestones(
    user_id: UUID = Depends(get_current_user_id),
    service: DashboardService = Depends(get_dashboard_service),
) -> MilestoneList:
    """Return progress toward each configured reward milestone."""
    return service.milestones(user_id)


@router.get(ApiPaths.ANOMALIES, response_model=AnomalyList, summary="Portfolio anomalies")
def get_anomalies(
    user_id: UUID = Depends(get_current_user_id),
    service: DashboardService = Depends(get_dashboard_service),
) -> AnomalyList:
    """Return detected anomalies across the user's latest statements."""
    return service.anomalies(user_id)
