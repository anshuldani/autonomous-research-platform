"use client";

import type { Citation } from "@/lib/types";

interface Props {
  citation: Citation;
}

function getDomain(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

function getFaviconUrl(url: string): string {
  try {
    return `https://www.google.com/s2/favicons?domain=${new URL(url).hostname}&sz=32`;
  } catch {
    return "";
  }
}

export function CitationCard({ citation }: Props) {
  const domain = getDomain(citation.url);
  const faviconUrl = getFaviconUrl(citation.url);

  return (
    <a
      href={citation.url}
      target="_blank"
      rel="noopener noreferrer"
      className="group flex items-start gap-2.5 rounded-xl border border-border/60 bg-muted/30 px-3 py-2.5 text-xs transition-all hover:border-primary/40 hover:bg-primary/5 hover:shadow-[0_0_12px_oklch(0.65_0.22_270/8%)] w-[220px] shrink-0"
    >
      {/* Favicon */}
      <img
        src={faviconUrl}
        alt=""
        className="mt-0.5 h-4 w-4 shrink-0 rounded"
        onError={(e) => {
          (e.target as HTMLImageElement).style.display = "none";
        }}
      />

      <div className="min-w-0 flex-1">
        <span className="block truncate text-[10px] font-semibold uppercase tracking-wide text-muted-foreground/60">
          {domain}
        </span>
        <span className="mt-0.5 block truncate text-foreground/80 leading-snug group-hover:text-foreground transition-colors">
          {citation.title}
        </span>
      </div>

      {/* External link */}
      <svg
        className="mt-0.5 h-3 w-3 shrink-0 text-muted-foreground/30 opacity-0 group-hover:opacity-100 transition-opacity"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
        <polyline points="15 3 21 3 21 9" />
        <line x1="10" y1="14" x2="21" y2="3" />
      </svg>
    </a>
  );
}
