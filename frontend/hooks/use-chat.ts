"use client";

import { useState, useCallback, useRef } from "react";
import type { ChatMessage, ChatStatus } from "@/lib/types";

const CHAT_ROUTE = "/api/chat";

function makeId() {
  return Math.random().toString(36).slice(2, 10);
}

export function useChat(researchId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [status, setStatus] = useState<ChatStatus>("idle");
  const abortRef = useRef<AbortController | null>(null);

  const send = useCallback(
    async (content: string) => {
      if (status === "thinking") return;

      const userMsg: ChatMessage = {
        id: makeId(),
        role: "user",
        content,
        createdAt: new Date(),
      };

      // Build updated history before we setState so we can send it
      const updatedHistory = [...messages, userMsg];
      setMessages(updatedHistory);
      setStatus("thinking");

      // Placeholder streaming assistant message
      const assistantId = makeId();
      const assistantMsg: ChatMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        createdAt: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      abortRef.current = new AbortController();

      try {
        const response = await fetch(CHAT_ROUTE, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            research_id: researchId,
            messages: updatedHistory.map((m) => ({
              role: m.role,
              content: m.content,
            })),
          }),
          signal: abortRef.current.signal,
        });

        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`);
        }

        const reader = response.body!.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let accumulated = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          buffer = buffer.replace(/\r\n/g, "\n");

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

            if (event.type === "token") {
              accumulated += event.text as string;
              const text = accumulated;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, content: text } : m
                )
              );
            } else if (event.type === "done") {
              setStatus("idle");
            } else if (event.type === "error") {
              throw new Error(event.message as string);
            }
          }
        }

        setStatus("idle");
      } catch (err: unknown) {
        if (err instanceof Error && err.name === "AbortError") {
          setStatus("idle");
          return;
        }
        const errMsg = err instanceof Error ? err.message : "Unknown error";
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: `Error: ${errMsg}` }
              : m
          )
        );
        setStatus("error");
      }
    },
    [status, messages, researchId]
  );

  const stop = useCallback(() => {
    abortRef.current?.abort();
    setStatus("idle");
  }, []);

  const clear = useCallback(() => {
    abortRef.current?.abort();
    setMessages([]);
    setStatus("idle");
  }, []);

  return { messages, status, send, stop, clear };
}
