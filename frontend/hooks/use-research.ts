"use client";

import { useState, useCallback, useRef } from "react";
import type { Message, ResearchResult, ResearchStatus } from "@/lib/types";

// Always call the Next.js proxy route — it forwards to the Python backend.
// In dev this is /api/research on localhost:3000.
const API_ROUTE = "/api/research";

function makeId() {
  return Math.random().toString(36).slice(2, 10);
}

export function useResearch() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [status, setStatus] = useState<ResearchStatus>("idle");
  const abortRef = useRef<AbortController | null>(null);

  const sendTopic = useCallback(async (topic: string) => {
    if (status === "researching") return;

    // Add the user message immediately
    const userMsg: Message = {
      id: makeId(),
      role: "user",
      content: topic,
      createdAt: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setStatus("researching");

    // Placeholder assistant message (streaming into it)
    const assistantId = makeId();
    const assistantMsg: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      createdAt: new Date(),
    };
    setMessages((prev) => [...prev, assistantMsg]);

    abortRef.current = new AbortController();

    try {
      const response = await fetch(API_ROUTE, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic,
          quality_threshold: 7.5,
          max_iterations: 1,
        }),
        signal: abortRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Normalize CRLF → LF so we handle both \n\n and \r\n\r\n separators
        // (sse-starlette v3 uses \r\n\r\n per the SSE spec)
        buffer = buffer.replace(/\r\n/g, "\n");

        // SSE frames are separated by double newlines
        const frames = buffer.split("\n\n");
        buffer = frames.pop() ?? "";

        for (const frame of frames) {
          const dataLine = frame
            .split("\n")
            .find((l) => l.startsWith("data:"));
          if (!dataLine) continue;

          const jsonStr = dataLine.slice(5).trim();
          if (!jsonStr) continue;

          let event: { type: string; [key: string]: unknown };
          try {
            event = JSON.parse(jsonStr);
          } catch {
            continue;
          }

          if (event.type === "result") {
            const result: ResearchResult = {
              summary: event.summary as string,
              quality_history: event.quality_history as ResearchResult["quality_history"],
              iterations: event.iterations as number,
              improvement_history: event.improvement_history as string[],
              citations: (event.sources as ResearchResult["citations"]) ?? [],
              research_id: (event.research_id as string) ?? "",
            };
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, content: result.summary, result }
                  : m
              )
            );
            setStatus("done");
          } else if (event.type === "error") {
            throw new Error(event.message as string);
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") return;
      const errMsg = err instanceof Error ? err.message : "Unknown error";
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                content: `Research failed: ${errMsg}`,
              }
            : m
        )
      );
      setStatus("error");
    }
  }, [status]);

  const stop = useCallback(() => {
    abortRef.current?.abort();
    setStatus("idle");
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setMessages([]);
    setStatus("idle");
  }, []);

  return { messages, status, sendTopic, stop, reset };
}
