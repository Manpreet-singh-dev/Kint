"use client";

import React from "react";
import { Message } from "@/types";
import { Badge, BounceDotsLoader } from "@/components/ui";
import { EmptyState } from "@/components/common";
import { useAutoScroll } from "@/hooks/useAutoScroll";
import { MessageItem } from "./MessageItem";

export interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  onSelectSuggestion?: (prompt: string) => void;
}

export function MessageList({
  messages,
  isLoading,
  onSelectSuggestion,
}: MessageListProps) {
  const scrollRef = useAutoScroll<HTMLDivElement>([messages, isLoading]);

  return (
    <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-8">
      <div className="space-y-6">
        {messages.length === 0 ? (
          <EmptyState
            icon={
              <svg
                className="h-12 w-12"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            }
            title="Start a new conversation"
            description='Describe the app you want to build. For example: "Build a todo list app with categories"'
          >
            {onSelectSuggestion && (
              <div className="flex flex-col gap-2 max-w-xs mx-auto">
                <button
                  type="button"
                  onClick={() =>
                    onSelectSuggestion("Build a todo list app with categories and local storage")
                  }
                  className="rounded-lg border border-zinc-800 bg-zinc-850 px-3 py-2 text-xs text-zinc-300 hover:bg-zinc-800 hover:border-zinc-700 transition-colors text-left cursor-pointer"
                >
                  💡 Todo list app with categories
                </button>
                <button
                  type="button"
                  onClick={() =>
                    onSelectSuggestion("Create a stopwatch app with lap times and dark mode")
                  }
                  className="rounded-lg border border-zinc-800 bg-zinc-850 px-3 py-2 text-xs text-zinc-300 hover:bg-zinc-800 hover:border-zinc-700 transition-colors text-left cursor-pointer"
                >
                  ⏱️ Stopwatch with lap times
                </button>
              </div>
            )}
          </EmptyState>
        ) : (
          messages.map((message, index) => (
            <MessageItem key={index} message={message} />
          ))
        )}

        {isLoading && (
          <div className="flex gap-3">
            <Badge variant="ai">AI</Badge>
            <div className="max-w-[85%] rounded-2xl bg-zinc-800 px-4 py-3">
              <BounceDotsLoader />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
