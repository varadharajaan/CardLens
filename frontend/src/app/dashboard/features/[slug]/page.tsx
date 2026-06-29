import { notFound } from "next/navigation";
import { Badge, ProgressBar, SectionHeader } from "@/components/ui";
import { FEATURES, findFeature } from "@/lib/features";

export function generateStaticParams() {
  return FEATURES.map((feature) => ({ slug: feature.slug }));
}

export default function FeaturePage({ params }: { params: { slug: string } }) {
  const feature = findFeature(params.slug);
  if (!feature) notFound();
  const progress = feature.status === "Live" ? 100 : feature.status === "MVP" ? 65 : 35;

  return (
    <div className="flex flex-col gap-6">
      <div className="card glow relative overflow-hidden">
        <div className="pointer-events-none absolute -right-12 -top-16 h-52 w-52 rounded-full bg-gradient-to-br from-violet-600/35 to-sky-500/10 blur-3xl" />
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-violet-300">Feature {feature.id} of 25</p>
            <h2 className="mt-1 text-3xl font-bold tracking-tight text-white">{feature.title}</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">{feature.summary}</p>
          </div>
          <Badge tone={feature.status === "Live" ? "ok" : feature.status === "MVP" ? "brand" : "info"}>{feature.status}</Badge>
        </div>
        <div className="mt-6 max-w-xl space-y-2">
          <div className="flex justify-between text-sm text-slate-400"><span>Implementation coverage</span><span>{progress}%</span></div>
          <ProgressBar pct={progress} />
        </div>
      </div>

      <section className="card">
        <SectionHeader title="Tracked signals" subtitle="First-class data hooks for this module" />
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {feature.metrics.map((metric) => (
            <div key={metric} className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <div className="text-sm font-semibold text-white">{metric}</div>
              <p className="mt-1 text-xs leading-5 text-slate-400">Represented in the domain roadmap and ready for ingestion-driven data.</p>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <SectionHeader title="Product behavior" subtitle="How this fits the CardLens intelligence workflow" />
        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4"><div className="text-sm font-semibold text-white">Ingest</div><p className="mt-1 text-xs leading-5 text-slate-400">Mailbox/PDF/registry inputs feed this module through typed APIs.</p></div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4"><div className="text-sm font-semibold text-white">Analyze</div><p className="mt-1 text-xs leading-5 text-slate-400">Rules, parsers, and confidence scoring convert raw signals into insight.</p></div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4"><div className="text-sm font-semibold text-white">Act</div><p className="mt-1 text-xs leading-5 text-slate-400">Dashboard, alerts, and recommendations expose the next best action.</p></div>
        </div>
      </section>
    </div>
  );
}