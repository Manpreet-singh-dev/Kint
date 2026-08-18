"use client";

import { useState, useCallback } from "react";
import { Message } from "@/types";
import { generateApp } from "@/api/generateService";
import { formatGeneratedFiles, getErrorMessage } from "@/utils";
import { usePreview } from "./usePreview";

/**
 * Master hook for managing chat messages, code generation state, and live preview.
 */
export function useAppGeneration() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { previewUrl, setPreviewUrl, refreshPreview } = usePreview();

  const handleGenerate = useCallback(
    async (prompt: string) => {
      const trimmedPrompt = prompt.trim();
      if (!trimmedPrompt || isLoading) return;

      // Append user message
      const userMessage: Message = {
        role: "user",
        content: trimmedPrompt,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        const response = await generateApp(trimmedPrompt);

        // Build assistant response with files summary
        let assistantContent = response.message;
        if (response.files && Object.keys(response.files).length > 0) {
          assistantContent += formatGeneratedFiles(response.files);
        }

        const assistantMessage: Message = {
          role: "assistant",
          content: assistantContent,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMessage]);

        if (response.preview_url) {
          setPreviewUrl(response.preview_url);
        }
      } catch (error) {
        const errorMessage: Message = {
          role: "assistant",
          content: `Error: ${getErrorMessage(
            error
          )}. Make sure the FastAPI server is running on http://localhost:8000`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, setPreviewUrl]
  );

  return {
    messages,
    isLoading,
    previewUrl,
    handleGenerate,
    refreshPreview,
  };
}
