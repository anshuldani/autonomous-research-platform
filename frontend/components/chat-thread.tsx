"use client";

import { useEffect, useRef } from "react";
import type { ChatMessage, ChatStatus } from "@/lib/types";
import { ChatBubble } from "@/components/chat-bubble";

interface Props {
  messages: ChatMessage[];
  status: ChatStatus;
}

const SUGGESTED = [
  "What are the key takeaways?",
  "What are the main limitations or uncertainties?",
  "What should future research focus on?",
];

export function ChatThread({ messages, status }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const lastAssistantIdx = messages.reduce(
    (acc, m, i) => (m.role === "assistant" ? i : acc),
    -1
  );

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-5 px-4 text-center animate-fade-in">
        {/* Icon */}
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 ring-1 ring-primary/20">
          <svg
            className="h-6 w-6 text-primary/70"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </div>

        <div className="space-y-1.5">
          <p className="text-sm font-semibold text-foreground">
            Ask a follow-up question
          </p>
          <p className="max-w-xs text-xs text-muted-foreground leading-relaxed">
            The AI will answer using context from the research above,
            stored in the vector knowledge base.
          </p>
        </div>

        {/* Suggested prompts */}
        <div className="flex flex-col gap-2 w-full max-w-sm">
          {SUGGESTED.map((s) => (
            <div
              key={s}
              className="rounded-xl border border-border/40 bg-muted/20 px-4 py-2.5 text-xs text-muted-foreground text-left"
            >
              {s}
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-1 min-h-0 flex-col gap-4 overflow-y-auto px-4 py-5">
      {messages.map((msg, i) => (
        <ChatBubble
          key={msg.id}
          message={msg}
          isStreaming={
            status === "thinking" &&
            i === lastAssistantIdx &&
            msg.role === "assistant"
          }
          status={status}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
