"use client";

import { useRef, useCallback } from "react";
import type { ResearchStatus } from "@/lib/types";

interface Props {
  value: string;
  onValueChange: (v: string) => void;
  status: ResearchStatus;
  onSend: (topic: string) => void;
  onStop: () => void;
}

export function ChatInput({ value, onValueChange, status, onSend, onStop }: Props) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isResearching = status === "researching";

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || isResearching) return;
    onSend(trimmed);
    onValueChange("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  }, [value, isResearching, onSend, onValueChange]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onValueChange(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  };

  return (
    <div className="border-t border-border/60 bg-background/80 backdrop-blur px-4 py-4">
      <div className="mx-auto max-w-3xl">
        {/* Input surface */}
        <div className={`input-glow flex items-end gap-3 rounded-2xl border bg-card px-4 py-3 transition-all ${
          isResearching
            ? "border-primary/30 animate-glow-pulse"
            : "border-border hover:border-border/80"
        }`}>
          {/* Icon */}
          <div className="mb-0.5 shrink-0">
            <svg
              className={`h-4 w-4 transition-colors ${isResearching ? "text-primary animate-research-pulse" : "text-muted-foreground"}`}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
          </div>

          {/* Textarea */}
          <textarea
            ref={textareaRef}
            rows={1}
            placeholder={
              isResearching
                ? "Research in progress…"
                : "Enter a research topic…  (Shift + Enter for new line)"
            }
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            disabled={isResearching}
            className="flex-1 resize-none bg-transparent text-sm outline-none placeholder:text-muted-foreground/60 disabled:opacity-50 max-h-[200px] leading-relaxed"
          />

          {/* Action button */}
          {isResearching ? (
            <button
              onClick={onStop}
              className="shrink-0 flex h-9 w-9 items-center justify-center rounded-xl bg-destructive/15 text-destructive hover:bg-destructive/25 transition-colors"
              aria-label="Stop research"
            >
              <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="6" width="12" height="12" rx="1" />
              </svg>
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!value.trim()}
              className="shrink-0 flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-[0_0_16px_oklch(0.65_0.22_270/30%)] hover:bg-primary/90 disabled:opacity-30 disabled:shadow-none transition-all"
              aria-label="Start research"
            >
              <svg
                className="h-3.5 w-3.5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          )}
        </div>

        {/* Footer hint */}
        <p className="mt-2 text-center text-[10px] text-muted-foreground/50">
          Searches the web · builds a vector knowledge base · self-critiques until quality ≥ 7.5 / 10
        </p>
      </div>
    </div>
  );
}
