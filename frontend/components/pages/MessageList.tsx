"use client";

import React from "react";
import { Message } from "@/types";
import { BounceDotsLoader } from "@/components/ui";
import { useAutoScroll } from "@/hooks/useAutoScroll";
import { MessageItem } from "./MessageItem";

export interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  onSelectSuggestion?: (prompt: string) => void;
}

const STARTER_SUGGESTIONS = [
  {
    icon: "⏱️",
    title: "Stopwatch & Timer",
    prompt: "Build a clean, modern stopwatch and countdown timer app with lap times, sound alerts, and dark mode.",
  },
  {
    icon: "📋",
    title: "Kanban Board",
    prompt: "Build a Kanban board with 3 columns, task cards with priority badges, drag-and-drop, and localStorage.",
  },
  {
    icon: "📊",
    title: "Expense Tracker",
    prompt: "Build a personal expense tracker with summary cards, transaction filtering, and an HTML5 Canvas pie chart.",
  },
  {
    icon: "🎮",
    title: "Snake Arcade Game",
    prompt: "Build a retro Snake arcade game using HTML5 Canvas with score tracking, speed levels, and touch controls.",
  },
];

export function MessageList({
  messages,
  isLoading,
  onSelectSuggestion,
}: MessageListProps) {
  const scrollRef = useAutoScroll<HTMLDivElement>([messages, isLoading]);

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto px-3.5 py-4 space-y-4 scroll-smooth"
    >
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-6 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-zinc-800/80 border border-zinc-700/60 text-indigo-400 shadow-inner mb-3">
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.75}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
          </div>
          <h2 className="text-sm font-semibold text-zinc-100">
            What do you want to build?
          </h2>
          <p className="mt-1 text-xs text-zinc-400 max-w-[260px] leading-relaxed">
            Describe your idea, and Kint will generate, run, and preview the app live.
          </p>

          {onSelectSuggestion && (
            <div className="mt-5 flex flex-col gap-2 w-full max-w-[290px]">
              <span className="text-[10px] uppercase font-semibold text-zinc-500 tracking-wider text-left pl-1">
                Suggested Starters
              </span>
              {STARTER_SUGGESTIONS.map((item, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => onSelectSuggestion(item.prompt)}
                  className="group flex items-start gap-2.5 rounded-xl border border-zinc-800 bg-zinc-950/60 p-2.5 text-left transition-all hover:bg-zinc-800/70 hover:border-zinc-700/80 cursor-pointer"
                >
                  <span className="text-sm shrink-0">{item.icon}</span>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-medium text-zinc-200 group-hover:text-indigo-300 transition-colors truncate">
                      {item.title}
                    </p>
                    <p className="text-[11px] text-zinc-500 line-clamp-1 leading-snug">
                      {item.prompt}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      ) : (
        messages.map((message, index) => (
          <MessageItem key={index} message={message} />
        ))
      )}

      {/* Loading indicator */}
      {isLoading && (
        <div className="flex items-start gap-2.5 w-full">
          <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 shadow-sm shadow-indigo-500/20 text-white mt-0.5">
            <svg
              className="h-3.5 w-3.5 animate-spin"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          </div>
          <div className="rounded-2xl rounded-tl-xs bg-zinc-950/90 border border-zinc-800/90 px-3.5 py-2.5 shadow-sm">
            <div className="flex items-center gap-2">
              <span className="text-xs text-zinc-400">Generating app...</span>
              <BounceDotsLoader />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
