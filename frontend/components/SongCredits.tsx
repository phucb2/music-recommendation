import type { Song } from "@/lib/types";

/** Compact credits for track rows (lists). */
export function SongCreditsRow({ song }: { song: Song }) {
  return (
    <span className="flex min-w-0 flex-col gap-0.5 text-left">
      <span className="truncate text-xs leading-snug">
        <span className="font-medium text-muted/90">Genre </span>
        <span className="text-accent/90">{song.genre}</span>
      </span>
      <span className="truncate text-xs leading-snug">
        <span className="font-medium text-muted/90">Author </span>
        <span className="text-muted">{song.author}</span>
      </span>
      <span className="truncate text-xs leading-snug">
        <span className="font-medium text-muted/90">Singer </span>
        <span className="text-muted">{song.singer}</span>
      </span>
    </span>
  );
}

/** Prominent credits on the player screen (`compact` fits a single viewport with the timeline). */
export function SongCreditsPlayer({ song, compact }: { song: Song; compact?: boolean }) {
  if (compact) {
    return (
      <dl className="space-y-1 text-sm">
        <div className="flex min-w-0 gap-2">
          <dt className="w-14 shrink-0 text-[10px] font-semibold uppercase tracking-wide text-muted">
            Genre
          </dt>
          <dd className="min-w-0 truncate font-medium text-accent/95">{song.genre}</dd>
        </div>
        <div className="flex min-w-0 gap-2">
          <dt className="w-14 shrink-0 text-[10px] font-semibold uppercase tracking-wide text-muted">
            Author
          </dt>
          <dd className="min-w-0 truncate font-medium text-foreground">{song.author}</dd>
        </div>
        <div className="flex min-w-0 gap-2">
          <dt className="w-14 shrink-0 text-[10px] font-semibold uppercase tracking-wide text-muted">
            Singer
          </dt>
          <dd className="min-w-0 truncate font-medium text-foreground">{song.singer}</dd>
        </div>
      </dl>
    );
  }

  return (
    <dl className="space-y-2 text-base sm:text-lg">
      <div className="flex flex-col gap-0.5 sm:flex-row sm:items-baseline sm:gap-3">
        <dt className="shrink-0 text-xs font-semibold uppercase tracking-wider text-muted sm:w-24 sm:text-sm">
          Genre
        </dt>
        <dd className="font-medium text-accent sm:text-lg">{song.genre}</dd>
      </div>
      <div className="flex flex-col gap-0.5 sm:flex-row sm:items-baseline sm:gap-3">
        <dt className="shrink-0 text-xs font-semibold uppercase tracking-wider text-muted sm:w-24 sm:text-sm">
          Author
        </dt>
        <dd className="font-medium text-foreground">{song.author}</dd>
      </div>
      <div className="flex flex-col gap-0.5 sm:flex-row sm:items-baseline sm:gap-3">
        <dt className="shrink-0 text-xs font-semibold uppercase tracking-wider text-muted sm:w-24 sm:text-sm">
          Singer
        </dt>
        <dd className="font-medium text-foreground">{song.singer}</dd>
      </div>
    </dl>
  );
}
