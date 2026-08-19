"use client";

import React, { useState } from "react";
import { PreviewHeader, ViewportMode } from "@/components/layout";
import { EmptyState } from "@/components/common";

export interface PreviewPanelProps {
  previewUrl: string | null;
  onRefresh: () => void;
}

export function PreviewPanel({ previewUrl, onRefresh }: PreviewPanelProps) {
  const [viewportMode, setViewportMode] = useState<ViewportMode>("desktop");

  const getViewportWidthClass = () => {
    switch (viewportMode) {
      case "mobile":
        return "max-w-[390px] h-[844px] max-h-full rounded-2xl border-4 border-zinc-800 shadow-2xl";
      case "tablet":
        return "max-w-[768px] h-[1024px] max-h-full rounded-xl border-2 border-zinc-800 shadow-2xl";
      case "desktop":
      default:
        return "w-full h-full rounded-lg border border-zinc-800/80 shadow-2xl";
    }
  };

  return (
    <div className="flex flex-1 flex-col bg-zinc-950 h-full overflow-hidden">
      <PreviewHeader
        previewUrl={previewUrl}
        onRefresh={onRefresh}
        viewportMode={viewportMode}
        onViewportChange={setViewportMode}
      />

      <div className="flex flex-1 items-center justify-center p-4 md:p-6 overflow-hidden bg-zinc-950/60">
        {previewUrl ? (
          <div
            className={`transition-all duration-300 ease-out flex items-center justify-center w-full h-full ${
              viewportMode !== "desktop" ? "py-4" : ""
            }`}
          >
            <iframe
              src={previewUrl}
              className={`bg-white transition-all duration-200 ${getViewportWidthClass()}`}
              title="App Preview"
              sandbox="allow-scripts allow-same-origin allow-forms"
            />
          </div>
        ) : (
          <EmptyState
            icon={
              <svg
                className="h-12 w-12 text-zinc-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            }
            title="Live Preview"
            description="Your generated web application will render interactively here in real time."
          />
        )}
      </div>
    </div>
  );
}
