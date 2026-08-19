"use client";

import React, { useState } from "react";
import { Message } from "@/types";
import { formatTime } from "@/utils";

export interface MessageItemProps {
  message: Message;
}

export function MessageItem({ message }: MessageItemProps) {
  const isUser = message.role === "user";
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  // Helper to parse text and code blocks cleanly
  const renderFormattedContent = (content: string) => {
    // If content contains code blocks ```...```
    const parts = content.split(/(```[\s\S]*?```)/g);

    return parts.map((part, idx) => {
      if (part.startsWith("```") && part.endsWith("```")) {
        const lines = part.slice(3, -3).trim().split("\n");
        const languageOrFile = lines[0]?.trim() || "code";
        const codeContent = lines.length > 1 ? lines.slice(1).join("\n") : lines[0];

        return (
          <div
            key={idx}
            className="my-2 overflow-hidden rounded-lg border border-zinc-800 bg-zinc-950/90 text-xs"
          >
            <div className="flex items-center justify-between border-b border-zinc-800/80 bg-zinc-900/80 px-2.5 py-1 text-[11px] text-zinc-400">
              <span className="font-mono text-zinc-300 truncate max-w-[180px]">
                {languageOrFile}
              </span>
              <button
                type="button"
                onClick={() => copyToClipboard(codeContent, idx)}
                className="text-[10px] text-zinc-400 hover:text-zinc-200 transition-colors cursor-pointer"
              >
                {copiedIndex === idx ? "Copied!" : "Copy"}
              </button>
            </div>
            <pre className="max-h-48 overflow-x-auto p-2.5 font-mono text-[11px] text-zinc-300 leading-relaxed">
              <code>{codeContent}</code>
            </pre>
          </div>
        );
      }

      // Regular text formatting
      return (
        <span key={idx} className="whitespace-pre-wrap leading-relaxed">
          {part}
        </span>
      );
    });
  };

  return (
    <div
      className={`flex gap-2.5 w-full ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      {/* Assistant Avatar */}
      {!isUser && (
        <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 shadow-sm shadow-indigo-500/20 text-white mt-0.5">
          <svg
            className="h-3.5 w-3.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
        </div>
      )}

      {/* Message Bubble Container */}
      <div
        className={`flex flex-col ${
          isUser ? "items-end max-w-[88%]" : "items-start max-w-[90%]"
        }`}
      >
        <div
          className={`rounded-2xl px-3.5 py-2.5 text-xs shadow-sm transition-all ${
            isUser
              ? "rounded-tr-xs bg-indigo-600/20 text-indigo-50 border border-indigo-500/30"
              : "rounded-tl-xs bg-zinc-950/90 text-zinc-200 border border-zinc-800/90"
          }`}
        >
          {renderFormattedContent(message.content)}
        </div>

        <span
          className={`mt-1 px-1 text-[10px] select-none ${
            isUser ? "text-indigo-300/60" : "text-zinc-500"
          }`}
        >
          {formatTime(message.timestamp)}
        </span>
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-zinc-800 text-zinc-300 border border-zinc-700 text-[10px] font-semibold mt-0.5">
          You
        </div>
      )}
    </div>
  );
}
