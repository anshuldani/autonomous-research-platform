"use client";

import type { ChatMessage, ChatStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

interface Props {
  message: ChatMessage;
  isStreaming?: boolean;
  status?: ChatStatus;
}

function renderMarkdown(text: string) {
  return text
    .replace(/^### (.+)$/gm, "<h3>$1</h3>")
    .replace(/^## (.+)$/gm, "<h2>$1</h2>")
    .replace(/^# (.+)$/gm, "<h1>$1</h1>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br />");
}

export function ChatBubble({ message, isStreaming }: Props) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex w-full animate-fade-in-up",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {isUser ? (
        /* User bubble — indigo tint */
        <div className="max-w-[78%] rounded-2xl rounded-br-sm bg-primary/15 px-4 py-3 text-sm ring-1 ring-primary/25">
          <p className="whitespace-pre-wrap text-foreground/90 leading-relaxed">{message.content}</p>
        </div>
      ) : (
        /* AI bubble — card surface */
        <div className="max-w-[88%] rounded-2xl rounded-bl-sm border border-border/50 bg-card px-4 py-3 text-sm shadow-[0_2px_16px_oklch(0_0_0/20%)]">
          {message.content ? (
            <>
              <div
                className="prose text-sm"
                dangerouslySetInnerHTML={{
                  __html: `<p>${renderMarkdown(message.content)}</p>`,
                }}
              />
              {isStreaming && (
                <span className="streaming-cursor ml-0.5 inline-block text-primary">▋</span>
              )}
            </>
          ) : (
            /* Thinking state */
            <div className="flex items-center gap-2.5 text-muted-foreground">
              <div className="flex gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-primary/50 animate-bounce [animation-delay:-0.3s]" />
                <span className="h-1.5 w-1.5 rounded-full bg-primary/50 animate-bounce [animation-delay:-0.15s]" />
                <span className="h-1.5 w-1.5 rounded-full bg-primary/50 animate-bounce" />
              </div>
              <span className="text-xs">Thinking…</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
