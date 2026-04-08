"use client";

import { TrackRow } from "@/components/TrackRow";
import { EVENT_TYPE, SURFACE } from "@/lib/constants";
import { emitEvent } from "@/lib/analytics";
import type { Song } from "@/lib/types";
import { useRouter } from "next/navigation";

type Surface = typeof SURFACE.homepage | typeof SURFACE.next_song;

export function TrackList({
  songs,
  userId,
  surface,
  layout = "stack",
  compact,
}: {
  songs: Song[];
  userId: string;
  surface: Surface;
  /** `grid`: multi-column on md+ (home). `stack`: single column (player queue). */
  layout?: "stack" | "grid";
  compact?: boolean;
}) {
  const router = useRouter();

  async function handleSelect(song: Song, position: number) {
    await emitEvent({
      user_id: userId,
      song_id: song.song_id,
      surface,
      event_type: EVENT_TYPE.click,
      position,
      request_id: `req_${surface}_${position}`,
    });
    const from = surface === SURFACE.homepage ? "homepage" : "next_song";
    router.push(`/play/${song.song_id}?from=${from}`);
  }

  const listClass =
    layout === "grid"
      ? "grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-3"
      : compact
        ? "space-y-1.5"
        : "space-y-2";

  return (
    <ul className={listClass}>
      {songs.map((song, position) => (
        <li key={song.song_id}>
          <TrackRow
            song={song}
            position={position}
            userId={userId}
            surface={surface}
            onSelect={handleSelect}
            compact={compact}
          />
        </li>
      ))}
    </ul>
  );
}
