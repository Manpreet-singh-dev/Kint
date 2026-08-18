import React from "react";
import { Message } from "@/types";
import { Badge } from "@/components/ui";
import { formatTime } from "@/utils";

export interface MessageItemProps {
  message: Message;
}

export function MessageItem({ message }: MessageItemProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && <Badge variant="ai">AI</Badge>}

      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 ${
          isUser ? "bg-zinc-100 text-zinc-900" : "bg-zinc-800 text-zinc-50"
        }`}
      >
        <p className="whitespace-pre-wrap text-sm leading-relaxed">
          {message.content}
        </p>
        <span
          className={`mt-1 block text-xs ${
            isUser ? "text-zinc-500" : "text-zinc-400 opacity-70"
          }`}
        >
          {formatTime(message.timestamp)}
        </span>
      </div>

      {isUser && <Badge variant="user">You</Badge>}
    </div>
  );
}
