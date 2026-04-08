"use client";

import { useState } from "react";
import { SiteFooter } from "@/components/SiteFooter";

export function LoginForm() {
  const [username, setUsername] = useState("demo");
  const [password, setPassword] = useState("demo");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setPending(true);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) {
        const data = (await res.json().catch(() => ({}))) as { error?: string };
        setError(data.error ?? "Invalid credentials");
        setPending(false);
        return;
      }
      window.location.href = "/";
    } catch {
      setError("Something went wrong");
      setPending(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-[100dvh] w-full max-w-7xl flex-col px-4 py-8 sm:px-6 lg:px-10">
      <div className="flex flex-1 flex-col justify-center py-4">
        <div className="mx-auto w-full max-w-md rounded-2xl border border-white/10 bg-stage/40 px-6 py-10 sm:px-8 lg:max-w-lg lg:border-white/15 lg:px-10 lg:py-12">
          <h1 className="font-display text-3xl font-semibold text-foreground sm:text-4xl">Nhạc của tôi</h1>
          <p className="mt-2 text-sm text-muted">Sign in to continue (demo: demo / demo)</p>

          <form onSubmit={onSubmit} className="mt-8 space-y-4">
            <div>
              <label className="mb-1 block text-sm text-muted" htmlFor="user">
                Username
              </label>
              <input
                id="user"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full rounded-lg border border-white/10 bg-stage px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-accent/40"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm text-muted" htmlFor="pass">
                Password
              </label>
              <input
                id="pass"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-white/10 bg-stage px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-accent/40"
              />
            </div>

            {error ? (
              <p className="text-sm text-red-400" role="alert">
                {error}
              </p>
            ) : null}

            <button
              type="submit"
              disabled={pending}
              className="w-full rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-venue transition-opacity hover:opacity-90 disabled:opacity-50"
            >
              {pending ? "Signing in…" : "Sign in"}
            </button>
          </form>
        </div>
      </div>
      <SiteFooter className="mt-auto shrink-0" />
    </div>
  );
}
