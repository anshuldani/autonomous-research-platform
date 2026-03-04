"use client";

import type { QualityRecord } from "@/lib/types";

interface Props {
  qualityHistory: QualityRecord[];
  iterations: number;
}

function scoreClass(score: number) {
  if (score >= 8) return { text: "score-high", bg: "score-bg-high" };
  if (score >= 6) return { text: "score-mid",  bg: "score-bg-mid" };
  return           { text: "score-low",  bg: "score-bg-low" };
}

function ScoreBar({ score }: { score: number }) {
  const pct = Math.min(100, (score / 10) * 100);
  const { text } = scoreClass(score);
  return (
    <div className="h-1 w-24 rounded-full bg-muted overflow-hidden">
      <div
        className={`h-full rounded-full transition-all ${text === "score-high" ? "bg-emerald-500" : text === "score-mid" ? "bg-amber-500" : "bg-rose-500"}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

export function QualityBadge({ qualityHistory, iterations }: Props) {
  if (!qualityHistory?.length) return null;

  const first = qualityHistory[0];
  const last = qualityHistory[qualityHistory.length - 1];
  const improved = last.overall - first.overall;
  const { text: textClass, bg: bgClass } = scoreClass(last.overall);

  return (
    <div className="mt-5 rounded-xl border border-border/60 bg-muted/30 p-4 animate-fade-in">
      <div className="flex flex-wrap items-start gap-4">
        {/* Score block */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] uppercase tracking-widest text-muted-foreground/70 font-semibold">
            Quality Score
          </span>
          <div className="flex items-baseline gap-1.5">
            <span className={`text-2xl font-bold tabular-nums ${textClass}`}>
              {last.overall.toFixed(1)}
            </span>
            <span className="text-xs text-muted-foreground">/&nbsp;10</span>
          </div>
          <ScoreBar score={last.overall} />
        </div>

        {/* Divider */}
        <div className="h-12 w-px bg-border/60 hidden sm:block" />

        {/* Iterations & improvement */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] uppercase tracking-widest text-muted-foreground/70 font-semibold">
            Iterations
          </span>
          <div className="flex items-center gap-2">
            {qualityHistory.map((r, i) => (
              <span key={i} className="flex items-center gap-1.5">
                <span className={`inline-flex h-7 w-7 items-center justify-center rounded-lg text-xs font-semibold border ${scoreClass(r.overall).bg}`}>
                  {r.overall.toFixed(1)}
                </span>
                {i < qualityHistory.length - 1 && (
                  <svg className="h-3 w-3 text-muted-foreground/40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                )}
              </span>
            ))}
          </div>
          {iterations > 1 && (
            <span className={`text-xs font-medium ${improved >= 0 ? "score-high" : "score-low"}`}>
              {improved >= 0 ? "+" : ""}{improved.toFixed(1)} pts over {iterations} iterations
            </span>
          )}
        </div>

        {/* Sub-scores */}
        {last.scores && (
          <>
            <div className="h-12 w-px bg-border/60 hidden lg:block" />
            <div className="hidden lg:flex flex-col gap-1.5">
              <span className="text-[10px] uppercase tracking-widest text-muted-foreground/70 font-semibold">
                Breakdown
              </span>
              <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-xs text-muted-foreground">
                {[
                  ["Depth",     last.scores.depth_score],
                  ["Relevance", last.scores.relevance_score],
                  ["Clarity",   last.scores.clarity_score],
                  ["Coverage",  last.scores.coverage_score],
                ].map(([label, val]) => (
                  <div key={label as string} className="flex items-center justify-between gap-3">
                    <span>{label}</span>
                    <span className={`font-semibold tabular-nums ${scoreClass(val as number).text}`}>
                      {(val as number).toFixed(1)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
