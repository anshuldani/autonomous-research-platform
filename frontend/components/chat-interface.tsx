"use client";

import { useState, useEffect } from "react";
import { useResearch } from "@/hooks/use-research";
import { MessageList } from "@/components/message-list";
import { ChatInput } from "@/components/chat-input";
import { PinnedResearch } from "@/components/pinned-research";
import { FollowUpPanel } from "@/components/follow-up-panel";
import { Button } from "@/components/ui/button";

type Mode = "research" | "chat";

export function ChatInterface() {
  const { messages, status, sendTopic, stop, reset } = useResearch();
  const [inputValue, setInputValue] = useState("");
  const [mode, setMode] = useState<Mode>("research");

  // Auto-switch to chat mode when research completes
  useEffect(() => {
    if (status === "done") {
      setMode("chat");
    }
  }, [status]);

  // Find the last completed research result
  const lastResearchMsg = [...messages]
    .reverse()
    .find((m) => m.role === "assistant" && m.result);
  const lastTopic = [...messages]
    .reverse()
    .find((m) => m.role === "user")?.content ?? "";

  function handleNewResearch() {
    reset();
    setMode("research");
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border px-6 py-3">
        <div className="flex items-center gap-2">
          <span className="text-lg">🔬</span>
          <span className="font-semibold text-sm tracking-tight">
            Autonomous Research Platform
          </span>
        </div>
        {(messages.length > 0 || mode === "chat") && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleNewResearch}
            className="text-xs"
          >
            New research
          </Button>
        )}
      </header>

      {mode === "research" ? (
        <>
          {/* Message list */}
          <MessageList messages={messages} onSelectExample={setInputValue} />

          {/* Input */}
          <ChatInput
            value={inputValue}
            onValueChange={setInputValue}
            status={status}
            onSend={sendTopic}
            onStop={stop}
          />
        </>
      ) : (
        <>
          {/* Pinned research summary */}
          {lastResearchMsg?.result && (
            <PinnedResearch
              topic={lastTopic}
              result={lastResearchMsg.result}
            />
          )}

          {/* Follow-up chat panel */}
          {lastResearchMsg?.result?.research_id ? (
            <FollowUpPanel researchId={lastResearchMsg.result.research_id} />
          ) : (
            <div className="flex flex-1 items-center justify-center text-sm text-muted-foreground">
              No research session available. Start a new research.
            </div>
          )}
        </>
      )}
    </div>
  );
}
