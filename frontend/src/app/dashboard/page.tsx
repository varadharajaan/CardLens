"use client";

import {
  Badge,
  ErrorBanner,
  Loading,
  ProgressBar,
  SectionHeader,
  StatCard,
  type Tone,
} from "@/components/ui";
import { formatDate, formatMoney, formatNumber } from "@/lib/format";
import { useApi } from "@/lib/hooks";
import type { Anomaly, DashboardOverview, Milestone, RewardsSummary } from "@/lib/types";

function severityTone(severity: string): Tone {
  if (severity === "warning") return "warn";
  if (severity === "info") return "info";
  return "danger";
}

export default function DashboardPage() {
  const overview = useApi<DashboardOverview>("/dashboard/overview");
  const rewards = useApi<RewardsSummary>("/rewards/summary");
  const milestones = useApi<{ items: Milestone[] }>("/milestones");
  const anomalies = useApi<{ items: Anomaly[] }>("/anomalies");

  if (overview.loading) return <Loading label="Loading your portfolio..." />;
  if (overview.error) return <ErrorBanner message={overview.error} />;
  if (!overview.data) return null;
  const o = overview.data;

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Outstanding due"
          value={formatMoney(o.total_outstanding_due, o.currency)}
          sub={`Minimum ${formatMoney(o.total_minimum_due, o.currency)} across ${o.billing_groups} billing groups`}
        />
        <StatCard
          label="Reward points"
          value={formatNumber(o.total_reward_points)}
          sub={`Cashback ${formatMoney(o.total_cashback, o.currency)}`}
        />
        <StatCard
          label="Cards"
          value={formatNumber(o.counts.cards)}
          sub={`${o.counts.card_accounts} companion accounts`}
        />
        <StatCard
          label="Nearest due"
          value={o.nearest_due_date ? formatDate(o.nearest_due_date) : "None"}
          sub={`${o.counts.bank_accounts} bank accounts, ${o.counts.debit_cards} debit cards`}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section className="card">
          <SectionHeader
            title="Rewards"
            subtitle="Latest statement per billing group"
            action={
              rewards.data ? (
                <Badge tone="brand">
                  ~{formatMoney(rewards.data.estimated_value_inr, o.currency)} value
                </Badge>
              ) : undefined
            }
          />
          {rewards.loading ? <Loading /> : null}
          {rewards.error ? <ErrorBanner message={rewards.error} /> : null}
          {rewards.data ? (
            <div className="flex flex-col gap-3">
              {rewards.data.by_format.length === 0 ? (
                <p className="text-sm text-muted">No reward data yet.</p>
              ) : (
                rewards.data.by_format.map((f) => {
                  const total = rewards.data!.total_reward_points || 1;
                  const pct = (f.reward_points / total) * 100;
                  return (
                    <div key={f.reward_format} className="flex flex-col gap-1.5">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-ink">{f.reward_format}</span>
                        <span className="text-muted">
                          {formatNumber(f.reward_points)} pts
                          {f.cashback > 0 ? ` / ${formatMoney(f.cashback, o.currency)}` : ""}
                        </span>
                      </div>
                      <ProgressBar pct={pct} />
                    </div>
                  );
                })
              )}
            </div>
          ) : null}
        </section>

        <section className="card">
          <SectionHeader title="Milestones" subtitle="Progress toward reward thresholds" />
          {milestones.loading ? <Loading /> : null}
          {milestones.error ? <ErrorBanner message={milestones.error} /> : null}
          {milestones.data ? (
            <div className="flex max-h-72 flex-col gap-3 overflow-auto pr-1">
              {milestones.data.items.map((m) => (
                <div key={m.key} className="flex flex-col gap-1.5">
                  <div className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-2 text-ink">
                      {m.label}
                      {m.achieved ? <Badge tone="ok">done</Badge> : null}
                    </span>
                    <span className="text-muted">{m.progress_pct.toFixed(0)}%</span>
                  </div>
                  <ProgressBar pct={m.progress_pct} />
                </div>
              ))}
            </div>
          ) : null}
        </section>
      </div>

      <section className="card">
        <SectionHeader title="Anomalies" subtitle="Things that may need your attention" />
        {anomalies.loading ? <Loading /> : null}
        {anomalies.error ? <ErrorBanner message={anomalies.error} /> : null}
        {anomalies.data ? (
          anomalies.data.items.length === 0 ? (
            <p className="text-sm text-muted">Nothing flagged. Your portfolio looks healthy.</p>
          ) : (
            <ul className="flex flex-col divide-y divide-line">
              {anomalies.data.items.map((a, i) => (
                <li key={`${a.rule}-${i}`} className="flex items-center justify-between gap-3 py-3">
                  <div className="flex items-center gap-3">
                    <Badge tone={severityTone(a.severity)}>{a.rule}</Badge>
                    <span className="text-sm text-ink">{a.message}</span>
                  </div>
                  {a.amount !== null ? (
                    <span className="shrink-0 text-sm text-muted">
                      {formatMoney(a.amount, o.currency)}
                    </span>
                  ) : null}
                </li>
              ))}
            </ul>
          )
        ) : null}
      </section>
    </div>
  );
}
