"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { useAuth } from "@/lib/auth";

const NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/dashboard/portfolio", label: "Cards" },
  { href: "/dashboard/bank-accounts", label: "Bank Accounts" },
  { href: "/dashboard/statements", label: "Statements" },
];

function Dot() {
  return <span className="h-1.5 w-1.5 rounded-full bg-current" />;
}

export function Shell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { token, ready, logout } = useAuth();

  useEffect(() => {
    if (ready && !token) router.replace("/login");
  }, [ready, token, router]);

  if (!ready || !token) {
    return (
      <div className="flex min-h-screen items-center justify-center text-muted">Loading...</div>
    );
  }

  // Match the most specific nav entry (nested routes win over the /dashboard root).
  const active =
    NAV.slice()
      .reverse()
      .find((n) => pathname === n.href || pathname.startsWith(`${n.href}/`)) ?? NAV[0];

  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-64 shrink-0 flex-col gap-6 border-r border-line bg-panel2/70 p-5 md:flex">
        <div className="flex items-center gap-2">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-brand to-brand-2 text-base font-bold text-white">
            C
          </div>
          <div className="text-lg font-semibold tracking-tight">
            Card<span className="gradient-text">Lens</span>
          </div>
        </div>
        <nav className="flex flex-col gap-1">
          {NAV.map((n) => (
            <Link
              key={n.href}
              href={n.href}
              className={`nav-link ${n.href === active.href ? "nav-link-active" : ""}`}
            >
              <Dot /> {n.label}
            </Link>
          ))}
        </nav>
        <button
          type="button"
          onClick={() => {
            logout();
            router.replace("/login");
          }}
          className="nav-link mt-auto w-full"
        >
          <Dot /> Sign out
        </button>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-10 flex items-center justify-between border-b border-line bg-bg/70 px-6 py-4 backdrop-blur">
          <div>
            <h1 className="text-xl font-semibold text-ink">{active.label}</h1>
            <p className="text-xs text-muted">CardLens portfolio intelligence</p>
          </div>
          <div className="pill border-line">
            <span className="h-2 w-2 rounded-full bg-ok" /> Connected
          </div>
        </header>
        <main className="mx-auto w-full max-w-6xl flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
