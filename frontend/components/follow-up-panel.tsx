"use client";

import { useChat } from "@/hooks/use-chat";
import { ChatThread } from "@/components/chat-thread";
import { FollowUpInput } from "@/components/follow-up-input";

interface Props {
  researchId: string;
}

export function FollowUpPanel({ researchId }: Props) {
  const { messages, status, send, stop, clear } = useChat(researchId);

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      {/* Section header */}
      <div className="flex items-center justify-between border-b border-border/40 px-5 py-2.5">
        <div className="flex items-center gap-2">
          <div className="h-1.5 w-1.5 rounded-full bg-primary" />
          <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground/70">
            Follow-up Chat
          </span>
          <span className="rounded-md bg-primary/10 px-1.5 py-0.5 text-[10px] font-medium text-primary/80 ring-1 ring-primary/20">
            RAG-powered
          </span>
        </div>

        {messages.length > 0 && (
          <button
            onClick={clear}
            className="flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors"
          >
            <svg
              className="h-3.5 w-3.5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M3 6h18M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6M10 11v6M14 11v6M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" />
            </svg>
            Clear
          </button>
        )}
      </div>

      {/* Thread */}
      <ChatThread messages={messages} status={status} />

      {/* Input bar */}
      <FollowUpInput status={status} onSend={send} onStop={stop} />
    </div>
  );
}
