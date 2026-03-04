"use client";

import { useChat } from "@/hooks/use-chat";
import { ChatThread } from "@/components/chat-thread";
import { FollowUpInput } from "@/components/follow-up-input";

interface Props {
  researchId: string;
}

export function FollowUpPanel({ researchId }: Props) {
  const { messages, status, send, stop, clear } = useChat(researchId);

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      {/* Thread — takes remaining height */}
      <ChatThread messages={messages} status={status} />

      {/* Clear button (only when there are messages) */}
      {messages.length > 0 && (
        <div className="flex justify-center px-4 pb-1">
          <button
            onClick={clear}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            Clear conversation
          </button>
        </div>
      )}

      {/* Input bar */}
      <FollowUpInput status={status} onSend={send} onStop={stop} />
    </div>
  );
}
