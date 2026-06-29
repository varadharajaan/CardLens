import Link from "next/link";
import { FEATURES } from "@/lib/features";
import { Badge, ProgressBar, SectionHeader } from "@/components/ui";

const statusTone = (status: string) => (status === "Live" ? "ok" : status === "MVP" ? "brand" : "info") as const;
const statusProgress = (status: string) => (status === "Live" ? 100 : status === "MVP" ? 65 : 35);

export default function IntelligencePage() {
  const live = FEATURES.filter((feature) => feature.status === "Live").length;
  const mvp = FEATURES.filter((feature) => feature.status === "MVP").length;
  const framework = FEATURES.filter((feature) => feature.status === "Framework").length;

  return (
    <div className="flex flex-col gap-6">
      <div className="card glow relative overflow-hidden">
        <div className="pointer-events-none absolute -right-16 -top-24 h-64 w-64 rounded-full bg-gradient-to-br from-violet-600/35 to-sky-400/10 blur-3xl" />
        <p className="text-sm font-medium text-violet-300">Product operating system</p>
        <h2 className="mt-1 text-3xl font-bold tracking-tight text-white">All 25 CardLens intelligence modules</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
          Every prompt feature is represented as a product surface. Live modules are data-backed today;
          MVP and Framework modules have typed UI surfaces and extension points for ingestion rules, parser signals, recommendations, and corrections.
        </p>
        <div className="mt-6 grid max-w-2xl grid-cols-3 gap-3">
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4"><div className="text-2xl font-bold text-white">{live}</div><div className="text-xs text-slate-400">Live</div></div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4"><div className="text-2xl font-bold text-white">{mvp}</div><div className="text-xs text-slate-400">MVP</div></div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4"><div className="text-2xl font-bold text-white">{framework}</div><div className="text-xs text-slate-400">Framework</div></div>
        </div>
      </div>

      <section className="card">
        <SectionHeader title="Coverage map" subtitle="Feature-by-feature architecture coverage from the CardLens prompt" />
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {FEATURES.map((feature) => (
            <Link key={feature.slug} href={`/dashboard/features/${feature.slug}`} className="group rounded-3xl border border-white/10 bg-white/[0.03] p-4 transition hover:-translate-y-0.5 hover:bg-white/[0.06]">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs font-semibold text-violet-300">{String(feature.id).padStart(2, "0")}</div>
                  <h3 className="mt-1 text-sm font-semibold text-white group-hover:text-violet-200">{feature.title}</h3>
                </div>
                <Badge tone={statusTone(feature.status)}>{feature.status}</Badge>
              </div>
              <p className="mt-3 line-clamp-3 min-h-[3.75rem] text-xs leading-5 text-slate-400">{feature.summary}</p>
              <div className="mt-4 space-y-1.5">
                <div className="flex justify-between text-[11px] text-slate-400"><span>coverage</span><span>{statusProgress(feature.status)}%</span></div>
                <ProgressBar pct={statusProgress(feature.status)} />
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}