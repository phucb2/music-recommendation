"use client";

import Image from "next/image";
import { EVENT_TYPE, SURFACE } from "@/lib/constants";
import { emitEvent } from "@/lib/analytics";
import { useInViewOnce } from "@/lib/hooks/useInViewOnce";
import { SongCreditsRow } from "@/components/SongCredits";
import type { Song } from "@/lib/types";
import { formatMmSs } from "@/lib/format";

type Surface = typeof SURFACE.homepage | typeof SURFACE.next_song;

export function TrackRow({
  song,
  position,
  userId,
  surface,
  onSelect,
  compact,
}: {
  song: Song;
  position: number;
  userId: string;
  surface: Surface;
  onSelect: (song: Song, position: number) => void;
  /** Tighter row for player sidebar (fits viewport without scrolling). */
  compact?: boolean;
}) {
  const ref = useInViewOnce(() => {
    void emitEvent({
      user_id: userId,
      song_id: song.song_id,
      surface,
      event_type: EVENT_TYPE.impression,
      position,
      request_id: `req_${surface}_${position}`,
    });
  });

  return (
    <div
      ref={ref}
      className={
        compact
          ? "rounded-lg border border-white/10 bg-stage/80 px-2 py-1.5 transition-colors hover:border-accent/30"
          : "rounded-xl border border-white/10 bg-stage/80 px-3 py-2.5 transition-colors hover:border-accent/30"
      }
    >
      <button
        type="button"
        onClick={() => onSelect(song, position)}
        className={compact ? "flex w-full items-center gap-2 text-left" : "flex w-full items-center gap-3 text-left"}
      >
        <div
          className={
            compact
              ? "relative h-10 w-10 shrink-0 overflow-hidden rounded bg-black/40"
              : "relative h-[4.25rem] w-[4.25rem] shrink-0 overflow-hidden rounded-md bg-black/40"
          }
        >
          <Image
            src={song.artwork_url}
            alt=""
            fill
            sizes={compact ? "40px" : "68px"}
            className="object-cover"
          />
        </div>
        <span className="min-w-0 flex-1">
          <span
            className={
              compact
                ? "block truncate text-sm font-medium leading-tight text-foreground"
                : "block truncate font-medium leading-snug text-foreground"
            }
          >
            {song.title}
          </span>
          {compact ? (
            <span className="mt-0.5 block text-[11px] leading-snug">
              <span className="block truncate font-medium text-accent/85">{song.genre}</span>
              <span className="mt-0.5 block truncate text-muted">
                <span className="text-muted/90">Author </span>
                {song.author}
                <span className="text-muted/50"> · </span>
                <span className="text-muted/90">Singer </span>
                {song.singer}
              </span>
            </span>
          ) : (
            <SongCreditsRow song={song} />
          )}
        </span>
        <span className="shrink-0 tabular-nums text-muted" style={{ fontSize: compact ? "0.7rem" : undefined }}>
          {formatMmSs(song.duration_seconds)}
        </span>
      </button>
    </div>
  );
}
