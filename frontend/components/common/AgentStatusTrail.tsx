"use client";

import React, { useState, useRef, useEffect } from "react";
import { AgentState, AgentTrailState, AgentType } from "@/types";

export interface AgentStatusTrailProps {
  trail?: AgentTrailState;
  isExpanded?: boolean;
  onToggleExpanded?: () => void;
  className?: string;
}

export const DEFAULT_AGENT_TRAIL: AgentTrailState = {
  planner: {
    type: "planner",
    label: "Planner",
    description: "Breaks prompt into architecture & build steps",
    state: "idle",
  },
  coder: {
    type: "coder",
    label: "Coder",
    description: "Generates HTML, CSS, and JS files",
    state: "idle",
  },
  sandbox: {
    type: "sandbox",
    label: "Sandbox",
    description: "Executes code & starts live preview server",
    state: "idle",
  },
  debugger: {
    type: "debugger",
    label: "Debugger",
    description: "Analyzes runtime errors & applies fixes",
    state: "idle",
  },
};

const AGENT_ICONS: Record<AgentType, { icon: string; color: string }> = {
  planner: { icon: "🧭", color: "from-blue-500 to-indigo-600" },
  coder: { icon: "⚡", color: "from-amber-500 to-orange-600" },
  sandbox: { icon: "📦", color: "from-emerald-500 to-teal-600" },
  debugger: { icon: "🔧", color: "from-purple-500 to-pink-600" },
};

export function AgentStatusTrail({
  trail = DEFAULT_AGENT_TRAIL,
  isExpanded: controlledExpanded,
  onToggleExpanded,
  className = "",
}: AgentStatusTrailProps) {
  // Default closed as requested
  const [internalExpanded, setInternalExpanded] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const isExpanded =
    controlledExpanded !== undefined ? controlledExpanded : internalExpanded;

  const handleToggle = () => {
    if (onToggleExpanded) {
      onToggleExpanded();
    } else {
      setInternalExpanded((prev) => !prev);
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    if (!isExpanded) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        if (onToggleExpanded) {
          onToggleExpanded();
        } else {
          setInternalExpanded(false);
        }
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isExpanded, onToggleExpanded]);

  const steps = Object.values(trail);
  const completedCount = steps.filter((s) => s.state === "done").length;
  const hasActive = steps.some((s) => s.state === "active");
  const hasError = steps.some((s) => s.state === "error");

  const getOverallBadge = () => {
    if (hasError) {
      return (
        <span className="flex items-center gap-1 rounded-full bg-rose-500/10 px-2 py-0.5 text-[10px] font-medium text-rose-400 border border-rose-500/20">
          <span className="h-1.5 w-1.5 rounded-full bg-rose-500" />
          Attention
        </span>
      );
    }
    if (hasActive) {
      return (
        <span className="flex items-center gap-1 rounded-full bg-indigo-500/10 px-2 py-0.5 text-[10px] font-medium text-indigo-400 border border-indigo-500/20 animate-pulse">
          <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-ping" />
          Running
        </span>
      );
    }
    if (completedCount === steps.length && completedCount > 0) {
      return (
        <span className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-400 border border-emerald-500/20">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
          Ready
        </span>
      );
    }
    return (
      <span className="rounded-full bg-zinc-800 px-2 py-0.5 text-[10px] font-medium text-zinc-400 border border-zinc-700/50">
        Idle
      </span>
    );
  };

  const renderStateIcon = (state: AgentState) => {
    switch (state) {
      case "active":
        return (
          <div className="relative flex h-5 w-5 items-center justify-center">
            <span className="absolute h-full w-full rounded-full bg-indigo-500/30 animate-ping" />
            <svg
              className="h-4 w-4 animate-spin text-indigo-400"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="3"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v8H4z"
              />
            </svg>
          </div>
        );
      case "done":
        return (
          <div className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 shadow-xs">
            <svg
              className="h-3 w-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={3}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
        );
      case "error":
        return (
          <div className="flex h-5 w-5 items-center justify-center rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30">
            <svg
              className="h-3 w-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={3}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </div>
        );
      case "idle":
      default:
        return (
          <div className="flex h-5 w-5 items-center justify-center rounded-full bg-zinc-800/80 text-zinc-600 border border-zinc-700/60 text-[10px]">
            <span className="h-1.5 w-1.5 rounded-full bg-zinc-600" />
          </div>
        );
    }
  };

  return (
    <div
      ref={containerRef}
      className={`rounded-xl border border-zinc-800/90 bg-zinc-950/80 shadow-md backdrop-blur-sm overflow-hidden select-none transition-all ${className}`}
    >
      {/* Header Bar */}
      <button
        type="button"
        onClick={handleToggle}
        className="flex w-full items-center justify-between px-3 py-2.5 bg-zinc-900/60 hover:bg-zinc-850 transition-colors cursor-pointer text-left"
      >
        <div className="flex items-center gap-2">
          <div className="flex h-5 w-5 items-center justify-center rounded-md bg-gradient-to-br from-indigo-500 to-purple-600 text-white text-[10px]">
            ✨
          </div>
          <div>
            <h3 className="text-xs font-semibold text-zinc-200">
              Agent Orchestrator
            </h3>
            <p className="text-[10px] text-zinc-500 leading-none">
              {completedCount}/4 Completed
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {getOverallBadge()}
          <svg
            className={`h-3.5 w-3.5 text-zinc-500 transition-transform duration-200 ${
              isExpanded ? "rotate-180" : ""
            }`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </div>
      </button>

      {/* Expanded Trail Content */}
      {isExpanded && (
        <div className="px-3.5 py-3 border-t border-zinc-800/60 space-y-1 relative">
          {/* Vertical Connecting Line */}
          <div className="absolute left-[23px] top-6 bottom-6 w-[1.5px] bg-gradient-to-b from-zinc-800 via-zinc-750 to-zinc-800 -z-0" />

          {steps.map((step) => {
            const meta = AGENT_ICONS[step.type];
            const isActive = step.state === "active";
            const isDone = step.state === "done";
            const isErr = step.state === "error";

            return (
              <div
                key={step.type}
                className={`relative flex items-start gap-2.5 py-1.5 px-1.5 rounded-lg transition-all z-10 ${
                  isActive
                    ? "bg-indigo-950/30 border border-indigo-500/20"
                    : "hover:bg-zinc-900/40"
                }`}
              >
                {/* Node Status Indicator */}
                <div className="shrink-0 mt-0.5 bg-zinc-950 rounded-full p-0.5">
                  {renderStateIcon(step.state)}
                </div>

                {/* Node Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-1">
                    <div className="flex items-center gap-1.5 min-w-0">
                      <span className="text-xs">{meta.icon}</span>
                      <span
                        className={`text-xs font-medium truncate ${
                          isActive
                            ? "text-indigo-300 font-semibold"
                            : isDone
                            ? "text-zinc-200"
                            : isErr
                            ? "text-rose-400 font-semibold"
                            : "text-zinc-400"
                        }`}
                      >
                        {step.label}
                      </span>
                    </div>

                    {/* Duration or State Badge */}
                    {step.durationSec !== undefined && step.durationSec > 0 && (
                      <span className="text-[10px] font-mono text-zinc-500 shrink-0">
                        {step.durationSec}s
                      </span>
                    )}
                  </div>

                  <p
                    className={`text-[11px] leading-tight truncate mt-0.5 ${
                      isActive
                        ? "text-indigo-200/90 font-medium"
                        : isErr
                        ? "text-rose-300/90"
                        : "text-zinc-500"
                    }`}
                  >
                    {step.error || step.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
