"use client";

import { useState } from "react";
import type { ResearchResult } from "@/lib/types";
import { CitationList } from "@/components/citation-list";

interface Props {
  topic: string;
  result: ResearchResult;
}

function QualityBadgeInline({ score }: { score: number }) {
  const color =
    score >= 8
      ? "bg-green-100 text-green-800 border-green-200"
      : score >= 6
      ? "bg-yellow-100 text-yellow-800 border-yellow-200"
      : "bg-red-100 text-red-800 border-red-200";

  return (
    <span className={`rounded-full border px-2 py-0.5 text-xs font-medium ${color}`}>
      {score.toFixed(1)}/10
    </span>
  );
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
  const [collapsed, setCollapsed] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const finalScore =
    result.quality_history[result.quality_history.length - 1]?.overall ?? 0;

  const PREVIEW_CHARS = 600;
  const isLong = result.summary.length > PREVIEW_CHARS;

  return (
    <div className="mx-auto w-full max-w-3xl px-4 pb-2">
      <div className="rounded-xl border border-border bg-muted/40 shadow-sm overflow-hidden">
        {/* Header row — always visible */}
        <button
          onClick={() => setCollapsed((v) => !v)}
          className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-muted/60 transition-colors"
        >
          <div className="flex items-center gap-2 min-w-0">
            <span className="text-sm font-semibold truncate">{topic}</span>
            <QualityBadgeInline score={finalScore} />
            {result.citations.length > 0 && (
              <span className="text-xs text-muted-foreground hidden sm:inline">
                {result.citations.length} source{result.citations.length !== 1 ? "s" : ""}
              </span>
            )}
          </div>
          <svg
            className={`h-4 w-4 shrink-0 text-muted-foreground transition-transform ${collapsed ? "-rotate-90" : ""}`}
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

        {/* Collapsible body */}
        {!collapsed && (
          <div className="border-t border-border px-4 pb-4 pt-3 overflow-y-auto max-h-[60vh]">
            <div
              className="prose text-sm"
              dangerouslySetInnerHTML={{
                __html: `<p>${renderMarkdown(
                  expanded || !isLong
                    ? result.summary
                    : result.summary.slice(0, PREVIEW_CHARS) + "…"
                )}</p>`,
              }}
            />

            {isLong && (
              <button
                onClick={() => setExpanded((v) => !v)}
                className="mt-2 text-xs font-medium text-primary hover:underline"
              >
                {expanded ? "Show less" : "Read full report"}
              </button>
            )}

            <CitationList citations={result.citations} />
          </div>
        )}
      </div>
    </div>
  );
}
