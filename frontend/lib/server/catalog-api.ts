import type { Song } from "@/lib/types";
import { dedupeBySongId, getNextSongs, getSongById } from "@/lib/mock/catalog";

function backendBase(): string | undefined {
  const u = process.env.BACKEND_API_URL;
  return u && u.length > 0 ? u.replace(/\/$/, "") : undefined;
}

async function fetchJson<T>(path: string): Promise<T> {
  const base = backendBase();
  if (!base) throw new Error("BACKEND_API_URL is not set");
  const res = await fetch(`${base}${path}`, { cache: "no-store" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Backend ${path} failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<T>;
}

/** Homepage rec list: requires BACKEND_API_URL to be set. */
export async function resolveHomeRecommendations(userId: string): Promise<Song[]> {
  const base = backendBase();
  if (!base) {
    throw new Error("BACKEND_API_URL is not set");
  }
  const songs = await fetchJson<Song[]>(
    `/v1/recommendations/home?user_id=${encodeURIComponent(userId)}`,
  );
  return dedupeBySongId(songs);
}

/** Player: current song + next list from API or mock. */
export async function resolvePlayContext(
  songId: string,
  userId?: string,
): Promise<{
  song: Song;
  nextSongs: Song[];
} | null> {
  const base = backendBase();
  if (!base) {
    const song = getSongById(songId);
    if (!song) return null;
    return { song, nextSongs: getNextSongs(songId) };
  }
  try {
    const song = await fetchJson<Song>(`/v1/songs/${encodeURIComponent(songId)}`);
    const nextQuery = new URLSearchParams({ current_song_id: songId });
    if (userId) nextQuery.set("user_id", userId);
    const nextSongs = await fetchJson<Song[]>(`/v1/recommendations/next?${nextQuery.toString()}`);
    return { song, nextSongs };
  } catch {
    const song = getSongById(songId);
    if (!song) return null;
    return { song, nextSongs: getNextSongs(songId) };
  }
}
