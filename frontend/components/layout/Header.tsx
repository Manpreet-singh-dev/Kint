import React from "react";
import { APP_NAME, APP_TAGLINE } from "@/lib/constants";

export interface HeaderProps {
  title?: string;
  subtitle?: string;
  onClearChat?: () => void;
  hasMessages?: boolean;
}

export function Header({
  title = APP_NAME,
  subtitle = APP_TAGLINE,
  onClearChat,
  hasMessages = false,
}: HeaderProps) {
  return (
    <header className="border-b border-zinc-800/80 px-4 py-3 bg-zinc-900/90 backdrop-blur-sm shrink-0 flex items-center justify-between">
      <div className="flex items-center gap-2.5 min-w-0">
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 shadow-md shadow-purple-500/20">
          <span className="text-xs font-bold text-white tracking-wider">K</span>
        </div>
        <div className="min-w-0">
          <div className="flex items-center gap-1.5">
            <h1 className="text-sm font-semibold text-zinc-100 tracking-tight">
              {title}
            </h1>
            <span className="rounded-full bg-indigo-500/10 px-1.5 py-0.5 text-[10px] font-medium text-indigo-400 border border-indigo-500/20">
              v0.1
            </span>
          </div>
          <p className="text-[11px] text-zinc-400 truncate max-w-[210px] leading-tight mt-0.5">
            {subtitle}
          </p>
        </div>
      </div>

      {onClearChat && hasMessages && (
        <button
          onClick={onClearChat}
          title="Start New Chat & Clear History"
          className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-zinc-400 hover:text-zinc-200 bg-zinc-800/60 hover:bg-zinc-800 border border-zinc-700/60 rounded-md transition-colors cursor-pointer"
        >
          <svg
            className="w-3.5 h-3.5 text-zinc-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          <span>New Chat</span>
        </button>
      )}
    </header>
  );
}
