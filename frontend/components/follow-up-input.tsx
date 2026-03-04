"use client";

import { useState, useRef, type KeyboardEvent } from "react";
import type { ChatStatus } from "@/lib/types";

interface Props {
  status: ChatStatus;
  onSend: (content: string) => void;
  onStop: () => void;
}

export function FollowUpInput({ status, onSend, onStop }: Props) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isThinking = status === "thinking";

  function handleSend() {
    const trimmed = value.trim();
    if (!trimmed || isThinking) return;
    onSend(trimmed);
    setValue("");
    textareaRef.current?.focus();
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    setValue(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }

  return (
    <div className="border-t border-border/60 bg-background/80 backdrop-blur px-4 py-4">
      <div className="mx-auto max-w-3xl">
        <div
          className={`input-glow flex items-end gap-3 rounded-2xl border bg-card px-4 py-3 transition-all ${
            isThinking
              ? "border-primary/30 animate-glow-pulse"
              : "border-border hover:border-border/80"
          }`}
        >
          {/* Icon */}
          <div className="mb-0.5 shrink-0">
            <svg
              className={`h-4 w-4 transition-colors ${isThinking ? "text-primary animate-research-pulse" : "text-muted-foreground/60"}`}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </div>

          <textarea
            ref={textareaRef}
            rows={1}
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={isThinking ? "Thinking…" : "Ask about the research above…"}
            disabled={isThinking}
            className="flex-1 resize-none bg-transparent text-sm outline-none placeholder:text-muted-foreground/50 disabled:opacity-50 max-h-[160px] leading-relaxed"
          />

          {isThinking ? (
            <button
              onClick={onStop}
              className="shrink-0 flex h-9 w-9 items-center justify-center rounded-xl bg-destructive/15 text-destructive hover:bg-destructive/25 transition-colors"
              aria-label="Stop"
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
              aria-label="Send"
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
      </div>
    </div>
  );
}
