"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { apiFetch, getToken, setToken } from "@/lib/api";
import type { TokenPair } from "@/lib/types";

interface AuthState {
  token: string | null;
  ready: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setTokenState(getToken());
    setReady(true);
  }, []);

  const persist = useCallback((pair: TokenPair) => {
    setToken(pair.access_token);
    setTokenState(pair.access_token);
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const pair = await apiFetch<TokenPair>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      persist(pair);
    },
    [persist],
  );

  const register = useCallback(
    async (email: string, password: string, fullName: string) => {
      const pair = await apiFetch<TokenPair>("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password, full_name: fullName }),
      });
      persist(pair);
    },
    [persist],
  );

  const logout = useCallback(() => {
    setToken(null);
    setTokenState(null);
  }, []);

  const value = useMemo(
    () => ({ token, ready, login, register, logout }),
    [token, ready, login, register, logout],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
