"use client";

import React from "react";
import { Button } from "@/components/ui";

export type ViewportMode = "desktop" | "tablet" | "mobile";

export interface PreviewHeaderProps {
  previewUrl: string | null;
  onRefresh: () => void;
  viewportMode?: ViewportMode;
  onViewportChange?: (mode: ViewportMode) => void;
}

export function PreviewHeader({
  previewUrl,
  onRefresh,
  viewportMode = "desktop",
  onViewportChange,
}: PreviewHeaderProps) {
  return (
    <div className="flex items-center justify-between border-b border-zinc-800/80 bg-zinc-900/90 backdrop-blur-sm px-4 py-2.5 shrink-0 select-none">
      {/* Left: Window dots & Refresh */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 mr-1">
          <span className="h-2.5 w-2.5 rounded-full bg-zinc-700/80 hover:bg-rose-500/80 transition-colors" />
          <span className="h-2.5 w-2.5 rounded-full bg-zinc-700/80 hover:bg-amber-500/80 transition-colors" />
          <span className="h-2.5 w-2.5 rounded-full bg-zinc-700/80 hover:bg-emerald-500/80 transition-colors" />
        </div>

        <Button
          variant="icon"
          onClick={onRefresh}
          disabled={!previewUrl}
          title="Refresh preview"
          aria-label="Refresh preview"
          className="h-7 w-7 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/80 disabled:opacity-30 rounded-md"
        >
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
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
        </Button>
      </div>

      {/* Middle: Browser Chrome URL Bar */}
      <div className="flex-1 max-w-md mx-3">
        <div className="flex items-center gap-2 rounded-lg bg-zinc-950/80 border border-zinc-800 px-3 py-1 text-xs text-zinc-400 font-mono shadow-inner">
          <svg
            className={`h-3.5 w-3.5 shrink-0 ${
              previewUrl ? "text-emerald-400" : "text-zinc-600"
            }`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
            />
          </svg>
          <span className="truncate flex-1 text-[11px]">
            {previewUrl || "https://preview.local"}
          </span>
          {previewUrl && (
            <span className="flex h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
          )}
        </div>
      </div>

      {/* Right: Viewport mode toggles & Open in new tab */}
      <div className="flex items-center gap-2">
        {onViewportChange && (
          <div className="flex items-center rounded-md bg-zinc-950 border border-zinc-800 p-0.5">
            <button
              onClick={() => onViewportChange("desktop")}
              className={`px-2 py-1 rounded text-[11px] font-medium transition-colors ${
                viewportMode === "desktop"
                  ? "bg-zinc-800 text-zinc-100 shadow-sm"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
              title="Desktop view"
            >
              Desktop
            </button>
            <button
              onClick={() => onViewportChange("tablet")}
              className={`px-2 py-1 rounded text-[11px] font-medium transition-colors ${
                viewportMode === "tablet"
                  ? "bg-zinc-800 text-zinc-100 shadow-sm"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
              title="Tablet view"
            >
              Tablet
            </button>
            <button
              onClick={() => onViewportChange("mobile")}
              className={`px-2 py-1 rounded text-[11px] font-medium transition-colors ${
                viewportMode === "mobile"
                  ? "bg-zinc-800 text-zinc-100 shadow-sm"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
              title="Mobile view"
            >
              Mobile
            </button>
          </div>
        )}

        {previewUrl && (
          <a
            href={previewUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 rounded-md p-1.5 text-xs text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/80 transition-colors border border-transparent hover:border-zinc-700/50"
            title="Open preview in new tab"
            aria-label="Open in new tab"
          >
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
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
          </a>
        )}
      </div>
    </div>
  );
}
