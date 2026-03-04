import { ChatInterface } from "@/components/chat-interface";

export default function ChatPage() {
  return (
    <div className="relative">
      {/* Ambient background glow */}
      <div className="ambient-glow" />
      <div className="relative z-10">
        <ChatInterface />
      </div>
    </div>
  );
}
