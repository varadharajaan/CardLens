"""Dashboard aggregation business logic: overview, rewards, milestones, and anomalies.

Every aggregate is derived from the latest statement per *billing group*, where a billing group is a
companion card account (when ``account_id`` is set) or otherwise a standalone card. This guarantees
that companion variants sharing one statement and one due are never double-counted.
"""

from __future__ import annotations

from datetime import date, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.dashboard.repository import DashboardRepository
from app.dashboard.schemas import (
    Anomaly,
    AnomalyList,
    DashboardOverview,
    Milestone,
    MilestoneList,
    PortfolioCounts,
    RewardFormatTotal,
    RewardsSummary,
)
from app.shared.config.data_loader import get_data_loader
from app.statements.models import Statement

_UNKNOWN_FORMAT = "OTHER"


def _billing_key(statement: Statement, card_to_account: dict[UUID, UUID]) -> str:
    """Return the grouping key that collapses companion variants onto one billing group.

    A statement recorded directly against a companion account groups by that account. A statement
    recorded against an individual variant card still groups by the card's account when it has one, so
    companion dues are never double-counted regardless of how the statement was attached.
    """
    account_id = statement.account_id
    if account_id is None and statement.card_id is not None:
        account_id = card_to_account.get(statement.card_id)
    if account_id is not None:
        return f"account:{account_id}"
    if statement.card_id is not None:
        return f"card:{statement.card_id}"
    return f"statement:{statement.id}"


