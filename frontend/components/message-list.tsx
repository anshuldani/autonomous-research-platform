"use client";

import { useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageItem } from "@/components/message-item";
import type { Message } from "@/lib/types";

const EXAMPLES = [
  {
    topic: "CRISPR applications in medicine",
    label: "Gene Editing",
    icon: (
      <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h18" />
      </svg>
    ),
  },
  {
    topic: "Impact of microplastics on ocean ecosystems",
    label: "Marine Science",
    icon: (
      <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M2 12h20M2 12c3.5-3 7-3 10 0s6.5 3 10 0M2 12c3.5 3 7 3 10 0s6.5-3 10 0" />
      </svg>
    ),
  },
  {
    topic: "Breakthroughs in quantum computing",
    label: "Quantum Tech",
    icon: (
      <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="3" />
        <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" />
      </svg>
    ),
  },
];

interface Props {
  messages: Message[];
  onSelectExample: (topic: string) => void;
}

export function MessageList({ messages, onSelectExample }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-8 px-4 text-center">
        {/* Hero */}
        <div className="animate-fade-in-up space-y-3">
          {/* Icon orb */}
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 ring-1 ring-primary/25 shadow-[0_0_40px_oklch(0.65_0.22_270/15%)]">
            <svg
              className="h-8 w-8 text-primary"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
              <path d="M11 8v6M8 11h6" />
            </svg>
          </div>

          <h1 className="text-2xl font-bold tracking-tight">
            <span className="gradient-text-shimmer">Autonomous Research</span>
          </h1>
          <p className="mx-auto max-w-md text-sm leading-relaxed text-muted-foreground">
            Enter any topic. The agent searches the web, builds a vector
            knowledge base, scores its own output, and iteratively improves
            until it meets the quality threshold.
          </p>

          {/* Pipeline steps */}
          <div className="mx-auto mt-2 flex items-center gap-1.5 text-[11px] text-muted-foreground/70">
            {["Search", "RAG", "Synthesize", "Critique", "Improve"].map((step, i, arr) => (
              <span key={step} className="flex items-center gap-1.5">
                <span className="rounded-md bg-muted/60 px-2 py-0.5 font-medium">
                  {step}
                </span>
                {i < arr.length - 1 && (
                  <svg className="h-3 w-3 text-muted-foreground/40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M5 12h14M12 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </span>
            ))}
          </div>
        </div>

        {/* Example topic cards */}
        <div className="flex w-full max-w-2xl flex-col gap-2.5 sm:flex-row">
          {EXAMPLES.map((ex, i) => (
            <button
              key={ex.topic}
              onClick={() => onSelectExample(ex.topic)}
              className={`group animate-fade-in-up flex flex-1 flex-col items-start gap-2 rounded-xl border border-border bg-card/60 p-4 text-left transition-all hover:border-primary/40 hover:bg-primary/5 hover:shadow-[0_0_20px_oklch(0.65_0.22_270/10%)] ${
                i === 0 ? "delay-75" : i === 1 ? "delay-150" : "delay-225"
              }`}
            >
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary group-hover:bg-primary/20 transition-colors">
                {ex.icon}
              </span>
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/70">
                  {ex.label}
                </p>
                <p className="mt-0.5 text-sm font-medium text-foreground leading-snug">
                  {ex.topic}
                </p>
              </div>
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1 px-4">
      <div className="mx-auto flex max-w-3xl flex-col gap-5 py-8">
        {messages.map((m) => (
          <MessageItem key={m.id} message={m} />
        ))}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
