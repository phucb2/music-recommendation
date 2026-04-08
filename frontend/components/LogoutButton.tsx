"use client";

export function LogoutButton() {
  async function logout() {
    await fetch("/api/auth/logout", { method: "POST" });
    window.location.href = "/login";
  }

  return (
    <button
      type="button"
      onClick={() => void logout()}
      className="rounded-lg border border-white/15 px-3 py-1.5 text-sm text-muted transition-colors hover:border-white/30 hover:text-foreground"
    >
      Log out
    </button>
  );
}
