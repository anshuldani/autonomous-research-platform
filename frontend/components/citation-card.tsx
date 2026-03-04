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
    const origin = new URL(url).origin;
    return `${origin}/favicon.ico`;
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
      className="flex items-start gap-2 rounded-lg border border-border bg-background px-3 py-2 text-xs hover:bg-muted transition-colors group max-w-[240px]"
    >
      {/* Favicon */}
      <img
        src={faviconUrl}
        alt=""
        className="mt-0.5 h-4 w-4 shrink-0 rounded-sm"
        onError={(e) => {
          (e.target as HTMLImageElement).style.display = "none";
        }}
      />

      <div className="min-w-0 flex-1">
        {/* Domain badge */}
        <span className="block truncate font-medium text-muted-foreground">
          {domain}
        </span>
        {/* Title */}
        <span className="block truncate text-foreground group-hover:underline leading-tight mt-0.5">
          {citation.title}
        </span>
      </div>

      {/* External link icon */}
      <svg
        className="shrink-0 mt-0.5 h-3 w-3 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity"
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
