"use client";

import { formatMmSs } from "@/lib/format";

/**
 * Read-only playback bar: elapsed (left), remaining (right), no seeking.
 */
export function PlaybackTimeline({
  currentSeconds,
  totalSeconds,
}: {
  currentSeconds: number;
  totalSeconds: number;
}) {
  const safeTotal = Math.max(0, totalSeconds);
  const elapsed = Math.min(Math.max(0, currentSeconds), safeTotal);
  const remaining = Math.max(0, safeTotal - elapsed);
  const pct = safeTotal > 0 ? Math.min(100, (elapsed / safeTotal) * 100) : 0;

  return (
    <div className="w-full space-y-1.5">
      <div className="flex items-baseline justify-between gap-3 text-xs tabular-nums text-muted sm:text-sm">
        <span className="text-foreground">{formatMmSs(elapsed)}</span>
        <span>
          <span className="text-muted/80">Remaining </span>
          <span className="font-medium text-foreground">{formatMmSs(remaining)}</span>
        </span>
      </div>
      {/* Decorative only — not interactive (no seeking). */}
      <div
        className="pointer-events-none h-2 w-full overflow-hidden rounded-full bg-white/10"
        aria-hidden
      >
        <div
          className="h-full rounded-full bg-accent/90"
          style={{
            width: `${pct}%`,
            transition: "width 0.25s linear",
          }}
        />
      </div>
    </div>
  );
}
