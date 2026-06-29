export type FeatureStatus = "Live" | "MVP" | "Framework";

export interface FeatureSpec {
  id: number;
  slug: string;
  title: string;
  status: FeatureStatus;
  summary: string;
  metrics: string[];
}

export const FEATURES: FeatureSpec[] = [
  { id: 1, slug: "overview-dashboard", title: "Overview dashboard", status: "Live", summary: "Cards, accounts, dues, rewards, milestones, anomalies, and parser health in one executive surface.", metrics: ["Cards detected", "Upcoming dues", "Reward value", "Parser failures"] },
  { id: 2, slug: "card-portfolio", title: "Card portfolio", status: "Live", summary: "Premium grid of cards, companion variants, due context, rewards, and registry match state.", metrics: ["Bank", "Last 4", "Due date", "Registry match"] },
  { id: 3, slug: "card-detail", title: "Individual card page", status: "MVP", summary: "Single-card command center with statement cycle, dues, rewards, annual-fee progress, benefits, anomalies, and history.", metrics: ["Reward balance", "Milestone progress", "Annual fee waiver", "Benefits"] },
  { id: 4, slug: "statement-intelligence", title: "Statement intelligence", status: "Live", summary: "Parsed statement table with due amounts, rewards, confidence, evidence, and parser status.", metrics: ["PDF status", "Due date", "Reward parse", "Evidence"] },
  { id: 5, slug: "reward-tracker", title: "Reward tracker", status: "Live", summary: "Reward points, cashback, estimated value, reward type breakdown, and parser failure awareness.", metrics: ["Total points", "Cashback", "Estimated INR", "Failures"] },
  { id: 6, slug: "milestone-tracker", title: "Milestone tracker", status: "Live", summary: "Milestones, progress percentage, achieved thresholds, and next milestone tracking.", metrics: ["Target", "Progress", "Deadline", "Worth chasing"] },
  { id: 7, slug: "fee-charge-anomalies", title: "Fee and charge anomaly tracker", status: "Live", summary: "Detects large dues, due-soon risk, utilization risk, and extensible fee anomaly rules.", metrics: ["Annual fee", "GST", "Finance charges", "Unusual charges"] },
  { id: 8, slug: "reward-leakage", title: "Reward leakage tracker", status: "Framework", summary: "Flags reward cap misses, expired points, missed milestones, and wrong-card usage patterns.", metrics: ["Wrong card", "Caps", "Expired points", "Missed cashback"] },
  { id: 9, slug: "best-card-recommendation", title: "Best-card recommendation", status: "Framework", summary: "Category-wise recommendation engine for ecommerce, food, fuel, rent, travel, UPI, and offline spend.", metrics: ["Category", "Best card", "Expected reward", "Exclusions"] },
  { id: 10, slug: "card-roi", title: "Card ROI", status: "MVP", summary: "Annual fee, GST, reward value, benefits used, and Keep / Review / Close / Downgrade verdicts.", metrics: ["Annual fee", "Net gain", "Benefits used", "Verdict"] },
  { id: 11, slug: "bank-account-tracker", title: "Bank account tracker", status: "Live", summary: "Bank accounts, balances, debit-card variants, and future salary/charge/debit pattern analytics.", metrics: ["Balance", "Debit cards", "Charges", "Large transfers"] },
  { id: 12, slug: "subscription-tracker", title: "Subscription tracker", status: "Framework", summary: "Recurring charges, inactive subscriptions, duplicate subscriptions, SaaS, OTT, and app-store billing.", metrics: ["Merchant", "Cycle", "Duplicate", "Inactive"] },
  { id: 13, slug: "refund-mismatch", title: "Refund mismatch tracker", status: "Framework", summary: "Tracks expected refunds, statement reconciliation, days pending, and missing credits.", metrics: ["Merchant", "Expected date", "Credited", "Pending days"] },
  { id: 14, slug: "offer-tracker", title: "Offer tracker", status: "Framework", summary: "Parses offer emails and maps bank/card offers to spend categories and expiry windows.", metrics: ["Merchant", "Category", "Expiry", "Matched card"] },
  { id: 15, slug: "benefit-usage", title: "Benefit usage tracker", status: "Framework", summary: "Tracks lounge, vouchers, concierge, hotel, flight, forex, insurance, and roadside benefits.", metrics: ["Benefit", "Quota", "Used", "Expiry"] },
  { id: 16, slug: "community-intelligence", title: "Community intelligence", status: "Framework", summary: "Approved community/search integrations for discussions, updates, devaluations, and reward-rule changes.", metrics: ["Source", "Topic", "Impact", "Confidence"] },
  { id: 17, slug: "document-vault", title: "Document vault", status: "Framework", summary: "Opt-in vault for PDFs, tax certificates, loan/insurance receipts, and searchable document metadata.", metrics: ["Vault enabled", "PDF retained", "Document type", "Retention"] },
  { id: 18, slug: "tax-summary", title: "Tax summary", status: "Framework", summary: "Yearly exports for fees, insurance, medical, education, rent, donations, investments, and GST.", metrics: ["Year", "Deduction type", "Amount", "Export"] },
  { id: 19, slug: "credit-utilization", title: "Credit utilization tracker", status: "MVP", summary: "Total limit, outstanding, card-level utilization, high-utilization warning, and statement-date risk.", metrics: ["Limit", "Outstanding", "Utilization", "Risk"] },
  { id: 20, slug: "payment-behavior", title: "Payment behavior tracker", status: "Framework", summary: "Full vs partial payment, minimum-only risk, auto-debit signals, delay risk, and payment found status.", metrics: ["Bill generated", "Payment found", "Full payment", "Delay risk"] },
  { id: 21, slug: "rule-change-devaluation", title: "Rule-change/devaluation tracker", status: "Framework", summary: "Registry version impact, reward-value drop estimates, notifications, and rule history.", metrics: ["Old value", "New value", "Impact", "Version"] },
  { id: 22, slug: "manual-correction", title: "Manual correction center", status: "Framework", summary: "Fix card detection, bank, last 4, duplicate accounts, parser mistakes, and reward extraction mistakes.", metrics: ["Field", "Old value", "New value", "Audit"] },
  { id: 23, slug: "duplicate-resolver", title: "Duplicate card/account resolver", status: "Framework", summary: "Merge or split same card/account variants from bank, CRED, SaveSage, replacements, and add-ons.", metrics: ["Candidate", "Confidence", "Merge", "Split"] },
  { id: 24, slug: "portfolio-recommendations", title: "Portfolio recommendations", status: "Framework", summary: "Keep, Close, Downgrade, Upgrade, Use More/Less, Chase/Stop milestone decisions.", metrics: ["Action", "Reason", "Confidence", "Savings"] },
  { id: 25, slug: "personal-finance-timeline", title: "Personal finance timeline", status: "Framework", summary: "Chronological feed of salary, statements, rewards, fees, anomalies, refunds, milestones, and payments.", metrics: ["Event", "Source", "Amount", "Confidence"] },
];

export function findFeature(slug: string): FeatureSpec | undefined {
  return FEATURES.find((feature) => feature.slug === slug);
}