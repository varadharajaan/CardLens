"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { useAuth } from "@/lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const { register, token, ready } = useAuth();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (ready && token) router.replace("/dashboard");
  }, [ready, token, router]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (password !== confirm) return setError("Passwords do not match");
    if (password.length < 8) return setError("Use at least 8 characters");
    setBusy(true);
    setError(null);
    try {
      await register(email, password, fullName);
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign up failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="mb-8 flex items-center justify-center gap-2">
          <div className="grid h-11 w-11 place-items-center rounded-2xl bg-gradient-to-br from-violet-600 to-fuchsia-600 text-lg font-black text-white">C</div>
          <div className="text-2xl font-bold tracking-tight">Card<span className="gradient-text">Lens</span></div>
        </div>
        <div className="card glow">
          <h1 className="text-xl font-bold text-white">Create your account</h1>
          <p className="mb-5 text-sm text-slate-400">Track cards, statements, rewards, and anomalies in one place.</p>
          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <input className="input" placeholder="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
            <input className="input" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" required />
            <input className="input" type="password" placeholder="Password (min 8 chars)" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="new-password" required />
            <input className="input" type="password" placeholder="Confirm password" value={confirm} onChange={(e) => setConfirm(e.target.value)} autoComplete="new-password" required />
            {error ? <p className="text-sm text-rose-300">{error}</p> : null}
            <button type="submit" className="btn mt-2" disabled={busy}>{busy ? "Creating..." : "Create account"}</button>
          </form>
          <p className="mt-4 text-center text-sm text-slate-400">Already have an account? <Link href="/login" className="font-medium text-violet-300 hover:text-violet-200">Sign in</Link></p>
        </div>
      </div>
    </div>
  );
}
