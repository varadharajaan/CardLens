"""Dashboard aggregation response schemas (DTOs)."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class PortfolioCounts(BaseModel):
    """Cardinalities across the user's portfolio."""

    cards: int
    card_accounts: int
    bank_accounts: int
    debit_cards: int
    statements: int


class DashboardOverview(BaseModel):
    """A single-call summary of the user's portfolio for the dashboard landing view.

    Dues are aggregated per billing group (a companion card account, or a standalone card) so that
    companion variants sharing one statement and one due are never counted more than once.
    """

    counts: PortfolioCounts
    billing_groups: int
    total_outstanding_due: float
    total_minimum_due: float
    total_reward_points: int
    total_cashback: float
    nearest_due_date: date | None
    currency: str = "INR"


class RewardFormatTotal(BaseModel):
    """Reward totals for one reward type/format bucket."""

    reward_format: str
    reward_points: int
    cashback: float
    statements: int


class RewardsSummary(BaseModel):
    """Portfolio-wide reward totals, plus a per-format breakdown and an estimated INR value."""

    total_reward_points: int
    total_cashback: float
    estimated_value_inr: float
    by_format: list[RewardFormatTotal]


class Milestone(BaseModel):
    """Progress of the portfolio toward one configured reward milestone."""

    key: str
    label: str
    reward_format: str
    threshold: float
    current: float
    progress_pct: float
    achieved: bool


class MilestoneList(BaseModel):
    """The user's milestone progress across all configured thresholds."""

    items: list[Milestone]


class Anomaly(BaseModel):
    """A single detected portfolio anomaly."""

    rule: str
    severity: str
    message: str
    card_name: str
    last4: str
    due_date: date | None = None
    amount: float | None = None


class AnomalyList(BaseModel):
    """Detected anomalies across the user's latest statements."""

    items: list[Anomaly]
