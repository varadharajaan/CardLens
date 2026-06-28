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
import type { BankAccount, DebitCard, Page } from "@/lib/types";

export default function BankAccountsPage() {
  const accounts = useApi<Page<BankAccount>>("/bank-accounts?page=1&size=100");
  const debitCards = useApi<Page<DebitCard>>("/debit-cards?page=1&size=100");

  if (accounts.loading || debitCards.loading) return <Loading label="Loading bank accounts..." />;
  if (accounts.error) return <ErrorBanner message={accounts.error} />;
  if (debitCards.error) return <ErrorBanner message={debitCards.error} />;

  const allAccounts = accounts.data?.items ?? [];
  const allDebit = debitCards.data?.items ?? [];
  const cardsForAccount = (id: string) =>
    allDebit
      .filter((c) => c.bank_account_id === id)
      .sort((a, b) => Number(b.is_primary) - Number(a.is_primary));

  return (
    <div className="flex flex-col gap-6">
      <SectionHeader
        title="Bank accounts"
        subtitle="Deposit accounts and their debit-card variants"
      />
      {allAccounts.length === 0 ? (
        <EmptyState title="No bank accounts yet" hint="Seed sample data to see them here." />
      ) : (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {allAccounts.map((acc) => (
            <div key={acc.id} className="card flex flex-col gap-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-ink">{acc.display_name}</span>
                    <StatusChip status={acc.status} />
                  </div>
                  <span className="text-xs text-muted">
                    {acc.bank} - {acc.account_type}
                    {acc.last4 ? ` - ****${acc.last4}` : ""}
                  </span>
                </div>
                <div className="text-right">
                  <div className="text-xs text-muted">Balance</div>
                  <div className="text-sm font-medium text-ink">{formatMoney(acc.balance)}</div>
                </div>
              </div>
              <div className="flex flex-col gap-2">
                {cardsForAccount(acc.id).length === 0 ? (
                  <span className="text-xs text-muted">No debit cards.</span>
                ) : (
                  cardsForAccount(acc.id).map((c) => (
                    <div
                      key={c.id}
                      className="flex items-center justify-between gap-3 rounded-xl border border-line bg-panel2/60 px-3.5 py-2.5"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-medium text-ink">{c.card_name}</span>
                        {c.is_primary ? <Badge tone="brand">primary</Badge> : null}
                        <NetworkChip network={c.network} />
                      </div>
                      <span className="font-mono text-xs text-muted">****{c.last4}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
