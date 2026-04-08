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

  return NextResponse.json({ received: events.length });
}
