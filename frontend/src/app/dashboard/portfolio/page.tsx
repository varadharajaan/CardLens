"use client";

import {
  Badge,
  EmptyState,
  ErrorBanner,
  Loading,
  NetworkChip,
  SectionHeader,
  StatusChip,
} from "@/components/ui";
import { formatMoney } from "@/lib/format";
import { useApi } from "@/lib/hooks";
import type { Card, CardAccount, Page } from "@/lib/types";

function VariantRow({ card }: { card: Card }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-line bg-panel2/60 px-3.5 py-2.5">
      <div className="flex items-center gap-3">
        <span className="text-sm font-medium text-ink">{card.card_name}</span>
        {card.is_primary ? <Badge tone="brand">primary</Badge> : null}
        <NetworkChip network={card.network} />
      </div>
      <div className="flex items-center gap-3">
        <span className="font-mono text-xs text-muted">****{card.last4}</span>
        {card.reward_format ? <Badge tone="muted">{card.reward_format}</Badge> : null}
      </div>
    </div>
  );
}

export default function PortfolioPage() {
  const cards = useApi<Page<Card>>("/cards?page=1&size=100");
  const accounts = useApi<Page<CardAccount>>("/card-accounts?page=1&size=100");

  if (cards.loading || accounts.loading) return <Loading label="Loading cards..." />;
  if (cards.error) return <ErrorBanner message={cards.error} />;
  if (accounts.error) return <ErrorBanner message={accounts.error} />;

  const allCards = cards.data?.items ?? [];
  const companionAccounts = accounts.data?.items ?? [];
  const standalone = allCards.filter((c) => !c.account_id);
  const variantsByAccount = (id: string) =>
    allCards
      .filter((c) => c.account_id === id)
      .sort((a, b) => Number(b.is_primary) - Number(a.is_primary));

  return (
    <div className="flex flex-col gap-6">
      <section>
        <SectionHeader
          title="Companion accounts"
          subtitle="Network variants that share one statement and one due"
        />
        {companionAccounts.length === 0 ? (
          <EmptyState title="No companion accounts yet" hint="Seed sample data to see them here." />
        ) : (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {companionAccounts.map((acc) => (
              <div key={acc.id} className="card flex flex-col gap-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-ink">{acc.display_name}</span>
                      <StatusChip status={acc.status} />
                    </div>
                    <span className="text-xs text-muted">{acc.bank}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-muted">Credit limit</div>
                    <div className="text-sm font-medium text-ink">
                      {formatMoney(acc.credit_limit)}
                    </div>
                  </div>
                </div>
                <div className="flex flex-col gap-2">
                  {variantsByAccount(acc.id).map((c) => (
                    <VariantRow key={c.id} card={c} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section>
        <SectionHeader title="Standalone cards" subtitle="Cards billed on their own" />
        {standalone.length === 0 ? (
          <EmptyState title="No standalone cards" />
        ) : (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {standalone.map((c) => (
              <div key={c.id} className="card flex flex-col gap-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium text-ink">{c.card_name}</span>
                  <StatusChip status={c.status} />
                </div>
                <span className="text-xs text-muted">{c.bank}</span>
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs text-muted">****{c.last4}</span>
                  <NetworkChip network={c.network} />
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
