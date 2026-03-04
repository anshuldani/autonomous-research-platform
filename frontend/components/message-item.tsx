"use client";

import type { Message } from "@/lib/types";
import { QualityBadge } from "@/components/quality-badge";
import { CitationList } from "@/components/citation-list";
import { cn } from "@/lib/utils";

interface Props {
  message: Message;
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

export function MessageItem({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex w-full animate-fade-in-up",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {isUser ? (
        /* ── User bubble ── */
        <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-primary/15 px-4 py-3 text-sm ring-1 ring-primary/25">
          <p className="whitespace-pre-wrap text-foreground/90">{message.content}</p>
        </div>
      ) : (
        /* ── Assistant card ── */
        <div className="w-full max-w-[95%]">
          {message.content ? (
            <div className="rounded-2xl rounded-bl-sm border border-border/60 bg-card shadow-[0_2px_24px_oklch(0_0_0/25%)]">
              {/* Top accent bar */}
              <div className="h-0.5 w-full rounded-t-2xl bg-gradient-to-r from-primary/60 via-primary/30 to-transparent" />

              {/* Report body */}
              <div className="px-5 py-5">
                <div
                  className="prose"
                  dangerouslySetInnerHTML={{
                    __html: `<p>${renderMarkdown(message.content)}</p>`,
                  }}
                />

                {message.result && (
                  <>
                    <QualityBadge
                      qualityHistory={message.result.quality_history}
                      iterations={message.result.iterations}
                    />
                    <CitationList citations={message.result.citations} />
                  </>
                )}
              </div>
            </div>
          ) : (
            /* Thinking state */
            <div className="flex items-center gap-3 rounded-2xl rounded-bl-sm border border-border/40 bg-card px-5 py-4">
              <div className="flex gap-1">
                <span className="h-2 w-2 rounded-full bg-primary/60 animate-bounce [animation-delay:-0.3s]" />
                <span className="h-2 w-2 rounded-full bg-primary/60 animate-bounce [animation-delay:-0.15s]" />
                <span className="h-2 w-2 rounded-full bg-primary/60 animate-bounce" />
              </div>
              <span className="text-xs text-muted-foreground">
                Researching, searching the web, building knowledge base…
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
