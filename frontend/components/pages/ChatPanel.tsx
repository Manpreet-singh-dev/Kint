"use client";

import React, { useState } from "react";
import { Message } from "@/types";
import { Header } from "@/components/layout";
import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";

export interface ChatPanelProps {
  messages: Message[];
  isLoading: boolean;
  onSend: (prompt: string) => void;
}

export function ChatPanel({ messages, isLoading, onSend }: ChatPanelProps) {
  const [inputVal, setInputVal] = useState("");

  const handleSelectSuggestion = (prompt: string) => {
    setInputVal(prompt);
  };

  return (
    <div className="flex w-[420px] shrink-0 flex-col border-r border-zinc-800 bg-zinc-900 h-full">
      <Header />
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
