import type { ReactNode } from "react";

export type Tone = "violet" | "sky" | "emerald" | "amber" | "rose" | "ok" | "warn" | "danger" | "info" | "muted" | "brand";

const chip: Record<string, string> = {
  ok: "text-emerald-300 bg-emerald-500/10 border-emerald-400/20",
  warn: "text-amber-300 bg-amber-500/10 border-amber-400/20",
  danger: "text-rose-300 bg-rose-500/10 border-rose-400/20",
  info: "text-sky-300 bg-sky-500/10 border-sky-400/20",
  muted: "text-slate-300 bg-white/5 border-white/10",
  brand: "text-violet-300 bg-violet-500/10 border-violet-400/20",
};

export function Badge({ children, tone = "muted" }: { children: ReactNode; tone?: Tone }) {
  return <span className={`pill ${chip[tone] ?? chip.muted}`}>{children}</span>;
}

export function ProgressBar({ pct }: { pct: number }) {
  const v = Math.max(0, Math.min(100, pct));
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-white/[0.06]">
      <div className="h-full rounded-full bg-gradient-to-r from-violet-500 via-fuchsia-500 to-sky-400" style={{ width: `${v}%` }} />
    </div>
  );
}

const grad: Record<string, string> = {
  violet: "from-violet-600/30 to-violet-500/5 text-violet-300",
  sky: "from-sky-600/30 to-sky-500/5 text-sky-300",
  emerald: "from-emerald-600/30 to-emerald-500/5 text-emerald-300",
  amber: "from-amber-600/30 to-amber-500/5 text-amber-300",
  rose: "from-rose-600/30 to-rose-500/5 text-rose-300",
};

export function StatTile({ label, value, sub, icon, tone = "violet" }: { label: string; value: ReactNode; sub?: ReactNode; icon?: ReactNode; tone?: Tone }) {
  return (
    <div className="card glow group relative overflow-hidden transition hover:-translate-y-0.5">
      <div className={`pointer-events-none absolute -right-8 -top-10 h-28 w-28 rounded-full bg-gradient-to-br ${grad[tone] ?? grad.violet} blur-2xl`} />
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400">{label}</span>
        <span className={`grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br ${grad[tone] ?? grad.violet}`}>{icon}</span>
      </div>
      <span className="mt-2 block text-3xl font-bold tracking-tight text-white">{value}</span>
      {sub ? <span className="text-sm text-slate-400">{sub}</span> : null}
    </div>
  );
}

export function Donut({ pct, label }: { pct: number; label?: string }) {
  const v = Math.max(0, Math.min(100, pct));
  return (
    <div className="relative h-28 w-28">
      <div className="absolute inset-0 rounded-full" style={{ background: `conic-gradient(#a855f7 ${v * 3.6}deg, rgba(255,255,255,0.07) 0deg)` }} />
      <div className="absolute inset-[10px] grid place-items-center rounded-full shadow-inner" style={{ background: "rgb(var(--donut-bg))" }}>
        <div className="text-center">
          <div className="text-xl font-bold" style={{ color: "rgb(var(--donut-text))" }}>{Math.round(v)}%</div>
          {label ? <div className="text-[10px]" style={{ color: "rgb(var(--donut-muted))" }}>{label}</div> : null}
        </div>
      </div>
    </div>
  );
}

export function SectionHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="mb-4 flex items-end justify-between gap-4">
      <div>
        <h2 className="text-lg font-semibold text-white">{title}</h2>
        {subtitle ? <p className="text-sm text-slate-400">{subtitle}</p> : null}
      </div>
      {action}
    </div>
  );
}

export function Loading({ label = "Loading..." }: { label?: string }) {
  return <div className="flex items-center gap-3 text-sm text-slate-400"><span className="h-4 w-4 animate-spin rounded-full border-2 border-violet-400 border-t-transparent" />{label}</div>;
}
export function ErrorBanner({ message }: { message: string }) {
  return <div className="card border-rose-400/20 bg-rose-500/10 text-sm text-rose-200">{message}</div>;
}
export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return <div className="card flex flex-col items-center gap-1 py-12 text-center"><p className="text-sm font-medium text-white">{title}</p>{hint ? <p className="text-xs text-slate-400">{hint}</p> : null}</div>;
}
export function NetworkChip({ network }: { network: string | null }) {
  return network ? <Badge tone="info">{network}</Badge> : null;
}
export function StatusChip({ status }: { status: string }) {
  return <Badge tone={status === "ACTIVE" ? "ok" : status === "BLOCKED" || status === "CLOSED" ? "danger" : "muted"}>{status}</Badge>;
}
export const StatCard = StatTile;
