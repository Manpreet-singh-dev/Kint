"use client";

import React, { useState, FormEvent, KeyboardEvent, useRef, useEffect } from "react";
import { Button, Spinner } from "@/components/ui";

export interface ChatInputProps {
  onSend: (prompt: string) => void;
  isLoading: boolean;
  externalInput?: string;
  onInputChange?: (value: string) => void;
}

export function ChatInput({
  onSend,
  isLoading,
  externalInput,
  onInputChange,
}: ChatInputProps) {
  const [internalInput, setInternalInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const input = externalInput !== undefined ? externalInput : internalInput;

  const setInputValue = (val: string) => {
    if (onInputChange) {
      onInputChange(val);
    } else {
      setInternalInput(val);
    }
  };

  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        140
      )}px`;
    }
  }, [input]);

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    onSend(input);
    setInputValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      e.currentTarget.form?.requestSubmit();
    }
  };

  return (
    <div className="border-t border-zinc-800/80 p-3 bg-zinc-900/95 shrink-0 select-none">
      <form
        onSubmit={handleSubmit}
        className="relative flex flex-col rounded-xl border border-zinc-800 bg-zinc-950/90 shadow-inner transition-colors focus-within:border-indigo-500/60 focus-within:ring-1 focus-within:ring-indigo-500/30"
      >
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe an app to build..."
          rows={1}
          disabled={isLoading}
          className="w-full resize-none bg-transparent px-3.5 pt-3 pb-8 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none disabled:opacity-50"
        />

        {/* Input Bottom Bar */}
        <div className="flex items-center justify-between px-2.5 pb-2">
          <span className="text-[10px] text-zinc-500">
            {isLoading ? "Building..." : "↵ Send"}
          </span>

          <Button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={`h-7 w-7 rounded-lg p-0 transition-all ${
              input.trim() && !isLoading
                ? "bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md shadow-indigo-500/20 hover:opacity-90"
                : "bg-zinc-800 text-zinc-500 border border-zinc-700/50"
            }`}
            aria-label="Send prompt"
          >
            {isLoading ? (
              <Spinner className="h-3.5 w-3.5 text-zinc-400" />
            ) : (
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
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
