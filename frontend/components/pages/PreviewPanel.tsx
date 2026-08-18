"use client";

import React from "react";
import { PreviewHeader } from "@/components/layout";
import { EmptyState } from "@/components/common";

export interface PreviewPanelProps {
  previewUrl: string | null;
  onRefresh: () => void;
}

export function PreviewPanel({ previewUrl, onRefresh }: PreviewPanelProps) {
  return (
    <div className="flex flex-1 flex-col bg-zinc-950 h-full overflow-hidden">
      <PreviewHeader previewUrl={previewUrl} onRefresh={onRefresh} />

      <div className="flex flex-1 items-center justify-center p-8 overflow-hidden">
        {previewUrl ? (
          <iframe
            src={previewUrl}
            className="h-full w-full rounded-lg border border-zinc-800 bg-white shadow-2xl"
            title="App Preview"
            sandbox="allow-scripts allow-same-origin allow-forms"
          />
        ) : (
          <EmptyState
            icon={
              <svg
                className="h-16 w-16 text-zinc-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            }
            title="No preview yet"
            description="Generate an app in the chat panel to see it running here in real-time."
          />
        )}
      </div>
    </div>
  );
}
