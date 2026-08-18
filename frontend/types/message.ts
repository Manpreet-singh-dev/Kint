export type MessageRole = "user" | "assistant";

export interface Message {
  role: MessageRole;
  content: string;
  timestamp: Date;
}

export type GeneratedFiles = Record<string, string>;
