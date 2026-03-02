"use client";

import { useResearch } from "@/hooks/use-research";
import { MessageList } from "@/components/message-list";
import { ChatInput } from "@/components/chat-input";
import { ResearchProgress } from "@/components/research-progress";
import { Button } from "@/components/ui/button";

export function ChatInterface() {
  const { messages, status, progressLines, sendTopic, stop, reset } =
    useResearch();

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
        {messages.length > 0 && (
          <Button variant="ghost" size="sm" onClick={reset} className="text-xs">
            New research
          </Button>
        )}
      </header>

      {/* Messages */}
      <MessageList messages={messages} />

      {/* Live progress stream */}
      {status === "researching" && progressLines.length > 0 && (
        <div className="mx-auto w-full max-w-3xl px-4 pb-2">
          <ResearchProgress lines={progressLines} />
        </div>
      )}

      {/* Input */}
      <ChatInput status={status} onSend={sendTopic} onStop={stop} />
    </div>
  );
}
