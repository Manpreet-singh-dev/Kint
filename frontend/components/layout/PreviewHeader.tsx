"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui";

export type ViewportMode = "desktop" | "tablet" | "mobile";

export interface PreviewHeaderProps {
  previewUrl: string | null;
  onRefresh: () => void;
  isLoading?: boolean;
  viewportMode?: ViewportMode;
  onViewportChange?: (mode: ViewportMode) => void;
}

export function PreviewHeader({
  previewUrl,
  onRefresh,
  isLoading = false,
  viewportMode = "desktop",
  onViewportChange,
}: PreviewHeaderProps) {
  const [copied, setCopied] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleCopyUrl = () => {
    if (!previewUrl) return;
    navigator.clipboard.writeText(previewUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRefreshClick = () => {
    setIsRefreshing(true);
    onRefresh();
    setTimeout(() => setIsRefreshing(false), 600);
  };

  return (
    <div className="flex items-center justify-between border-b border-zinc-800/80 bg-zinc-900/90 backdrop-blur-md px-4 py-2.5 shrink-0 select-none z-10">
      {/* Left: Window dots & Refresh */}
      <div className="flex items-center gap-2.5">
        <div className="flex items-center gap-1.5 mr-1.5">
          <span
            className="h-2.5 w-2.5 rounded-full bg-zinc-700/80 hover:bg-rose-500 transition-colors"
            title="Close"
          />
          <span
            className="h-2.5 w-2.5 rounded-full bg-zinc-700/80 hover:bg-amber-500 transition-colors"
            title="Minimize"
          />
          <span
            className="h-2.5 w-2.5 rounded-full bg-zinc-700/80 hover:bg-emerald-500 transition-colors"
            title="Maximize"
          />
        </div>

        <Button
          variant="icon"
          onClick={handleRefreshClick}
          disabled={!previewUrl || isLoading}
          title="Refresh preview"
          aria-label="Refresh preview"
          className="h-7 w-7 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/90 disabled:opacity-30 rounded-md transition-all cursor-pointer"
        >
          <svg
            className={`h-3.5 w-3.5 ${isRefreshing ? "animate-spin text-indigo-400" : ""}`}
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
      <div className="flex-1 max-w-lg mx-3">
        <div
          onClick={handleCopyUrl}
          className={`group flex items-center gap-2 rounded-lg bg-zinc-950/90 border px-3 py-1 text-xs font-mono shadow-inner transition-all ${
            previewUrl
              ? "border-zinc-800 hover:border-zinc-700 cursor-pointer"
              : "border-zinc-800/60 cursor-default"
          }`}
          title={previewUrl ? "Click to copy preview URL" : "Sandbox preview URL"}
        >
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

          <span
            className={`truncate flex-1 text-[11px] ${
              previewUrl
                ? "text-zinc-300 group-hover:text-zinc-100"
                : "text-zinc-500"
            }`}
          >
            {copied
              ? "✓ URL Copied to clipboard!"
              : previewUrl || "https://preview.local"}
          </span>

          {previewUrl && (
            <div className="flex items-center gap-1.5">
              <span className="flex h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[10px] text-zinc-500 group-hover:text-zinc-300 font-sans hidden sm:inline">
                Copy
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Right: Viewport mode toggles & Open in new tab */}
      <div className="flex items-center gap-2">
        {onViewportChange && (
          <div className="flex items-center rounded-lg bg-zinc-950 border border-zinc-800 p-0.5">
            <button
              type="button"
              onClick={() => onViewportChange("desktop")}
              className={`flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-medium transition-all cursor-pointer ${
                viewportMode === "desktop"
                  ? "bg-zinc-800 text-zinc-100 shadow-sm"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
              title="Desktop View (100%)"
            >
              <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span className="hidden md:inline">Desktop</span>
            </button>

            <button
              type="button"
              onClick={() => onViewportChange("tablet")}
              className={`flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-medium transition-all cursor-pointer ${
                viewportMode === "tablet"
                  ? "bg-zinc-800 text-zinc-100 shadow-sm"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
              title="Tablet View (768px)"
            >
              <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <span className="hidden md:inline">Tablet</span>
            </button>

            <button
              type="button"
              onClick={() => onViewportChange("mobile")}
              className={`flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-medium transition-all cursor-pointer ${
                viewportMode === "mobile"
                  ? "bg-zinc-800 text-zinc-100 shadow-sm"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
              title="Mobile View (390px)"
            >
              <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <span className="hidden md:inline">Mobile</span>
            </button>
          </div>
        )}

        {previewUrl && (
          <a
            href={previewUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/90 transition-all border border-zinc-800 hover:border-zinc-700 shadow-xs"
            title="Open preview in new tab"
            aria-label="Open in new tab"
          >
            <span className="hidden sm:inline text-[11px] font-medium">Open</span>
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
