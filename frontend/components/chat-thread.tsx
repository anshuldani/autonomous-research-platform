"use client";

import { useEffect, useRef } from "react";
import type { ChatMessage, ChatStatus } from "@/lib/types";
import { ChatBubble } from "@/components/chat-bubble";

interface Props {
  messages: ChatMessage[];
  status: ChatStatus;
}

export function ChatThread({ messages, status }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-2 text-center text-muted-foreground px-4">
        <svg
          className="h-8 w-8 opacity-30"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
        <p className="text-sm">Ask a follow-up question about the research above</p>
      </div>
    );
  }

  const lastAssistantIdx = messages.reduce(
    (acc, m, i) => (m.role === "assistant" ? i : acc),
    -1
  );

  return (
    <div className="flex flex-1 flex-col gap-4 overflow-y-auto px-4 py-4">
      {messages.map((msg, i) => (
        <ChatBubble
          key={msg.id}
          message={msg}
          isStreaming={
            status === "thinking" && i === lastAssistantIdx && msg.role === "assistant"
          }
          status={status}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
