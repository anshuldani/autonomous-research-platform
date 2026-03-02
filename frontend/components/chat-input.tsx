"use client";

import { useRef, useState, useCallback } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import type { ResearchStatus } from "@/lib/types";

interface Props {
  status: ResearchStatus;
  onSend: (topic: string) => void;
  onStop: () => void;
}

export function ChatInput({ status, onSend, onStop }: Props) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const isResearching = status === "researching";

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || isResearching) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  }, [value, isResearching, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    // Auto-grow textarea
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  };

  return (
    <div className="border-t border-border bg-background px-4 py-3">
      <div className="mx-auto flex max-w-3xl items-end gap-2">
        <Textarea
          id="research-input"
          ref={textareaRef}
          rows={1}
          placeholder="Enter a research topic… (Shift+Enter for new line)"
          value={value}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          disabled={isResearching}
          className="min-h-[44px] resize-none overflow-hidden rounded-xl text-sm"
        />

        {isResearching ? (
          <Button
            variant="destructive"
            size="sm"
            onClick={onStop}
            className="h-11 shrink-0 rounded-xl px-4"
          >
            Stop
          </Button>
        ) : (
          <Button
            size="sm"
            onClick={handleSend}
            disabled={!value.trim()}
            className="h-11 shrink-0 rounded-xl px-4"
          >
            Research
          </Button>
        )}
      </div>

      <p className="mt-1.5 text-center text-[10px] text-muted-foreground">
        AI researches the web, builds a vector knowledge base, and
        self-critiques until quality ≥ 7.5 / 10
      </p>
    </div>
  );
}
