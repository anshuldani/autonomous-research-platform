"use client";

import { useState } from "react";
import type { Citation } from "@/lib/types";
import { CitationCard } from "@/components/citation-card";

interface Props {
  citations: Citation[];
}

export function CitationList({ citations }: Props) {
  const [expanded, setExpanded] = useState(false);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-4 border-t border-border/40 pt-4">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="group flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        <span className="flex h-5 w-5 items-center justify-center rounded-md bg-primary/10 text-primary ring-1 ring-primary/20 text-[10px] font-bold">
          {citations.length}
        </span>
        <span className="font-medium">
          {expanded ? "Hide" : "Show"} sources
        </span>
        <svg
          className={`h-3.5 w-3.5 text-muted-foreground/60 transition-transform ${expanded ? "rotate-180" : ""}`}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {expanded && (
        <div className="mt-3 flex gap-2 overflow-x-auto pb-1 animate-fade-in">
          {citations.map((citation) => (
            <CitationCard key={citation.url} citation={citation} />
          ))}
        </div>
      )}
    </div>
  );
}
