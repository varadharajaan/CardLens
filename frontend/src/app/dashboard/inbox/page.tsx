"use client";

import { useState } from "react";
import { ErrorBanner, SectionHeader, StatTile } from "@/components/ui";
import { IMail, IInbox, IRepeat, IShield } from "@/components/icons";
import { apiFetch } from "@/lib/api";

interface ConnectResponse { authorize_url: string; dry_run: boolean }
interface ScanResult { scanned: number; statements_ingested: number; dry_run: boolean }

export default function InboxPage() {
  const [busy, setBusy] = useState(false);
  const [scan, setScan] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function connect() {
    setBusy(true);
    setError(null);
    try {
      const result = await apiFetch<ConnectResponse>("/mail/accounts/connect", { method: "POST" });
      if (!result.dry_run) window.location.href = result.authorize_url;
      else setScan({ scanned: 0, statements_ingested: 0, dry_run: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not start Gmail consent");
    } finally {
      setBusy(false);
    }
  }

  async function runScan() {
    setBusy(true);
    setError(null);
    try {
      setScan(await apiFetch<ScanResult>("/ingestion/scan", { method: "POST" }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Mailbox scan failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="card glow relative overflow-hidden">
        <div className="pointer-events-none absolute -right-16 -top-20 h-56 w-56 rounded-full bg-gradient-to-br from-sky-500/30 to-violet-500/10 blur-3xl" />
        <p className="text-sm font-medium text-sky-300">Gmail onboarding</p>
        <h2 className="mt-1 text-3xl font-bold tracking-tight text-white">Connect Gmail, scan statements, populate CardLens</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
          OAuth only. No Gmail passwords. Tokens are encrypted. Dry-run mode ingests sample statement data until Google OAuth credentials are configured.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <button className="btn" type="button" onClick={connect} disabled={busy}>Connect Gmail</button>
          <button className="rounded-2xl border border-white/10 px-5 py-3 text-sm font-semibold text-slate-300 hover:bg-white/10 hover:text-white" type="button" onClick={runScan} disabled={busy}>Run pull scan</button>
        </div>
      </div>

      {error ? <ErrorBanner message={error} /> : null}

      <div className="grid gap-4 md:grid-cols-4">
        <StatTile label="Consent" value="OAuth" sub="read-only Gmail scope" icon={<IMail className="h-5 w-5" />} tone="sky" />
        <StatTile label="Pull scan" value={scan ? String(scan.scanned) : "Ready"} sub="last 24h mailbox window" icon={<IInbox className="h-5 w-5" />} tone="violet" />
        <StatTile label="Scheduler" value="6h" sub="testable scan cadence" icon={<IRepeat className="h-5 w-5" />} tone="amber" />
        <StatTile label="Privacy" value="Encrypted" sub="tokens + masked logs" icon={<IShield className="h-5 w-5" />} tone="emerald" />
      </div>

      {scan ? (
        <section className="card">
          <SectionHeader title="Latest scan result" subtitle={scan.dry_run ? "Dry-run mode (configure Google OAuth credentials for live Gmail)" : "Live Gmail scan"} />
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4"><div className="text-sm font-semibold text-white">Emails scanned</div><div className="mt-2 text-3xl font-bold text-white">{scan.scanned}</div></div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4"><div className="text-sm font-semibold text-white">Statements ingested</div><div className="mt-2 text-3xl font-bold text-white">{scan.statements_ingested}</div></div>
          </div>
        </section>
      ) : null}
    </div>
  );
}
