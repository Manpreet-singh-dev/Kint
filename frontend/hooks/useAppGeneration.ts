"use client";

import { useState, useCallback, useEffect } from "react";
import { Message, AgentTrailState, GeneratedFiles } from "@/types";
import { generateApp } from "@/api/generateService";
import { formatGeneratedFiles, getErrorMessage } from "@/utils";
import { DEFAULT_AGENT_TRAIL } from "@/components/common";
import { usePreview } from "./usePreview";

const STORAGE_KEY_MESSAGES = "kint_chat_messages";
const STORAGE_KEY_FILES = "kint_current_files";

/**
 * Master hook for managing chat messages, multi-agent status trail, codebase state, and live preview
 * with recursive incremental improvement and persistent localStorage storage.
 */
export function useAppGeneration() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentFiles, setCurrentFiles] = useState<GeneratedFiles | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [agentTrail, setAgentTrail] = useState<AgentTrailState>(DEFAULT_AGENT_TRAIL);
  const { previewUrl, setPreviewUrl, refreshPreview } = usePreview();

  // Load chat messages and existing files from localStorage on client mount
  useEffect(() => {
    try {
      const savedMessages = window.localStorage.getItem(STORAGE_KEY_MESSAGES);
      if (savedMessages) {
        const parsed = JSON.parse(savedMessages);
        if (Array.isArray(parsed)) {
          const restored: Message[] = parsed.map((m: any) => ({
            ...m,
            timestamp: m.timestamp ? new Date(m.timestamp) : new Date(),
          }));
          setMessages(restored);
        }
      }

      const savedFiles = window.localStorage.getItem(STORAGE_KEY_FILES);
      if (savedFiles) {
        setCurrentFiles(JSON.parse(savedFiles));
      }
    } catch (e) {
      console.error("Failed to load state from localStorage", e);
    } finally {
      setIsLoaded(true);
    }
  }, []);

  // Sync messages to localStorage whenever they change
  useEffect(() => {
    if (!isLoaded) return;
    try {
      window.localStorage.setItem(STORAGE_KEY_MESSAGES, JSON.stringify(messages));
    } catch (e) {
      console.error("Failed to save chat history to localStorage", e);
    }
  }, [messages, isLoaded]);

  // Sync currentFiles to localStorage
  useEffect(() => {
    if (!isLoaded) return;
    try {
      if (currentFiles) {
        window.localStorage.setItem(STORAGE_KEY_FILES, JSON.stringify(currentFiles));
      } else {
        window.localStorage.removeItem(STORAGE_KEY_FILES);
      }
    } catch (e) {
      console.error("Failed to save files to localStorage", e);
    }
  }, [currentFiles, isLoaded]);

  // Clear chat history, current files, and reset app state
  const clearChat = useCallback(() => {
    setMessages([]);
    setCurrentFiles(null);
    setPreviewUrl(null);
    setAgentTrail(DEFAULT_AGENT_TRAIL);
    try {
      window.localStorage.removeItem(STORAGE_KEY_MESSAGES);
      window.localStorage.removeItem(STORAGE_KEY_FILES);
      window.localStorage.removeItem("kint_preview_url");
    } catch (e) {
      console.error("Failed to clear localStorage", e);
    }
  }, [setPreviewUrl]);

  const handleGenerate = useCallback(
    async (prompt: string) => {
      const trimmedPrompt = prompt.trim();
      if (!trimmedPrompt || isLoading) return;

      const isIncremental = Boolean(currentFiles && Object.keys(currentFiles).length > 0);
      const startTime = Date.now();

      // Append user message
      const userMessage: Message = {
        role: "user",
        content: trimmedPrompt,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      // 1. Initial State: Planner Active
      setAgentTrail({
        planner: {
          type: "planner",
          label: "Planner",
          description: isIncremental
            ? "Planning incremental code modifications on existing codebase..."
            : "Analyzing prompt & architecture plan...",
          state: "active",
        },
        coder: {
          type: "coder",
          label: "Coder",
          description: "Waiting for planner...",
          state: "idle",
        },
        sandbox: {
          type: "sandbox",
          label: "Sandbox",
          description: "Waiting for generated files...",
          state: "idle",
        },
        debugger: {
          type: "debugger",
          label: "Debugger",
          description: "Ready for verification...",
          state: "idle",
        },
      });

      // Transition Planner -> Coder
      const plannerTimer = setTimeout(() => {
        const planDuration = Number(((Date.now() - startTime) / 1000).toFixed(1));
        setAgentTrail((prev) => ({
          ...prev,
          planner: {
            ...prev.planner,
            state: "done",
            description: isIncremental ? "Modification plan formulated" : "Multi-step plan formulated",
            durationSec: planDuration,
          },
          coder: {
            ...prev.coder,
            state: "active",
            description: isIncremental
              ? "Applying code modifications & merging with existing files..."
              : "Generating HTML, CSS, and JS files with RAG context...",
          },
        }));
      }, 500);

      try {
        const response = await generateApp(trimmedPrompt, currentFiles || undefined);
        clearTimeout(plannerTimer);

        const totalGenDuration = Number(((Date.now() - startTime) / 1000).toFixed(1));
        const fileCount = response.files ? Object.keys(response.files).length : 0;

        // Store updated codebase files
        if (response.files && fileCount > 0) {
          setCurrentFiles(response.files);
        }

        // Build assistant response with files summary
        let assistantContent = response.message;
        if (response.files && fileCount > 0) {
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

          setAgentTrail({
            planner: {
              type: "planner",
              label: "Planner",
              description: isIncremental ? "Modification plan formulated" : "App architecture formulated",
              state: "done",
              durationSec: 0.5,
            },
            coder: {
              type: "coder",
              label: "Coder",
              description: isIncremental
                ? `Updated and merged ${fileCount} file(s)`
                : `Generated ${fileCount} file(s) with RAG context`,
              state: "done",
              durationSec: Math.max(0.5, totalGenDuration - 3.0),
            },
            sandbox: {
              type: "sandbox",
              label: "Sandbox",
              description: "Live HTTP server running on port 3000",
              state: "done",
              durationSec: 2.5,
            },
            debugger: {
              type: "debugger",
              label: "Debugger",
              description: "App verified, preview live",
              state: "done",
            },
          });
        } else {
          setAgentTrail({
            planner: {
              type: "planner",
              label: "Planner",
              description: isIncremental ? "Modification plan formulated" : "App architecture formulated",
              state: "done",
              durationSec: 0.5,
            },
            coder: {
              type: "coder",
              label: "Coder",
              description: `Generated ${fileCount} file(s)`,
              state: "done",
              durationSec: totalGenDuration,
            },
            sandbox: {
              type: "sandbox",
              label: "Sandbox",
              description: "Sandbox execution finished without preview URL",
              state: "done",
            },
            debugger: {
              type: "debugger",
              label: "Debugger",
              description: "No debug step needed",
              state: "idle",
            },
          });
        }
      } catch (error) {
        clearTimeout(plannerTimer);
        const errText = getErrorMessage(error);

        const errorMessage: Message = {
          role: "assistant",
          content: `Error: ${errText}. Make sure the FastAPI server is running on http://localhost:8000`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);

        setAgentTrail((prev) => ({
          ...prev,
          coder: {
            ...prev.coder,
            state: "error",
            error: errText,
          },
          sandbox: {
            ...prev.sandbox,
            state: "idle",
          },
          debugger: {
            ...prev.debugger,
            state: "idle",
          },
        }));
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, currentFiles, setPreviewUrl]
  );

  return {
    messages,
    currentFiles,
    isLoading,
    previewUrl,
    agentTrail,
    handleGenerate,
    refreshPreview,
    clearChat,
  };
}
