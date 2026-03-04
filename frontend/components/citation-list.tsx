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
    <div className="mt-3 border-t border-border pt-3">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        <svg
          className={`h-3.5 w-3.5 transition-transform ${expanded ? "rotate-90" : ""}`}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
        <span className="font-medium">
          {citations.length} source{citations.length !== 1 ? "s" : ""}
        </span>
      </button>

      {expanded && (
        <div className="mt-2 flex flex-wrap gap-2">
          {citations.map((citation) => (
            <CitationCard key={citation.url} citation={citation} />
          ))}
        </div>
      )}
    </div>
  );
}
