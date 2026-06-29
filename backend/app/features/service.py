"""Feature catalog business logic.

This module keeps the 25 prompt features as a typed backend contract. Live/MVP/Framework status is not
a completion claim; it states current implementation depth and gives clients a stable product map.
"""

from __future__ import annotations

from app.features.schemas import FeatureList, FeatureRead
from app.shared.errors.exceptions import NotFoundError

_FEATURES = [
    FeatureRead(
        id=1,
        slug="overview-dashboard",
        title="Overview dashboard",
        status="Live",
        summary="Cards, accounts, dues, rewards, milestones, anomalies, and parser health.",
        metrics=["Cards detected", "Upcoming dues", "Reward value", "Parser failures"],
    ),
    FeatureRead(
        id=2,
        slug="card-portfolio",
        title="Card portfolio",
        status="Live",
        summary="Cards, companion variants, due context, rewards, and registry match state.",
        metrics=["Bank", "Last 4", "Due date", "Registry match"],
    ),
    FeatureRead(
        id=3,
        slug="card-detail",
        title="Individual card page",
        status="MVP",
        summary="Single-card command center with dues, rewards, milestones, benefits, anomalies, and history.",
        metrics=["Reward balance", "Milestone progress", "Annual fee waiver", "Benefits"],
    ),
    FeatureRead(
        id=4,
        slug="statement-intelligence",
        title="Statement intelligence",
        status="Live",
        summary="Parsed statements with dues, rewards, confidence, evidence, and parser status.",
        metrics=["PDF status", "Due date", "Reward parse", "Evidence"],
    ),
    FeatureRead(
        id=5,
        slug="reward-tracker",
        title="Reward tracker",
        status="Live",
        summary="Reward points, cashback, estimated value, breakdown, and parser failure awareness.",
        metrics=["Total points", "Cashback", "Estimated INR", "Failures"],
    ),
    FeatureRead(
        id=6,
        slug="milestone-tracker",
        title="Milestone tracker",
        status="Live",
        summary="Milestones, progress percentage, achieved thresholds, and next milestone tracking.",
        metrics=["Target", "Progress", "Deadline", "Worth chasing"],
    ),
    FeatureRead(
        id=7,
        slug="fee-charge-anomalies",
        title="Fee and charge anomaly tracker",
        status="Live",
        summary="Large dues, due-soon risk, utilization risk, and extensible fee anomaly rules.",
        metrics=["Annual fee", "GST", "Finance charges", "Unusual charges"],
    ),
    FeatureRead(
        id=8,
        slug="reward-leakage",
        title="Reward leakage tracker",
        status="Framework",
        summary="Reward cap misses, expired points, missed milestones, and wrong-card usage patterns.",
        metrics=["Wrong card", "Caps", "Expired points", "Missed cashback"],
    ),
    FeatureRead(
        id=9,
        slug="best-card-recommendation",
        title="Best-card recommendation",
        status="Framework",
        summary="Category-wise recommendations for ecommerce, food, fuel, rent, travel, UPI, and offline spend.",
        metrics=["Category", "Best card", "Expected reward", "Exclusions"],
    ),
    FeatureRead(
        id=10,
        slug="card-roi",
        title="Card ROI",
        status="MVP",
        summary="Annual fee, GST, reward value, benefits used, and portfolio verdict.",
        metrics=["Annual fee", "Net gain", "Benefits used", "Verdict"],
    ),
    FeatureRead(
        id=11,
        slug="bank-account-tracker",
        title="Bank account tracker",
        status="Live",
        summary="Bank accounts, balances, debit variants, and debit-pattern analytics foundation.",
        metrics=["Balance", "Debit cards", "Charges", "Large transfers"],
    ),
    FeatureRead(
        id=12,
        slug="subscription-tracker",
        title="Subscription tracker",
        status="Framework",
        summary="Recurring charges, inactive subscriptions, duplicate subscriptions, and app-store billing.",
        metrics=["Merchant", "Cycle", "Duplicate", "Inactive"],
    ),
    FeatureRead(
        id=13,
        slug="refund-mismatch",
        title="Refund mismatch tracker",
        status="Framework",
        summary="Expected refunds, statement reconciliation, pending days, and missing credits.",
        metrics=["Merchant", "Expected date", "Credited", "Pending days"],
    ),
    FeatureRead(
        id=14,
        slug="offer-tracker",
        title="Offer tracker",
        status="Framework",
        summary="Bank/card offer emails matched to categories and expiry windows.",
        metrics=["Merchant", "Category", "Expiry", "Matched card"],
    ),
    FeatureRead(
        id=15,
        slug="benefit-usage",
        title="Benefit usage tracker",
        status="Framework",
        summary="Lounge, vouchers, concierge, hotel, flight, forex, insurance, and roadside benefits.",
        metrics=["Benefit", "Quota", "Used", "Expiry"],
    ),
    FeatureRead(
        id=16,
        slug="community-intelligence",
        title="Community intelligence",
        status="Framework",
        summary="Approved community/search integrations for discussions, updates, devaluations, and reward-rule changes.",
        metrics=["Source", "Topic", "Impact", "Confidence"],
    ),
    FeatureRead(
        id=17,
        slug="document-vault",
        title="Document vault",
        status="Framework",
        summary="Opt-in vault for PDFs, certificates, receipts, and searchable document metadata.",
        metrics=["Vault enabled", "PDF retained", "Document type", "Retention"],
    ),
    FeatureRead(
        id=18,
        slug="tax-summary",
        title="Tax summary",
        status="Framework",
        summary="Yearly exports for fees, insurance, medical, education, rent, donations, investments, and GST.",
        metrics=["Year", "Deduction type", "Amount", "Export"],
    ),
    FeatureRead(
        id=19,
        slug="credit-utilization",
        title="Credit utilization tracker",
        status="MVP",
        summary="Total limit, outstanding, card-level utilization, warnings, and statement-date risk.",
        metrics=["Limit", "Outstanding", "Utilization", "Risk"],
    ),
    FeatureRead(
        id=20,
        slug="payment-behavior",
        title="Payment behavior tracker",
        status="Framework",
        summary="Full vs partial payment, minimum-only risk, auto-debit signals, delay risk, and payment found status.",
        metrics=["Bill generated", "Payment found", "Full payment", "Delay risk"],
    ),
    FeatureRead(
        id=21,
        slug="rule-change-devaluation",
        title="Rule-change/devaluation tracker",
        status="Framework",
        summary="Registry version impact, reward-value drop estimates, notifications, and rule history.",
        metrics=["Old value", "New value", "Impact", "Version"],
    ),
    FeatureRead(
        id=22,
        slug="manual-correction",
        title="Manual correction center",
        status="Framework",
        summary="Fix card detection, bank, last 4, duplicates, parser mistakes, and reward extraction mistakes.",
        metrics=["Field", "Old value", "New value", "Audit"],
    ),
    FeatureRead(
        id=23,
        slug="duplicate-resolver",
        title="Duplicate card/account resolver",
        status="Framework",
        summary="Merge/split duplicates from bank/CRED/SaveSage/replacement/add-on variants.",
        metrics=["Candidate", "Confidence", "Merge", "Split"],
    ),
    FeatureRead(
        id=24,
        slug="portfolio-recommendations",
        title="Portfolio recommendations",
        status="Framework",
        summary="Keep, Close, Downgrade, Upgrade, Use More/Less, Chase/Stop milestone decisions.",
        metrics=["Action", "Reason", "Confidence", "Savings"],
    ),
    FeatureRead(
        id=25,
        slug="personal-finance-timeline",
        title="Personal finance timeline",
        status="Framework",
        summary="Chronological feed of salary, statements, rewards, fees, anomalies, refunds, milestones, and payments.",
        metrics=["Event", "Source", "Amount", "Confidence"],
    ),
]


class FeatureService:
    """Read-only service for CardLens feature surfaces."""

    def list_features(self) -> FeatureList:
        return FeatureList(
            items=_FEATURES,
            live=sum(1 for item in _FEATURES if item.status == "Live"),
            mvp=sum(1 for item in _FEATURES if item.status == "MVP"),
            framework=sum(1 for item in _FEATURES if item.status == "Framework"),
        )

    def get_feature(self, slug: str) -> FeatureRead:
        for feature in _FEATURES:
            if feature.slug == slug:
                return feature
        raise NotFoundError("Feature not found.")
