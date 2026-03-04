"use client";

const STEPS = [
  { key: "planning",     label: "Plan" },
  { key: "searching",    label: "Search" },
  { key: "synthesising", label: "Synthesise" },
  { key: "scoring",      label: "Score" },
  { key: "refining",     label: "Refine" },
];

const DESCRIPTIONS: Record<string, string> = {
  planning:     "Breaking your topic into research questions",
  searching:    "Querying the live web in parallel",
  synthesising: "Writing a structured report from sources",
  scoring:      "Evaluating depth, relevance and coverage",
  refining:     "Targeted improvement pass underway",
};

const LABELS: Record<string, string> = {
  planning:     "Planning",
  searching:    "Searching",
  synthesising: "Synthesising",
  scoring:      "Scoring",
  refining:     "Refining",
};

interface Props {
  step: string;
}

export function ResearchStatus({ step }: Props) {
  const currentIdx = STEPS.findIndex((s) => s.key === step);
  const visibleSteps = step === "refining" ? STEPS : STEPS.filter((s) => s.key !== "refining");

  return (
    <div className="border-b border-primary/20 bg-primary/5 px-5 py-3.5 animate-fade-in">
      <div className="mx-auto max-w-3xl flex items-center justify-between gap-6">

        {/* Left — pulsing dot + current step label + description */}
        <div className="flex items-center gap-3 min-w-0">
          {/* Ping animation dot */}
          <span className="relative flex h-3 w-3 shrink-0">
            <span className="absolute inline-flex h-full w-full rounded-full bg-primary opacity-60 animate-ping" />
            <span className="relative inline-flex h-3 w-3 rounded-full bg-primary" />
          </span>
          <div className="min-w-0">
            <p className="text-xs font-bold text-foreground tracking-wide">
              {LABELS[step] ?? "Researching"}
            </p>
            <p className="text-[11px] text-muted-foreground truncate">
              {DESCRIPTIONS[step] ?? "Working on your research…"}
            </p>
          </div>
        </div>

        {/* Right — step pill track (hidden on small screens) */}
        <div className="hidden sm:flex items-center gap-1 shrink-0">
          {visibleSteps.map((s, i) => {
            const idx = STEPS.findIndex((x) => x.key === s.key);
            const isDone   = currentIdx > idx;
            const isActive = s.key === step;

            return (
              <div key={s.key} className="flex items-center gap-1">
                {i > 0 && (
                  <div className={`h-px w-3 transition-colors duration-500 ${isDone ? "bg-primary/50" : "bg-border/40"}`} />
                )}
                <div
                  className={`flex items-center gap-1 rounded-full px-2.5 py-1 text-[10px] font-semibold transition-all duration-300 ${
                    isActive
                      ? "bg-primary text-primary-foreground shadow-[0_0_10px_oklch(0.65_0.22_270/40%)]"
                      : isDone
                      ? "bg-primary/20 text-primary"
                      : "bg-muted/40 text-muted-foreground/50"
                  }`}
                >
                  {isDone && (
                    <svg className="h-2.5 w-2.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  )}
                  {s.label}
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </div>
  );
}
