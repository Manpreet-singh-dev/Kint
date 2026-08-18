"use client";

import React, { useState, FormEvent, KeyboardEvent } from "react";
import { Button, Textarea } from "@/components/ui";

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
  const input = externalInput !== undefined ? externalInput : internalInput;

  const setInputValue = (val: string) => {
    if (onInputChange) {
      onInputChange(val);
    } else {
      setInternalInput(val);
    }
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    onSend(input);
    setInputValue("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      e.currentTarget.form?.requestSubmit();
    }
  };

  return (
    <div className="border-t border-zinc-800 px-6 py-4 bg-zinc-900">
      <form onSubmit={handleSubmit} className="flex gap-3">
        <Textarea
          value={input}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe the app you want to build..."
          rows={1}
          disabled={isLoading}
        />
        <Button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="h-14 w-14 shrink-0 rounded-xl"
          aria-label="Send prompt"
        >
          <svg
            className="h-5 w-5"
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
        </Button>
      </form>
      <p className="mt-3 text-center text-xs text-zinc-500">
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
}
