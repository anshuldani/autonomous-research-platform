import { NextRequest, NextResponse } from "next/server";

export const maxDuration = 600;
export const dynamic = "force-dynamic";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

/**
 * POST /api/chat
 *
 * Proxies the chat request to the Python FastAPI backend and pipes the
 * SSE token stream back to the browser.
 */
export async function POST(req: NextRequest) {
  const body = await req.json();

  let backendRes: Response;
  try {
    backendRes = await fetch(`${BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    return NextResponse.json(
      { error: "Could not reach research backend. Is it running?" },
      { status: 502 }
    );
  }

  if (!backendRes.ok) {
    const text = await backendRes.text();
    return NextResponse.json({ error: text }, { status: backendRes.status });
  }

  return new NextResponse(backendRes.body, {
    status: 200,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
