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

export function ChatBubble({ message, isStreaming, status }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[85%] rounded-2xl px-4 py-3 text-sm",
          isUser
            ? "bg-primary text-primary-foreground rounded-br-sm"
            : "bg-muted text-foreground rounded-bl-sm"
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : message.content ? (
          <div className="prose">
            <span
              dangerouslySetInnerHTML={{
                __html: `<p>${renderMarkdown(message.content)}</p>`,
              }}
            />
            {isStreaming && (
              <span className="streaming-cursor ml-0.5 inline-block">▋</span>
            )}
          </div>
        ) : (
          <div className="flex items-center gap-2 text-muted-foreground">
            <span className="inline-flex gap-1">
              <span className="animate-bounce [animation-delay:-0.3s]">·</span>
              <span className="animate-bounce [animation-delay:-0.15s]">·</span>
              <span className="animate-bounce">·</span>
            </span>
            <span className="text-xs">Thinking…</span>
          </div>
        )}
      </div>
    </div>
  );
}
