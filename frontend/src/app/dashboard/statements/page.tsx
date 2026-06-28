"use client";

import { Badge, EmptyState, ErrorBanner, Loading, SectionHeader, type Tone } from "@/components/ui";
import { formatDate, formatMoney, formatNumber } from "@/lib/format";
import { useApi } from "@/lib/hooks";
import type { Page, Statement } from "@/lib/types";

function parseTone(status: string): Tone {
  if (status === "FOUND") return "ok";
  if (status === "PARTIAL") return "warn";
  return "muted";
}

export default function StatementsPage() {
  const statements = useApi<Page<Statement>>("/statements?page=1&size=50");

  if (statements.loading) return <Loading label="Loading statements..." />;
  if (statements.error) return <ErrorBanner message={statements.error} />;
  const items = statements.data?.items ?? [];

  return (
    <div className="flex flex-col gap-4">
      <SectionHeader
        title="Statements"
        subtitle={`${statements.data?.total ?? 0} parsed statements`}
      />
      {items.length === 0 ? (
        <EmptyState title="No statements yet" hint="Seed sample data to see them here." />
      ) : (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-line text-left text-xs uppercase tracking-wide text-muted">
                <th className="px-4 py-3 font-medium">Card</th>
                <th className="px-4 py-3 font-medium">Due date</th>
                <th className="px-4 py-3 text-right font-medium">Total due</th>
                <th className="px-4 py-3 text-right font-medium">Min due</th>
                <th className="px-4 py-3 text-right font-medium">Points</th>
                <th className="px-4 py-3 font-medium">Reward parse</th>
              </tr>
            </thead>
            <tbody>
              {items.map((s) => (
                <tr key={s.id} className="border-b border-line/60 last:border-0">
                  <td className="px-4 py-3">
                    <div className="font-medium text-ink">{s.card_name}</div>
                    <div className="text-xs text-muted">
                      {s.bank} - ****{s.last4}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-muted">{formatDate(s.due_date)}</td>
                  <td className="px-4 py-3 text-right text-ink">{formatMoney(s.total_due)}</td>
                  <td className="px-4 py-3 text-right text-muted">{formatMoney(s.minimum_due)}</td>
                  <td className="px-4 py-3 text-right text-muted">
                    {formatNumber(s.reward_points_closing)}
                  </td>
                  <td className="px-4 py-3">
                    <Badge tone={parseTone(s.reward_parse_status)}>{s.reward_parse_status}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
