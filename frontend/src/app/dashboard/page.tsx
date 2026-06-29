"use client";

import { Badge, Donut, ErrorBanner, Loading, ProgressBar, SectionHeader, StatTile, type Tone } from "@/components/ui";
import { IRupee, IGift, ICard, IAlert, ITrophy, ITrend } from "@/components/icons";
import { formatDate, formatMoney, formatNumber } from "@/lib/format";
import { useApi } from "@/lib/hooks";
import type { Anomaly, DashboardOverview, Milestone, RewardsSummary } from "@/lib/types";

const sev = (s: string): Tone => (s === "warning" ? "warn" : s === "info" ? "info" : "danger");

export default function DashboardPage() {
  const overview = useApi<DashboardOverview>("/dashboard/overview");
  const rewards = useApi<RewardsSummary>("/rewards/summary");
  const milestones = useApi<{ items: Milestone[] }>("/milestones");
  const anomalies = useApi<{ items: Anomaly[] }>("/anomalies");

  if (overview.loading) return <Loading label="Loading your portfolio..." />;
  if (overview.error) return <ErrorBanner message={overview.error} />;
  if (!overview.data) return null;
  const o = overview.data;
  const next = milestones.data?.items.find((m) => !m.achieved);

  return (
    <div className="flex flex-col gap-6">
      <div className="card glow relative overflow-hidden">
        <div className="pointer-events-none absolute -right-10 -top-16 h-48 w-48 rounded-full bg-gradient-to-br from-violet-600/40 to-fuchsia-500/10 blur-3xl" />
        <p className="text-sm text-slate-400">Welcome back</p>
        <h2 className="text-2xl font-bold text-white">Your portfolio at a glance</h2>
        <p className="mt-1 text-sm text-slate-400">{o.counts.cards} cards · {o.counts.card_accounts} companion accounts · {o.counts.bank_accounts} bank accounts · {o.counts.statements} statements</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatTile label="Outstanding due" tone="rose" icon={<IRupee className="h-5 w-5" />} value={formatMoney(o.total_outstanding_due, o.currency)} sub={`Min ${formatMoney(o.total_minimum_due, o.currency)} · ${o.billing_groups} groups`} />
        <StatTile label="Reward points" tone="violet" icon={<IGift className="h-5 w-5" />} value={formatNumber(o.total_reward_points)} sub={`Cashback ${formatMoney(o.total_cashback, o.currency)}`} />
        <StatTile label="Cards" tone="sky" icon={<ICard className="h-5 w-5" />} value={formatNumber(o.counts.cards)} sub={`${o.counts.debit_cards} debit cards`} />
        <StatTile label="Nearest due" tone="amber" icon={<ITrend className="h-5 w-5" />} value={o.nearest_due_date ? formatDate(o.nearest_due_date) : "None"} sub={`${o.counts.bank_accounts} bank accounts`} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section className="card">
          <SectionHeader title="Rewards" subtitle="Estimated value across the portfolio" action={rewards.data ? <Badge tone="brand">~{formatMoney(rewards.data.estimated_value_inr, o.currency)}</Badge> : undefined} />
          {rewards.data ? (
            <div className="flex items-center gap-6">
              <Donut pct={next ? next.progress_pct : 100} label={next ? "to next" : "maxed"} />
              <div className="flex-1 space-y-3">
                {rewards.data.by_format.length === 0 ? <p className="text-sm text-slate-400">No reward data yet.</p> : rewards.data.by_format.map((f) => {
                  const tot = rewards.data!.total_reward_points || 1;
                  return (
                    <div key={f.reward_format} className="space-y-1.5">
                      <div className="flex justify-between text-sm"><span className="text-white">{f.reward_format}</span><span className="text-slate-400">{formatNumber(f.reward_points)} pts{f.cashback > 0 ? ` · ${formatMoney(f.cashback, o.currency)}` : ""}</span></div>
                      <ProgressBar pct={(f.reward_points / tot) * 100} />
                    </div>
                  );
                })}
              </div>
            </div>
          ) : <Loading />}
        </section>

        <section className="card">
          <SectionHeader title="Milestones" subtitle="Progress toward reward thresholds" />
          <div className="flex max-h-72 flex-col gap-3 overflow-auto pr-1">
            {milestones.data?.items.map((m) => (
              <div key={m.key} className="space-y-1.5">
                <div className="flex justify-between text-sm"><span className="flex items-center gap-2 text-white">{m.achieved ? <ITrophy className="h-4 w-4 text-amber-300" /> : null}{m.label}</span><span className="text-slate-400">{m.progress_pct.toFixed(0)}%</span></div>
                <ProgressBar pct={m.progress_pct} />
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="card">
        <SectionHeader title="Anomalies" subtitle="Things that may need your attention" />
        {anomalies.data && anomalies.data.items.length === 0 ? <p className="text-sm text-slate-400">All clear. Your portfolio looks healthy.</p> : (
          <div className="grid gap-3 sm:grid-cols-2">
            {anomalies.data?.items.map((a, i) => (
              <div key={i} className="flex items-start gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-rose-500/15 text-rose-300"><IAlert className="h-5 w-5" /></span>
                <div className="min-w-0"><div className="flex items-center gap-2"><Badge tone={sev(a.severity)}>{a.rule}</Badge>{a.amount !== null ? <span className="text-xs text-slate-400">{formatMoney(a.amount, o.currency)}</span> : null}</div><p className="mt-1 text-sm text-slate-200">{a.message}</p></div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
