"use client";

import { useState, useEffect } from "react";
import { useResearch } from "@/hooks/use-research";
import { MessageList } from "@/components/message-list";
import { ChatInput } from "@/components/chat-input";
import { PinnedResearch } from "@/components/pinned-research";
import { FollowUpPanel } from "@/components/follow-up-panel";
import { ResearchStatus } from "@/components/research-status";

type Mode = "research" | "chat";

export function ChatInterface() {
  const { messages, status, step, sendTopic, stop, reset } = useResearch();
  const [inputValue, setInputValue] = useState("");
  const [mode, setMode] = useState<Mode>("research");

  // No auto-switch — user triggers chat mode manually via the CTA button

  const lastResearchMsg = [...messages]
    .reverse()
    .find((m) => m.role === "assistant" && m.result);
  const lastTopic =
    [...messages].reverse().find((m) => m.role === "user")?.content ?? "";

  function handleNewResearch() {
    reset();
    setMode("research");
  }

  const isResearching = status === "researching";

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* ── Header ── */}
      <header className="glass sticky top-0 z-20 flex items-center justify-between px-6 py-3.5">
        <div className="flex items-center gap-3">
          {/* Logo mark */}
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/15 ring-1 ring-primary/30">
            <svg
              className="h-4 w-4 text-primary"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
              <path d="M11 8v6M8 11h6" />
            </svg>
          </div>
          <div>
            <span className="gradient-text font-semibold text-sm tracking-tight">
              Research Agent
            </span>
            <span className="ml-2 hidden text-[10px] text-muted-foreground sm:inline">
              Autonomous · Iterative · RAG-powered
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Research status indicator */}
          {isResearching && (
            <div className="flex items-center gap-2 animate-fade-in">
              <span className="h-2 w-2 rounded-full bg-primary animate-research-pulse" />
              <span className="text-xs text-muted-foreground hidden sm:inline">
                Researching…
              </span>
            </div>
          )}
          {mode === "chat" && !isResearching && (
            <div className="flex items-center gap-2 animate-fade-in">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              <span className="text-xs text-muted-foreground hidden sm:inline">
                Research complete
              </span>
            </div>
          )}

          {(messages.length > 0 || mode === "chat") && (
            <button
              onClick={handleNewResearch}
              className="rounded-lg border border-border px-3 py-1.5 text-xs text-muted-foreground transition-all hover:border-primary/50 hover:text-primary hover:bg-primary/5"
            >
              + New research
            </button>
          )}
        </div>
      </header>

      {/* ── Research progress status ── */}
      {isResearching && <ResearchStatus step={step} />}

      {/* ── Modes ── */}
      {mode === "research" ? (
        <div className="flex flex-1 flex-col overflow-hidden">
          <MessageList messages={messages} onSelectExample={setInputValue} />

          {status === "done" && lastResearchMsg?.result?.research_id ? (
            /* ── Research done — invite to chat ── */
            <div className="border-t border-border/40 bg-card/30 px-4 py-4 animate-fade-in">
              <div className="mx-auto flex max-w-3xl items-center justify-between gap-4">
                <p className="text-sm text-muted-foreground">
                  Report complete. Ask follow-up questions grounded in the research.
                </p>
                <button
                  onClick={() => setMode("chat")}
                  className="shrink-0 flex items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow-[0_0_20px_oklch(0.65_0.22_270/25%)] transition-all hover:bg-primary/90 hover:shadow-[0_0_28px_oklch(0.65_0.22_270/35%)]"
                >
                  Chat about this
                  <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>
          ) : (
            <ChatInput
              value={inputValue}
              onValueChange={setInputValue}
              status={status}
              onSend={sendTopic}
              onStop={stop}
            />
          )}
        </div>
      ) : (
        <div className="flex flex-1 flex-col overflow-hidden min-h-0 animate-fade-in">
          {/* Pinned card — shrink-0 so it never steals flex space from chat */}
          {lastResearchMsg?.result && (
            <div className="shrink-0">
              <PinnedResearch topic={lastTopic} result={lastResearchMsg.result} />
            </div>
          )}
          {/* Chat panel — flex-1 min-h-0 so it fills ALL remaining height */}
          {lastResearchMsg?.result?.research_id ? (
            <div className="flex flex-1 flex-col min-h-0 overflow-hidden">
              <FollowUpPanel researchId={lastResearchMsg.result.research_id} />
            </div>
          ) : (
            <div className="flex flex-1 items-center justify-center text-sm text-muted-foreground">
              No research session found. Start a new research.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
