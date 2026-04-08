# Mockup — demo music streaming app

**Purpose:** UI/flow spec for the demo streaming app that showcases recommendations. **When:** While designing or building the demo frontend; keep behavior aligned with [prd.md](prd.md).

Draft product surface for a **music streaming website** that demonstrates homepage and next-song recommendations plus basic analytics. Scope is intentionally smaller than the full [prd.md](prd.md) (e.g. simple auth, no subscription tiers in the UI).

---

## Goals (demo)

- Show **personalized homepage** recommendations after login.
- Show **next-song** suggestions in the player so playback can continue.
- Emit **impression / click / play** events (with play duration) to an in-house analytics pipeline for model training and evaluation.

**PRD note:** The full product assumes **subscribed** users and rich catalog metadata server-side; the demo can use simple login and still log the same **interaction shape** as [prd.md](prd.md) §8.3 so models and metrics stay comparable.

---

## User flows

### Login / logout

- **Login:** username + password only (no OAuth for the demo).
- **Success:** redirect to **Home**.
- **Logout:** clear session; redirect to **Login**.
- **Errors:** show inline message for invalid credentials (keep copy minimal).

### Home (post-login)

- **Primary:** scrollable list of **recommended songs** (title, artist, artwork thumbnail, optional duration). If the API can return duplicates, **client-side dedupe** by `song_id` helps match PRD “avoid excessive repetition” for the demo list.
- **Search (visual only):** a **search bar** at the top for **showcase**—no query, no results, no navigation. It exists so the layout reads like a streaming app; there is **no search feature** in v1 of the demo.
- **Impression:** **viewport-based**—fire when a recommended row **enters the viewport** (e.g. `IntersectionObserver`). Use **`surface: homepage`** so homepage CTR in PRD §11.2 can be computed.
- **Click:** fire when user selects a **homepage** rec to play; **navigate to the Player route** with that track and load **next recommendations** for the queue.

### Player

- **Route:** Player lives on its **own URL route** (not a modal, drawer, or overlay).
- **Now playing:** current track metadata + basic controls (play/pause, scrub optional).
- **Skip:** a **Skip** control advances to the next track in queue (or triggers next-song behavior). Emit an explicit **`skip`** analytics event when the user taps Skip (see Analytics), in addition to `play_end` for the partial listen.
- **Up next:** short list of **recommended next songs** (PRD §9.2 song-to-song similarity); populate when the current track starts or changes. **Viewport-based impressions** for these rows, same rule as Home. Log **`surface: next_song`** for impressions/clicks—PRD §11 splits homepage vs next-song for CTR and skip rate.
- **Play tracking:** record **start**, periodic **heartbeat** or **pause/end** with **listened duration** (seconds) and **total song duration** so the backend can apply PRD-style rules (e.g. qualified listen ≥30s or ≥50% of track—§11.1) and skip rate (early stop—§11.2). Include **`surface`** on the play that started the listen: **`homepage`** or **`next_song`** only for this demo.
- **Like / dislike:** **both** controls on the current track; log **`like`** and **`dislike`** events (PRD §8.1, MVP §14). Use `surface: player` (or attach to the playing track’s origin surface if you prefer one schema).

### Navigation

- **Home** ↔ **Player** via **separate routes** only (e.g. `/` and `/play` or `/player/:trackId`).

---

## Analytics (in-house)

Use a single small **event API** (REST or batch) from the web app. Align with PRD **§8.3 Interaction data to log** at minimum:

| PRD field | Notes for demo |
|-----------|----------------|
| `user_id` | From session / mock login |
| `song_id` | Catalog id |
| `timestamp` | Every event (server or client clock—be consistent) |
| `surface` | `homepage` \| `next_song` \| `player` (demo has no search; see below) |
| `event_type` | e.g. `impression`, `click`, `play_start`, `play_end`, `skip`, `like`, `dislike` |
| `play_duration_seconds` | On play end / heartbeat updates (listened portion) |
| `song_duration_seconds` | Track length—**required** to compute qualified listens and skip rules in §11.1–§11.2 |
| `session_id` | Browser session or app session id |

Suggested event shapes (conceptual; map into your `event_type` + columns):

| Event | When to send | Extra conceptual fields |
|-------|----------------|-------------------------|
| `impression` | Rec row shown | `surface` (`homepage` or `next_song`), `position`, `request_id` / `recommendation_id` |
| `click` | User selects a rec to play | same + which surface |
| `play_start` | Playback actually starts | `surface` of the action that started this play, `session_id` |
| `play_progress` / `play_end` | Heartbeat, pause, complete, tab close, or advance via Skip | `play_duration_seconds`, `song_duration_seconds`, `completed` if natural end |
| `skip` | User taps **Skip** | `song_id`, `play_duration_seconds` at skip time, `surface` (`homepage`-origin vs `next_song`-origin play if you track it) |

**Skip rate (PRD §11.2):** Combine explicit **`skip`** events with **`play_end`** rows where listened duration is below the skip threshold (e.g. under 30 seconds, or under 20% of `song_duration_seconds`).

**Explicit feedback:** Log **`like`** and **`dislike`** with `song_id`, `timestamp`, `surface` (e.g. `player`).

**Demo:** identities and catalog are **mock data**—no extra privacy or PII handling required for this build.

---

## Out of scope for this mockup (demo)

- Full subscription / billing UI (PRD assumes subscribed users; demo may omit subscription **UI** only).
- **Search** as a product feature (no queries, no results—the bar is visual only).
- Playlists, social, or upload.
- Session-aware **sequence** modeling beyond song-to-song next rec (PRD §5.2)—the UI still surfaces **next_song** as its own surface for logging.
- Production-grade feature stores or third-party analytics SDKs—**in-house only** for the demo.
- Cold-start users/songs (PRD §4)—demo can ignore or seed fake history.

---

## Gaps resolved vs PRD (this pass)

| PRD topic | Was missing / weak in mockup | Now |
|-----------|------------------------------|-----|
| §8.3 `timestamp`, `song_duration_seconds` | Not in event table | Required fields documented |
| §11 CTR / skip by surface | Only “homepage”-style events | `next_song` impressions/clicks + plays tagged by `surface` |
| §11 Qualified listen & skip | Only “duration” vaguely | Tie to `song_duration_seconds` + PRD threshold examples |
| §8.1 / §14 explicit feedback | Was optional | **Like + dislike** on Player, logged |
| §7.1 repetition | Not mentioned | Light dedupe note on Home |

---

## Locked decisions (demo v1)

- **Search:** none—search bar is **visual only** for layout/showcase.
- **Impressions:** **viewport-based** (homepage list and **Up next** list).
- **Player:** **dedicated route**, not overlay.
- **Like / dislike:** **in scope** on Player; both logged. **No `recommendation_id`** on these events—`user_id` + `song_id` + `timestamp` is enough for the demo.
- **Skip:** **Skip** control in Player UI; emit **`skip`** events plus `play_end` for the partial listen.

---

## Open decisions (optional later)

- [ ] Exact URL patterns for Home vs Player (e.g. `/play/:id`).
