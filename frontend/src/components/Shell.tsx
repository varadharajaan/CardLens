"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { useAuth } from "@/lib/auth";
import {
  IAlert,
  IBank,
  ICard,
  IDoc,
  IFolder,
  IGift,
  IGrid,
  IInbox,
  IRepeat,
  IShield,
  ISignout,
  ISpark,
  ITarget,
  ITrend,
  IUpload,
  IWallet,
} from "@/components/icons";
import { ThemeToggle } from "@/components/ThemeToggle";

const NAV_GROUPS = [
  {
    title: "Command",
    items: [
      { href: "/dashboard", label: "Overview", Icon: IGrid, badge: "Live" },
      { href: "/dashboard/intelligence", label: "Intelligence Suite", Icon: ISpark, badge: "25" },
    ],
  },
  {
    title: "Portfolio",
    items: [
      { href: "/dashboard/portfolio", label: "Cards", Icon: ICard },
      { href: "/dashboard/features/card-roi", label: "Card ROI", Icon: ITrend },
      { href: "/dashboard/features/credit-utilization", label: "Utilization", Icon: ITarget },
      { href: "/dashboard/bank-accounts", label: "Bank Accounts", Icon: IBank },
    ],
  },
  {
    title: "Statements",
    items: [
      { href: "/dashboard/statements", label: "Statement Intelligence", Icon: IDoc },
      { href: "/dashboard/upload", label: "Upload PDF", Icon: IUpload },
      { href: "/dashboard/inbox", label: "Gmail Onboarding", Icon: IInbox, badge: "OAuth" },
    ],
  },
  {
    title: "Money Leaks",
    items: [
      { href: "/dashboard/features/reward-tracker", label: "Rewards", Icon: IGift },
      { href: "/dashboard/features/milestone-tracker", label: "Milestones", Icon: ITarget },
      { href: "/dashboard/features/fee-charge-anomalies", label: "Anomalies", Icon: IAlert },
      { href: "/dashboard/features/subscription-tracker", label: "Subscriptions", Icon: IRepeat },
      { href: "/dashboard/features/portfolio-recommendations", label: "Recommendations", Icon: IWallet },
    ],
  },
  {
    title: "Ops",
    items: [
      { href: "/dashboard/features/document-vault", label: "Document Vault", Icon: IFolder },
      { href: "/dashboard/features/manual-correction", label: "Corrections", Icon: IShield },
    ],
  },
];

export function Shell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { token, ready, logout } = useAuth();

  useEffect(() => {
    if (ready && !token) router.replace("/login");
  }, [ready, token, router]);

  if (!ready || !token) {
    return <div className="flex min-h-screen items-center justify-center text-slate-400">Loading...</div>;
  }
  const flatNav = NAV_GROUPS.flatMap((group) => group.items);
  const active = flatNav.slice().reverse().find((n) => pathname === n.href || pathname.startsWith(`${n.href}/`)) ?? flatNav[0];

  const signOut = () => { logout(); router.replace("/login"); };

  return (
    <div className="flex min-h-screen">
      <aside className="sticky top-0 hidden h-screen w-[18.5rem] shrink-0 flex-col gap-5 overflow-hidden border-r border-white/10 bg-white/[0.035] p-5 backdrop-blur-xl md:flex">
        <div className="flex items-center gap-3 px-1">
          <div className="grid h-11 w-11 place-items-center rounded-2xl bg-gradient-to-br from-violet-600 to-fuchsia-600 text-lg font-black text-white shadow-lg shadow-violet-900/50">C</div>
          <div>
            <div className="text-xl font-bold tracking-tight">Card<span className="gradient-text">Lens</span></div>
            <div className="text-[11px] font-medium uppercase tracking-[0.18em] text-slate-500">Financial OS</div>
          </div>
        </div>
        <nav className="flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto pr-1">
          {NAV_GROUPS.map((group) => (
            <div key={group.title} className="space-y-1.5">
              <div className="px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">{group.title}</div>
              {group.items.map(({ href, label, Icon, badge }) => (
                <Link key={href} href={href} className={`nav-link ${href === active.href ? "nav-link-active" : ""}`}>
                  <span className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-white/[0.045] text-slate-300 ring-1 ring-white/10">
                    <Icon className="h-[18px] w-[18px]" />
                  </span>
                  <span className="min-w-0 flex-1 truncate">{label}</span>
                  {badge ? <span className="rounded-full bg-white/10 px-2 py-0.5 text-[10px] font-semibold text-slate-300">{badge}</span> : null}
                </Link>
              ))}
            </div>
          ))}
        </nav>
        <div className="rounded-3xl border border-violet-400/20 bg-gradient-to-br from-violet-500/15 to-sky-500/10 p-4">
          <div className="text-sm font-semibold text-white">Gmail ingestion</div>
          <p className="mt-1 text-xs leading-5 text-slate-400">Connect, scan, parse, and populate your dashboard.</p>
          <Link href="/dashboard/inbox" className="mt-3 inline-flex text-xs font-semibold text-violet-300 hover:text-violet-200">Open onboarding</Link>
        </div>
        <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.04] p-3">
          <div className="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-sky-500 to-violet-600 text-sm font-bold text-white">D</div>
          <div className="min-w-0 flex-1"><div className="truncate text-sm font-medium text-white">Demo user</div><div className="text-xs text-slate-400">Signed in</div></div>
          <button type="button" onClick={signOut} className="rounded-xl p-2 text-slate-400 hover:bg-white/10 hover:text-white"><ISignout className="h-5 w-5" /></button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-10 flex items-center justify-between gap-3 border-b border-white/10 bg-[#070a14]/70 px-4 py-3 backdrop-blur-xl sm:px-6 lg:px-8">
          <div className="min-w-0">
            <h1 className="truncate text-xl font-bold tracking-tight text-white sm:text-2xl">{active.label}</h1>
            <p className="truncate text-xs text-slate-400 sm:text-sm">Credit-card and bank-account intelligence</p>
          </div>
          <div className="flex shrink-0 items-center gap-2 sm:gap-3">
            <ThemeToggle />
            <div className="pill text-emerald-300"><span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_10px] shadow-emerald-400" /><span className="hidden sm:inline">Live</span></div>
            <button type="button" onClick={signOut} aria-label="Sign out" className="grid h-9 w-9 place-items-center rounded-xl border border-white/10 bg-white/5 text-slate-300 transition hover:bg-white/10 hover:text-white sm:w-auto sm:px-3">
              <ISignout className="h-4 w-4" /> <span className="ml-2 hidden whitespace-nowrap text-xs font-semibold sm:inline">Sign out</span>
            </button>
          </div>
        </header>
        <nav className="flex gap-2 overflow-x-auto border-b border-white/10 px-4 py-3 md:hidden">
          {flatNav.slice(0, 8).map(({ href, label, Icon }) => (
            <Link key={href} href={href} className={`inline-flex shrink-0 items-center gap-2 rounded-2xl border px-3 py-2 text-xs font-semibold ${href === active.href ? "border-violet-400/30 bg-violet-500/15 text-white" : "border-white/10 bg-white/[0.04] text-slate-400"}`}>
              <Icon className="h-4 w-4" /> {label}
            </Link>
          ))}
        </nav>
        <main className="mx-auto w-full max-w-6xl flex-1 p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
