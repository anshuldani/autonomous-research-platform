import { NextRequest, NextResponse } from "next/server";

// Research can take 3-5 minutes — raise the route timeout to 10 minutes.
// Without this Next.js kills the handler after 30 s, cutting the SSE stream.
export const maxDuration = 600;
export const dynamic = "force-dynamic";

const BACKEND_URL =
  process.env.BACKEND_URL ?? "http://localhost:8000";

/**
 * POST /api/research
 *
 * Proxies the request body to the Python FastAPI backend and pipes the
 * SSE stream straight back to the browser.  Keeping this as a thin proxy
 * means the ANTHROPIC / TAVILY / PINECONE keys never need to be in the
 * Next.js environment — they stay on the Python side.
 */
export async function POST(req: NextRequest) {
  const body = await req.json();

  let backendRes: Response;
  try {
    backendRes = await fetch(`${BACKEND_URL}/api/research`, {
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
    return NextResponse.json(
      { error: text },
      { status: backendRes.status }
    );
  }

  // Pipe the SSE stream from Python → browser
  return new NextResponse(backendRes.body, {
    status: 200,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
