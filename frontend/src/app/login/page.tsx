"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { useAuth } from "@/lib/auth";

const DEMO_EMAIL = "demo@example.com";
const DEMO_PASSWORD = "Sup3rSecret!";

export default function LoginPage() {
  const router = useRouter();
  const { login, register, token, ready } = useAuth();
  const [email, setEmail] = useState(DEMO_EMAIL);
  const [password, setPassword] = useState(DEMO_PASSWORD);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (ready && token) router.replace("/dashboard");
  }, [ready, token, router]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(email, password);
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  async function useDemo() {
    setBusy(true);
    setError(null);
    try {
      try {
        await login(DEMO_EMAIL, DEMO_PASSWORD);
      } catch {
        await register(DEMO_EMAIL, DEMO_PASSWORD, "CardLens Demo");
      }
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not start the demo");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="mb-8 flex items-center justify-center gap-2">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-brand to-brand-2 text-lg font-bold text-white">
            C
          </div>
          <div className="text-2xl font-semibold tracking-tight">
            Card<span className="gradient-text">Lens</span>
          </div>
        </div>
        <div className="card shadow-glow">
          <h1 className="text-lg font-semibold text-ink">Sign in</h1>
          <p className="mb-5 text-sm text-muted">
            Access your card and bank-account intelligence.
          </p>
          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <label className="text-sm text-muted">
              Email
              <input
                className="input mt-1"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="username"
                required
              />
            </label>
            <label className="text-sm text-muted">
              Password
              <input
                className="input mt-1"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </label>
            {error ? <p className="text-sm text-danger">{error}</p> : null}
            <button type="submit" className="btn mt-2" disabled={busy}>
              {busy ? "Signing in..." : "Sign in"}
            </button>
          </form>
          <button
            type="button"
            onClick={useDemo}
            disabled={busy}
            className="mt-3 w-full rounded-xl border border-line px-4 py-2.5 text-sm font-medium text-muted transition hover:bg-white/5 hover:text-ink disabled:opacity-50"
          >
            Use the demo account
          </button>
        </div>
      </div>
    </div>
  );
}
