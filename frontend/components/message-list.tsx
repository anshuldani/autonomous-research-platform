"use client";

import { useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageItem } from "@/components/message-item";
import type { Message } from "@/lib/types";

/* ─── Static data ───────────────────────────────────────────────────── */

const STATS = [
  { value: "15+",    label: "Sources per research",   sub: "Web-scraped & ranked" },
  { value: "3",      label: "Iterative refinements",  sub: "Self-critique loop" },
  { value: "7.5/10", label: "Quality threshold",      sub: "Before report finalises" },
  { value: "100%",   label: "AI-automated",           sub: "Zero human intervention" },
];

const STEPS = [
  {
    n: "01",
    title: "Plan & Question",
    body: "The planning agent decomposes your topic into targeted research questions.",
    icon: (
      <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
    ),
  },
  {
    n: "02",
    title: "Web Search",
    body: "Tavily AI searches the live web and returns the most relevant, high-quality sources.",
    icon: (
      <>
        <circle cx="11" cy="11" r="8" />
        <path d="m21 21-4.35-4.35" />
      </>
    ),
  },
  {
    n: "03",
    title: "Vector RAG",
    body: "Documents are chunked, embedded with Voyage AI, and stored in Pinecone for hybrid semantic search.",
    icon: (
      <>
        <ellipse cx="12" cy="5" rx="9" ry="3" />
        <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5" />
        <path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3" />
      </>
    ),
  },
  {
    n: "04",
    title: "Synthesise",
    body: "Claude writes a comprehensive 600+ word report grounded in retrieved context.",
    icon: (
      <>
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
        <polyline points="10 9 9 9 8 9" />
      </>
    ),
  },
  {
    n: "05",
    title: "Critique & Score",
    body: "A separate critic agent scores depth, relevance, clarity and coverage on a 0–10 scale.",
    icon: (
      <>
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </>
    ),
  },
  {
    n: "06",
    title: "Iterate to Threshold",
    body: "If the score falls below 7.5/10 the agent researches gaps and rewrites — up to 3 times.",
    icon: (
      <>
        <polyline points="1 4 1 10 7 10" />
        <path d="M3.51 15a9 9 0 1 0 .49-3.51" />
      </>
    ),
  },
];

const FEATURES = [
  {
    title: "Hybrid Search",
    body: "Combines dense (semantic) and sparse (keyword) retrieval for maximum recall across stored documents.",
    color: "from-violet-500/20 to-indigo-500/10",
    ring: "ring-violet-500/20",
  },
  {
    title: "Self-Critique Loop",
    body: "The critique agent identifies weaknesses and generates targeted follow-up questions to fill knowledge gaps.",
    color: "from-indigo-500/20 to-blue-500/10",
    ring: "ring-indigo-500/20",
  },
  {
    title: "Grounded Follow-up",
    body: "After research, ask unlimited questions. Answers are grounded in the stored Pinecone knowledge base via RAG.",
    color: "from-sky-500/20 to-indigo-500/10",
    ring: "ring-sky-500/20",
  },
  {
    title: "Quality Scoring",
    body: "Every report is scored across four dimensions: depth, relevance, clarity, and coverage — before being delivered.",
    color: "from-emerald-500/20 to-teal-500/10",
    ring: "ring-emerald-500/20",
  },
];

const EXAMPLES = [
  { topic: "CRISPR applications in medicine",          label: "Gene Editing",   delay: "delay-75" },
  { topic: "Impact of microplastics on ocean ecosystems", label: "Marine Science", delay: "delay-150" },
  { topic: "Breakthroughs in quantum computing",       label: "Quantum Tech",   delay: "delay-225" },
];

/* ─── Icons ─────────────────────────────────────────────────────────── */

function Icon({ children }: { children: React.ReactNode }) {
  return (
    <svg
      className="h-5 w-5"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {children}
    </svg>
  );
}

/* ─── Component ─────────────────────────────────────────────────────── */

interface Props {
  messages: Message[];
  onSelectExample: (topic: string) => void;
}

