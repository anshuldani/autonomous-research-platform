"use client";

import { Badge } from "@/components/ui/badge";
import type { QualityRecord } from "@/lib/types";

interface Props {
  qualityHistory: QualityRecord[];
  iterations: number;
}

function scoreColor(score: number) {
  if (score >= 8) return "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300";
  if (score >= 6) return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300";
  return "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300";
}

export function QualityBadge({ qualityHistory, iterations }: Props) {
  if (!qualityHistory?.length) return null;

  const first = qualityHistory[0];
  const last = qualityHistory[qualityHistory.length - 1];
  const improved = last.overall - first.overall;

  return (
    <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-border pt-4">
      {/* Final score */}
      <span
        className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${scoreColor(last.overall)}`}
      >
        ★ {last.overall.toFixed(1)} / 10
      </span>

      {/* Iterations */}
      <Badge variant="secondary" className="text-xs">
        {iterations} iteration{iterations !== 1 ? "s" : ""}
      </Badge>

      {/* Improvement delta */}
      {iterations > 1 && (
        <Badge variant="outline" className="text-xs">
          {improved >= 0 ? "+" : ""}
          {improved.toFixed(1)} pts improvement
        </Badge>
      )}

      {/* Per-iteration scores */}
      {qualityHistory.length > 1 && (
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <span>Progression:</span>
          {qualityHistory.map((r, i) => (
            <span key={i}>
              <span className="font-medium text-foreground">
                {r.overall.toFixed(1)}
              </span>
              {i < qualityHistory.length - 1 && (
                <span className="mx-0.5 text-muted-foreground">→</span>
              )}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
