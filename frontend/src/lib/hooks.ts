"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

interface ApiResult<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
}

// Fetch a path on mount (and whenever it changes). Pass null to skip fetching.
export function useApi<T>(path: string | null): ApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!path) {
      setLoading(false);
      return;
    }
    let active = true;
    setLoading(true);
    setError(null);
    apiFetch<T>(path)
      .then((d) => {
        if (active) setData(d);
      })
      .catch((e: unknown) => {
        if (active) setError(e instanceof Error ? e.message : "Request failed");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [path]);

  return { data, error, loading };
}
