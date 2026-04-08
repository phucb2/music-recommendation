"use client";

/** Visual-only search chrome (mockup: no queries in v1). */
export function SearchBarDecor() {
  return (
    <div className="w-full max-w-xl">
      <label className="sr-only" htmlFor="search-demo">
        Search
      </label>
      <input
        id="search-demo"
        readOnly
        tabIndex={-1}
        placeholder="Search (demo)"
        className="w-full rounded-lg border border-white/10 bg-stage px-4 py-2.5 text-sm text-muted placeholder:text-muted/70 focus:outline-none focus:ring-2 focus:ring-accent/40"
        aria-disabled
      />
    </div>
  );
}
