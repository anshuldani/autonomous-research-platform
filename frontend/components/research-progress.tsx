"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import { useEffect, useRef } from "react";

interface Props {
  lines: string[];
}

export function ResearchProgress({ lines }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

  if (lines.length === 0) return null;

  return (
    <div className="rounded-xl border border-border bg-muted/40 p-3">
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Live progress
      </p>
      <ScrollArea className="h-36">
        <div className="space-y-0.5 font-mono text-xs text-muted-foreground">
          {lines.map((line, i) => (
            <p key={i} className="leading-5">
              {line}
            </p>
          ))}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>
    </div>
  );
}
