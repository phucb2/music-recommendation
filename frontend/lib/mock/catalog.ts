import type { Song } from "@/lib/types";

/** Deterministic demo catalog; swap this module to point at a real API. */
export const CATALOG: Song[] = [
  {
    song_id: "s1",
    title: "Midnight Hall",
    author: "Maya Ortiz",
    singer: "The Amber Keys",
    genre: "Indie rock",
    artwork_url: "https://picsum.photos/seed/midnight/400/400",
    duration_seconds: 372,
    audio_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
  },
  {
    song_id: "s2",
    title: "Velvet Stage",
    author: "Jonah Reeves & Lina Cho",
    singer: "Luna Quartet",
    genre: "Contemporary jazz",
    artwork_url: "https://picsum.photos/seed/velvet/400/400",
    duration_seconds: 398,
    audio_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
  },
  {
    song_id: "s3",
    title: "Slow Spotlight",
    author: "Elena Voss",
    singer: "Nora Grey",
    genre: "Soul",
    artwork_url: "https://picsum.photos/seed/spotlight/400/400",
    duration_seconds: 421,
    audio_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
  },
  {
    song_id: "s4",
    title: "Brass Echo",
    author: "Marcus Bell",
    singer: "Harbor Brass",
    genre: "Brass band",
    artwork_url: "https://picsum.photos/seed/brass/400/400",
    duration_seconds: 350,
    audio_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
  },
  {
    song_id: "s5",
    title: "Side Door",
    author: "Priya Nair",
    singer: "Metro Fiction",
    genre: "Alternative",
    artwork_url: "https://picsum.photos/seed/sidedoor/400/400",
    duration_seconds: 405,
    audio_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
  },
  {
    song_id: "s6",
    title: "Encore Whisper",
    author: "Chris Yamamoto",
    singer: "Soft Voltage",
    genre: "Electronic",
    artwork_url: "https://picsum.photos/seed/encore/400/400",
    duration_seconds: 388,
    audio_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
  },
  {
    song_id: "s7",
    title: "Crowd Fade",
    author: "Sam Okonkwo",
    singer: "Analog Tides",
    genre: "Ambient rock",
    artwork_url: "https://picsum.photos/seed/crowd/400/400",
    duration_seconds: 410,
    audio_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3",
  },
  {
    song_id: "s8",
    title: "House Lights",
    author: "Dana Frost",
    singer: "Circuit Choir",
    genre: "others",
    artwork_url: "https://picsum.photos/seed/houselights/400/400",
    duration_seconds: 365,
    audio_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
  },
];

export function getSongById(id: string): Song | undefined {
  return CATALOG.find((s) => s.song_id === id);
}

function hash(str: string): number {
  let h = 0;
  for (let i = 0; i < str.length; i++) h = (Math.imul(31, h) + str.charCodeAt(i)) | 0;
  return h;
}

/** Deterministic “personalized” order per user. */
export function getHomeRecommendations(userId: string): Song[] {
  const shuffled = [...CATALOG].sort(
    (a, b) => hash(userId + a.song_id) - hash(userId + b.song_id),
  );
  const list = shuffled.slice(0, 10);
  // Intentional duplicate of first item to exercise client dedupe (mockup).
  if (list.length > 0) {
    return [list[0]!, ...list];
  }
  return list;
}

/** Song-to-song “similar” next picks: other catalog tracks in stable order. */
export function getNextSongs(currentSongId: string): Song[] {
  return CATALOG.filter((s) => s.song_id !== currentSongId).slice(0, 6);
}

export function dedupeBySongId(songs: Song[]): Song[] {
  const seen = new Set<string>();
  return songs.filter((s) => {
    if (seen.has(s.song_id)) return false;
    seen.add(s.song_id);
    return true;
  });
}