class DashboardService:
    """Computes portfolio aggregates for a single user from the latest statement per billing group."""

    def __init__(self, db: Session) -> None:
        self._repo = DashboardRepository(db)
        self._data = get_data_loader()

    def _latest_per_group(self, statements: list[Statement], card_to_account: dict[UUID, UUID]) -> list[Statement]:
        """Return the newest statement for each billing group (input must be newest-first)."""
        seen: dict[str, Statement] = {}
        for statement in statements:
            seen.setdefault(_billing_key(statement, card_to_account), statement)
        return list(seen.values())

    def overview(self, user_id: UUID) -> DashboardOverview:
        """Return a single-call portfolio summary with dues aggregated per billing group."""
        counts = self._repo.counts(user_id)
        card_to_account = self._repo.card_to_account(user_id)
        latest = self._latest_per_group(self._repo.statements(user_id), card_to_account)
        today = date.today()
        upcoming = [s.due_date for s in latest if s.due_date is not None and s.due_date >= today]
        return DashboardOverview(
            counts=PortfolioCounts(**counts),
            billing_groups=len(latest),
            total_outstanding_due=round(sum(s.total_due or 0.0 for s in latest), 2),
            total_minimum_due=round(sum(s.minimum_due or 0.0 for s in latest), 2),
            total_reward_points=sum(s.reward_points_closing or 0 for s in latest),
            total_cashback=round(sum(s.cashback_earned or 0.0 for s in latest), 2),
            nearest_due_date=min(upcoming) if upcoming else None,
        )

    def rewards_summary(self, user_id: UUID) -> RewardsSummary:
        """Return portfolio-wide reward totals with a per-format breakdown and estimated INR value."""
        card_to_account = self._repo.card_to_account(user_id)
        latest = self._latest_per_group(self._repo.statements(user_id), card_to_account)
        points_by_format: dict[str, int] = {}
        cashback_by_format: dict[str, float] = {}
        count_by_format: dict[str, int] = {}
        for s in latest:
            fmt = s.reward_type or _UNKNOWN_FORMAT
            points_by_format[fmt] = points_by_format.get(fmt, 0) + (s.reward_points_closing or 0)
            cashback_by_format[fmt] = cashback_by_format.get(fmt, 0.0) + (s.cashback_earned or 0.0)
            count_by_format[fmt] = count_by_format.get(fmt, 0) + 1
        by_format = [
            RewardFormatTotal(
                reward_format=fmt,
                reward_points=points_by_format[fmt],
                cashback=round(cashback_by_format[fmt], 2),
                statements=count_by_format[fmt],
            )
            for fmt in sorted(points_by_format)
        ]
        total_points = sum(t.reward_points for t in by_format)
        total_cashback = round(sum(t.cashback for t in by_format), 2)
        estimated = round(total_points * self._data.reward_value_per_point() + total_cashback, 2)
        return RewardsSummary(
            total_reward_points=total_points,
            total_cashback=total_cashback,
            estimated_value_inr=estimated,
            by_format=by_format,
        )

    def milestones(self, user_id: UUID) -> MilestoneList:
        """Return progress toward each configured reward milestone."""
        summary = self.rewards_summary(user_id)
        current_by_format = {
            "REWARD_POINTS": float(summary.total_reward_points),
            "CASHBACK": summary.total_cashback,
        }
        items: list[Milestone] = []
        for fmt, rules in self._data.reward_milestones().items():
            current = current_by_format.get(fmt, 0.0)
            for rule in rules:
                achieved = current >= rule.threshold
                pct = 100.0 if achieved else round(current / rule.threshold * 100, 1)
                items.append(
                    Milestone(
                        key=rule.key,
                        label=rule.label,
                        reward_format=fmt,
                        threshold=rule.threshold,
                        current=round(current, 2),
                        progress_pct=pct,
                        achieved=achieved,
                    )
                )
        return MilestoneList(items=items)

    def anomalies(self, user_id: UUID) -> AnomalyList:
        """Return detected anomalies across the user's latest statements, applying config thresholds."""
        all_statements = self._repo.statements(user_id)
        card_to_account = self._repo.card_to_account(user_id)
        latest = self._latest_per_group(all_statements, card_to_account)
        rules = self._data.anomaly_rules()
        limits = self._repo.credit_limit_by_account(user_id)
        today = date.today()
        series_by_group: dict[str, list[Statement]] = {}
        for s in all_statements:
            series_by_group.setdefault(_billing_key(s, card_to_account), []).append(s)

        items: list[Anomaly] = []
        for s in latest:
            due = s.total_due or 0.0
            tail = f"{s.card_name} (****{s.last4})"
            if (
                s.due_date is not None
                and due > 0
                and today <= s.due_date <= today + timedelta(days=rules.due_soon_days)
            ):
                items.append(
                    Anomaly(
                        rule="DUE_SOON",
                        severity="warning",
                        message=f"{tail} is due on {s.due_date.isoformat()} with Rs {due:,.0f} outstanding.",
                        card_name=s.card_name,
                        last4=s.last4,
                        due_date=s.due_date,
                        amount=due,
                    )
                )
            if due >= rules.large_due_amount:
                items.append(
                    Anomaly(
                        rule="LARGE_DUE",
                        severity="warning",
                        message=f"{tail} has an unusually large total due of Rs {due:,.0f}.",
                        card_name=s.card_name,
                        last4=s.last4,
                        amount=due,
                    )
                )
            limit = limits.get(s.account_id) if s.account_id is not None else None
            if limit is not None and limit > 0:
                utilization = due / limit * 100
                if utilization >= rules.high_utilization_pct:
                    items.append(
                        Anomaly(
                            rule="HIGH_UTILIZATION",
                            severity="warning",
                            message=f"{tail} is at {utilization:.0f}% of its credit limit.",
                            card_name=s.card_name,
                            last4=s.last4,
                            amount=due,
                        )
                    )
            series = series_by_group.get(_billing_key(s, card_to_account), [])
            if len(series) >= 2:
                drop = (series[1].reward_points_closing or 0) - (s.reward_points_closing or 0)
                if drop >= rules.reward_drop_points:
                    items.append(
                        Anomaly(
                            rule="REWARD_DROP",
                            severity="info",
                            message=f"{tail} reward balance fell by {drop:,} points versus the prior statement.",
                            card_name=s.card_name,
                            last4=s.last4,
                            amount=float(drop),
                        )
                    )
        return AnomalyList(items=items)
