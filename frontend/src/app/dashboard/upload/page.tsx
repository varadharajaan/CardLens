"use client";

import { useState } from "react";
import { ErrorBanner, SectionHeader } from "@/components/ui";
import { API_BASE, getToken } from "@/lib/api";
import { formatMoney, formatNumber } from "@/lib/format";
import type { ParsedStatement } from "@/lib/types";

export default function UploadPage() {
  const [bank, setBank] = useState("HDFC");
  const [name, setName] = useState("");
  const [dob, setDob] = useState("");
  const [last4, setLast4] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ParsedStatement | null>(null);

  async function onUpload(file: File) {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const form = new FormData();
      form.append("file", file);
      if (bank) form.append("bank", bank);
      if (name) form.append("name", name);
      if (dob) form.append("dob_ddmm", dob);
      if (last4) form.append("card_last4", last4);
      const res = await fetch(`${API_BASE}/api/v1/parsers/preview-pdf`, {
        method: "POST",
        headers: { Authorization: `Bearer ${getToken() ?? ""}` },
        body: form,
      });
      if (!res.ok) {
        const e = await res.json().catch(() => ({}));
        throw new Error(e.detail ?? "Could not parse this statement");
      }
      setResult(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <SectionHeader
        title="Parse a statement"
        subtitle="Upload a PDF; password unlock + extraction run locally"
      />
      <div className="card flex flex-col gap-3">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <input className="input" value={bank} onChange={(e) => setBank(e.target.value)} placeholder="Bank (e.g. HDFC)" />
          <input className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder="Name on card" />
          <input className="input" value={dob} onChange={(e) => setDob(e.target.value)} placeholder="DOB ddmm" />
          <input className="input" value={last4} onChange={(e) => setLast4(e.target.value)} placeholder="Card last4" />
        </div>
        <label className="btn w-fit cursor-pointer">
          {busy ? "Parsing..." : "Choose PDF"}
          <input
            type="file"
            accept="application/pdf"
            className="hidden"
            disabled={busy}
            onChange={(e) => e.target.files?.[0] && onUpload(e.target.files[0])}
          />
        </label>
      </div>
      {error ? <ErrorBanner message={error} /> : null}
      {result ? (
        <div className="card flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-ink">{result.bank} statement</span>
            <span className="pill border-brand/30 bg-brand/10 text-brand">{result.reward_parse_status}</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm sm:grid-cols-3">
            <div><span className="text-muted">Card </span>{result.card_name ?? "-"} {result.last4 ? `****${result.last4}` : ""}</div>
            <div><span className="text-muted">Total due </span>{formatMoney(result.total_due)}</div>
            <div><span className="text-muted">Min due </span>{formatMoney(result.minimum_due)}</div>
            <div><span className="text-muted">Points </span>{formatNumber(result.reward_points_closing)}</div>
            <div><span className="text-muted">Due date </span>{result.due_date ?? "-"}</div>
            <div><span className="text-muted">Confidence </span>{Math.round(result.parse_confidence * 100)}%</div>
          </div>
          {result.evidence_snippet ? <p className="text-xs text-muted">Evidence: {result.evidence_snippet}</p> : null}
        </div>
      ) : null}
    </div>
  );
}
