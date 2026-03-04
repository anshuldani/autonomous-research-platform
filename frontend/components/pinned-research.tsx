"use client";

import { useState } from "react";
import type { ResearchResult } from "@/lib/types";
import { CitationList } from "@/components/citation-list";

interface Props {
  topic: string;
  result: ResearchResult;
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

export function PinnedResearch({ topic, result }: Props) {
  // Start collapsed so the chat panel is immediately visible
  const [collapsed, setCollapsed] = useState(true);
  const [expanded, setExpanded] = useState(false);

  const PREVIEW = 700;
  const isLong = result.summary.length > PREVIEW;

  return (
    <div className="mx-auto w-full max-w-3xl px-4 pt-3 pb-2">
      <div className="overflow-hidden rounded-2xl border border-border/60 bg-card shadow-[0_4px_32px_oklch(0_0_0/30%)]">
        {/* Gradient top bar */}
        <div className="h-0.5 w-full bg-gradient-to-r from-primary/70 via-primary/40 to-transparent" />

        {/* Header */}
        <button
          onClick={() => setCollapsed((v) => !v)}
          className="flex w-full items-center justify-between px-5 py-3.5 text-left hover:bg-muted/20 transition-colors"
        >
          <div className="flex items-center gap-3 min-w-0">
            {/* Topic */}
            <span className="truncate text-sm font-semibold text-foreground">
              {topic}
            </span>

            {/* Inline meta — iterations + sources */}
            <div className="hidden shrink-0 items-center gap-1.5 sm:flex">
              {result.quality_history.length > 0 && (
                <span className="rounded-md bg-muted/60 px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                  {result.quality_history.length} iter{result.quality_history.length !== 1 ? "s" : ""}
                </span>
              )}
              {result.citations.length > 0 && (
                <span className="rounded-md bg-muted/60 px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                  {result.citations.length} sources
                </span>
              )}
              {collapsed && (
                <span className="rounded-md bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary/70 ring-1 ring-primary/20">
                  Click to expand
                </span>
              )}
            </div>
          </div>

          {/* Collapse chevron */}
          <svg
            className={`ml-3 h-4 w-4 shrink-0 text-muted-foreground/60 transition-transform ${collapsed ? "-rotate-180" : ""}`}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="18 15 12 9 6 15" />
          </svg>
        </button>

        {/* Body */}
        {!collapsed && (
          <div className="border-t border-border/40 px-5 pb-5 pt-4 overflow-y-auto max-h-[30vh] animate-fade-in">
            <div
              className="prose text-sm"
              dangerouslySetInnerHTML={{
                __html: `<p>${renderMarkdown(
                  expanded || !isLong
                    ? result.summary
                    : result.summary.slice(0, PREVIEW) + "…"
                )}</p>`,
              }}
            />

            {isLong && (
              <button
                onClick={() => setExpanded((v) => !v)}
                className="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-primary/10 px-3 py-1.5 text-xs font-medium text-primary ring-1 ring-primary/20 hover:bg-primary/20 transition-colors"
              >
                {expanded ? (
                  <>
                    <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
                    Show less
                  </>
                ) : (
                  <>
                    <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
                    Read full report
                  </>
                )}
              </button>
            )}

            <CitationList citations={result.citations} />
          </div>
        )}
      </div>
    </div>
  );
}
