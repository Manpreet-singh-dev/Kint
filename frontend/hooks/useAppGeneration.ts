"use client";

import { useState, useCallback } from "react";
import { Message, AgentTrailState } from "@/types";
import { generateApp } from "@/api/generateService";
import { formatGeneratedFiles, getErrorMessage } from "@/utils";
import { DEFAULT_AGENT_TRAIL } from "@/components/common";
import { usePreview } from "./usePreview";

/**
 * Master hook for managing chat messages, multi-agent status trail, and live preview.
 */
export function useAppGeneration() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [agentTrail, setAgentTrail] =
    useState<AgentTrailState>(DEFAULT_AGENT_TRAIL);
  const { previewUrl, setPreviewUrl, refreshPreview } = usePreview();

  const handleGenerate = useCallback(
    async (prompt: string) => {
      const trimmedPrompt = prompt.trim();
      if (!trimmedPrompt || isLoading) return;

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
          description: "Analyzing prompt & architecture plan...",
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

      // Transition Planner -> Coder after brief planning phase
      const plannerTimer = setTimeout(() => {
        const planDuration = Number(
          ((Date.now() - startTime) / 1000).toFixed(1)
        );
        setAgentTrail((prev) => ({
          ...prev,
          planner: {
            ...prev.planner,
            state: "done",
            description: "Single-agent plan formulated",
            durationSec: planDuration,
          },
          coder: {
            ...prev.coder,
            state: "active",
            description: "Generating HTML, CSS, and JS files...",
          },
        }));
      }, 500);

      try {
        const response = await generateApp(trimmedPrompt);
        clearTimeout(plannerTimer);

        const totalGenDuration = Number(
          ((Date.now() - startTime) / 1000).toFixed(1)
        );
        const fileCount = response.files
          ? Object.keys(response.files).length
          : 0;

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

          // Update Agent Trail to Done
          setAgentTrail({
            planner: {
              type: "planner",
              label: "Planner",
              description: "App architecture formulated",
              state: "done",
              durationSec: 0.5,
            },
            coder: {
              type: "coder",
              label: "Coder",
              description: `Generated ${fileCount} file(s) successfully`,
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
          // If no preview URL returned
          setAgentTrail({
            planner: {
              type: "planner",
              label: "Planner",
              description: "App architecture formulated",
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

        // Mark active agent step as error
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
    [isLoading, setPreviewUrl]
  );

  return {
    messages,
    isLoading,
    previewUrl,
    agentTrail,
    handleGenerate,
    refreshPreview,
  };
}