export function MessageList({ messages, onSelectExample }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /* ── Empty / landing state ── */
  if (messages.length === 0) {
    return (
      <div className="flex-1 overflow-y-auto">
        {/* Hero ─────────────────────────────────────────────────────── */}
        <section className="dot-grid flex flex-col items-center justify-center gap-6 px-4 py-16 text-center">
          <div className="animate-fade-in-up space-y-4">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 ring-1 ring-primary/25 shadow-[0_0_40px_oklch(0.65_0.22_270/15%)]">
              <svg className="h-8 w-8 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" /><path d="M11 8v6M8 11h6" />
              </svg>
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">
                <span className="gradient-text-shimmer">Autonomous Research Agent</span>
              </h1>
              <p className="mt-3 mx-auto max-w-lg text-sm leading-relaxed text-muted-foreground">
                An AI agent that searches the live web, builds a vector knowledge base,
                writes a comprehensive report, scores it with a critic model, and
                iteratively improves the quality — fully automated.
              </p>
            </div>
          </div>

          {/* Example topic cards */}
          <div className="flex w-full max-w-2xl flex-col gap-2.5 sm:flex-row mt-2">
            {EXAMPLES.map((ex) => (
              <button
                key={ex.topic}
                onClick={() => onSelectExample(ex.topic)}
                className={`group animate-fade-in-up flex flex-1 flex-col items-start gap-2 rounded-xl border border-border/60 bg-card/60 p-4 text-left transition-all hover:border-primary/40 hover:bg-primary/5 hover:shadow-[0_0_20px_oklch(0.65_0.22_270/10%)] ${ex.delay}`}
              >
                <span className="rounded-md bg-primary/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-widest text-primary/70">
                  {ex.label}
                </span>
                <p className="text-sm font-medium text-foreground leading-snug">{ex.topic}</p>
              </button>
            ))}
          </div>
        </section>

        {/* Stats bar ───────────────────────────────────────────────── */}
        <section className="border-y border-border/40 bg-muted/20 px-4 py-8">
          <div className="mx-auto grid max-w-4xl grid-cols-2 gap-px sm:grid-cols-4">
            {STATS.map((s, i) => (
              <div
                key={s.label}
                className={`animate-fade-in-up flex flex-col items-center gap-1 px-6 py-4 text-center ${
                  i === 0 ? "delay-75" : i === 1 ? "delay-150" : i === 2 ? "delay-225" : ""
                } ${i > 0 ? "border-l border-border/30" : ""}`}
              >
                <span className="gradient-text text-3xl font-bold tabular-nums">{s.value}</span>
                <span className="text-xs font-semibold text-foreground/80">{s.label}</span>
                <span className="text-[10px] text-muted-foreground">{s.sub}</span>
              </div>
            ))}
          </div>
        </section>

        {/* How it works ────────────────────────────────────────────── */}
        <section className="px-4 py-12">
          <div className="mx-auto max-w-4xl">
            <div className="mb-8 text-center">
              <h2 className="text-lg font-bold tracking-tight text-foreground">How it works</h2>
              <p className="mt-1.5 text-sm text-muted-foreground">Six automated steps from topic to verified report</p>
            </div>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {STEPS.map((step, i) => (
                <div
                  key={step.n}
                  className="card-lift group relative overflow-hidden rounded-xl border border-border/50 bg-card/50 p-4 transition-all hover:border-primary/30 hover:bg-card"
                  style={{ animationDelay: `${i * 60}ms` }}
                >
                  {/* Step number watermark */}
                  <span className="absolute right-3 top-2 text-4xl font-black text-primary/5 select-none">
                    {step.n}
                  </span>
                  <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary ring-1 ring-primary/20 group-hover:bg-primary/15 transition-colors">
                    <Icon>{step.icon}</Icon>
                  </div>
                  <h3 className="text-sm font-semibold text-foreground">{step.title}</h3>
                  <p className="mt-1 text-xs leading-relaxed text-muted-foreground">{step.body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features ────────────────────────────────────────────────── */}
        <section className="border-t border-border/40 bg-muted/10 px-4 py-12">
          <div className="mx-auto max-w-4xl">
            <div className="mb-8 text-center">
              <h2 className="text-lg font-bold tracking-tight text-foreground">Key capabilities</h2>
              <p className="mt-1.5 text-sm text-muted-foreground">Production-grade AI research stack</p>
            </div>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {FEATURES.map((f) => (
                <div
                  key={f.title}
                  className={`rounded-xl border bg-gradient-to-br p-5 ${f.color} ${f.ring} ring-1 transition-all hover:scale-[1.01]`}
                >
                  <h3 className="text-sm font-semibold text-foreground">{f.title}</h3>
                  <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">{f.body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Accuracy / tech stack section */}
        <section className="border-t border-border/40 px-4 py-12">
          <div className="mx-auto max-w-4xl">
            <div className="mb-8 text-center">
              <h2 className="text-lg font-bold tracking-tight">Quality scoring breakdown</h2>
              <p className="mt-1.5 text-sm text-muted-foreground">
                Every report is evaluated across four dimensions before delivery
              </p>
            </div>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {[
                { dim: "Depth",     pct: 90, desc: "Thoroughness of coverage and analysis" },
                { dim: "Relevance", pct: 95, desc: "Alignment with the research questions" },
                { dim: "Clarity",   pct: 85, desc: "Writing quality and structure" },
                { dim: "Coverage",  pct: 88, desc: "Breadth across all sub-topics" },
              ].map((d) => (
                <div key={d.dim} className="rounded-xl border border-border/50 bg-card/50 p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-foreground">{d.dim}</span>
                    <span className="score-high text-xs font-bold tabular-nums">{d.pct}%</span>
                  </div>
                  <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-primary/60 to-emerald-500/80"
                      style={{ width: `${d.pct}%` }}
                    />
                  </div>
                  <p className="mt-2 text-[11px] text-muted-foreground leading-snug">{d.desc}</p>
                </div>
              ))}
            </div>

            {/* Tech stack */}
            <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
              {[
                { name: "Claude Sonnet 4.6", role: "Research & Synthesis" },
                { name: "Tavily Search",     role: "Live Web Search" },
                { name: "Pinecone",          role: "Vector Database" },
                { name: "Voyage AI",         role: "Embeddings" },
              ].map((t) => (
                <div key={t.name} className="flex items-center gap-2 rounded-xl border border-border/50 bg-card/40 px-4 py-2.5">
                  <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                  <div>
                    <p className="text-xs font-semibold text-foreground">{t.name}</p>
                    <p className="text-[10px] text-muted-foreground">{t.role}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Footer note */}
        <div className="px-4 py-6 text-center border-t border-border/20">
          <p className="text-[11px] text-muted-foreground/40">
            Autonomous Research Platform · Built with Next.js, FastAPI, and the Anthropic API
          </p>
        </div>
      </div>
    );
  }

  /* ── Message thread ── */
  return (
    <div className="relative flex-1 overflow-hidden">
      <div className="pointer-events-none absolute inset-x-0 top-0 z-10 h-8 bg-gradient-to-b from-background to-transparent" />
      <ScrollArea className="h-full px-4">
        <div className="mx-auto flex max-w-3xl flex-col gap-5 py-8">
          {messages.map((m) => (
            <MessageItem key={m.id} message={m} />
          ))}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>
      <div className="pointer-events-none absolute inset-x-0 bottom-0 z-10 h-8 bg-gradient-to-t from-background to-transparent" />
    </div>
  );
}
