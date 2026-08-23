"use client";

import React, { useState } from "react";
import { Message, AgentTrailState } from "@/types";
import { Header } from "@/components/layout";
import { AgentStatusTrail } from "@/components/common";
import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";

export interface ChatPanelProps {
  messages: Message[];
  isLoading: boolean;
  onSend: (prompt: string) => void;
  agentTrail?: AgentTrailState;
  onClearChat?: () => void;
}

export function ChatPanel({
  messages,
  isLoading,
  onSend,
  agentTrail,
  onClearChat,
}: ChatPanelProps) {
  const [inputVal, setInputVal] = useState("");

  const handleSelectSuggestion = (prompt: string) => {
    setInputVal(prompt);
  };

  return (
    <div className="flex w-full h-full flex-col bg-zinc-900 overflow-hidden">
      <Header onClearChat={onClearChat} hasMessages={messages.length > 0} />
      <div className="px-3 pt-3">
        <AgentStatusTrail trail={agentTrail} />
      </div>
      <MessageList
        messages={messages}
        isLoading={isLoading}
        onSelectSuggestion={handleSelectSuggestion}
      />
      <ChatInput
        onSend={onSend}
        isLoading={isLoading}
        externalInput={inputVal}
        onInputChange={setInputVal}
      />
    </div>
  );
}
