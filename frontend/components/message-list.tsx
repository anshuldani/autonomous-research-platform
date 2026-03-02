"use client";

import { useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageItem } from "@/components/message-item";
import type { Message } from "@/lib/types";

interface Props {
  messages: Message[];
}

export function MessageList({ messages }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 text-center">
        <div className="text-4xl">🔬</div>
        <h2 className="text-lg font-semibold">Autonomous Research Platform</h2>
        <p className="max-w-sm text-sm text-muted-foreground">
          Enter any research topic below. The AI will search the web, build a
          knowledge base, score its own output, and iteratively improve it until
          it meets the quality threshold.
        </p>
        <div className="mt-2 flex flex-wrap justify-center gap-2">
          {[
            "CRISPR applications in medicine",
            "Impact of microplastics on ocean ecosystems",
            "Breakthroughs in quantum computing",
          ].map((example) => (
            <button
              key={example}
              className="rounded-full border border-border px-3 py-1 text-xs text-muted-foreground transition-colors hover:border-primary hover:text-primary"
              onClick={() => {
                const input = document.getElementById(
                  "research-input"
                ) as HTMLTextAreaElement | null;
                if (input) {
                  input.value = example;
                  input.dispatchEvent(new Event("input", { bubbles: true }));
                  input.focus();
                }
              }}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1 px-4">
      <div className="mx-auto flex max-w-3xl flex-col gap-4 py-6">
        {messages.map((m) => (
          <MessageItem key={m.id} message={m} />
        ))}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
