/**
 * Analytics BFF: validates payloads, then forwards to the catalog API.
 * Only `POST {BACKEND_API_URL}/v1/events` persists rows to `analytics_events` in Postgres.
 */
import { NextResponse } from "next/server";
import type { AnalyticsEvent } from "@/lib/types";

function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null;
}

function looksLikeEvent(v: unknown): v is AnalyticsEvent {
  if (!isRecord(v)) return false;
  return (
    typeof v.user_id === "string" &&
    typeof v.song_id === "string" &&
    typeof v.timestamp === "string" &&
    typeof v.surface === "string" &&
    typeof v.event_type === "string" &&
    typeof v.session_id === "string"
  );
}

function backendUrl(): string | undefined {
  const u = process.env.BACKEND_API_URL;
  return u && u.length > 0 ? u.replace(/\/$/, "") : undefined;
}

export async function POST(request: Request) {
  let raw: unknown;
  try {
    raw = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const items: unknown[] = Array.isArray(raw)
    ? raw
    : isRecord(raw) && Array.isArray(raw.events)
      ? raw.events
      : [raw];

  const events: AnalyticsEvent[] = [];
  for (const item of items) {
    if (looksLikeEvent(item)) events.push(item);
  }

  if (events.length === 0) {
    return NextResponse.json({ error: "No valid events" }, { status: 400 });
  }

  for (const e of events) {
    console.log("[analytics]", JSON.stringify(e));
  }

  const base = backendUrl();
  if (!base) {
    return NextResponse.json(
      {
        error:
          "BACKEND_API_URL is not set. Configure it so this route can call POST /v1/events on the catalog API; only the API writes to analytics_events.",
      },
      { status: 503 },
    );
  }

  const forwardBody = Array.isArray(raw) ? raw : raw;
  try {
    const fr = await fetch(`${base}/v1/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(forwardBody),
    });
    const text = await fr.text();
    if (!fr.ok) {
      return NextResponse.json(
        { error: "Backend rejected events", detail: text },
        { status: 502 },
      );
    }
    try {
      return NextResponse.json(JSON.parse(text) as { received: number });
    } catch {
      return NextResponse.json({ received: events.length });
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json(
      { error: "Failed to reach backend", detail: message },
      { status: 502 },
    );
  }
}
