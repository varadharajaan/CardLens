import type { ReactNode } from "react";

export type Tone = "ok" | "warn" | "danger" | "info" | "muted" | "brand";

const toneMap: Record<Tone, string> = {
  ok: "border-ok/30 bg-ok/10 text-ok",
  warn: "border-warn/30 bg-warn/10 text-warn",
  danger: "border-danger/30 bg-danger/10 text-danger",
  info: "border-info/30 bg-info/10 text-info",
  muted: "border-line bg-white/5 text-muted",
  brand: "border-brand/30 bg-brand/10 text-brand",
};

export function Badge({ children, tone = "muted" }: { children: ReactNode; tone?: Tone }) {
  return <span className={`pill ${toneMap[tone]}`}>{children}</span>;
}

export function ProgressBar({ pct }: { pct: number }) {
  const clamped = Math.max(0, Math.min(100, pct));
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-white/5">
      <div
        className="h-full rounded-full bg-gradient-to-r from-brand to-brand-2 transition-all"
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}

export function StatCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: ReactNode;
  sub?: ReactNode;
}) {
  return (
    <div className="stat-card">
      <span className="text-xs uppercase tracking-wide text-muted">{label}</span>
      <span className="text-2xl font-semibold text-ink">{value}</span>
      {sub ? <span className="text-sm text-muted">{sub}</span> : null}
    </div>
  );
}

export function SectionHeader({
  title,
  subtitle,
  action,
}: {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-4 flex items-end justify-between gap-4">
      <div>
        <h2 className="text-lg font-semibold text-ink">{title}</h2>
        {subtitle ? <p className="text-sm text-muted">{subtitle}</p> : null}
      </div>
      {action}
    </div>
  );
}

export function Loading({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-sm text-muted">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand border-t-transparent" />
      {label}
    </div>
  );
}

export function ErrorBanner({ message }: { message: string }) {
  return <div className="card border-danger/30 bg-danger/10 text-sm text-danger">{message}</div>;
}

export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="card flex flex-col items-center gap-1 py-10 text-center">
      <p className="text-sm font-medium text-ink">{title}</p>
      {hint ? <p className="text-xs text-muted">{hint}</p> : null}
    </div>
  );
}

export function NetworkChip({ network }: { network: string | null }) {
  if (!network) return null;
  return <Badge tone="info">{network}</Badge>;
}

export function StatusChip({ status }: { status: string }) {
  const tone: Tone =
    status === "ACTIVE" ? "ok" : status === "BLOCKED" || status === "CLOSED" ? "danger" : "muted";
  return <Badge tone={tone}>{status}</Badge>;
}
