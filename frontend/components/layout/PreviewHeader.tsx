"use client";

import React from "react";
import { Button } from "@/components/ui";

export interface PreviewHeaderProps {
  previewUrl: string | null;
  onRefresh: () => void;
}

export function PreviewHeader({ previewUrl, onRefresh }: PreviewHeaderProps) {
  return (
    <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-900 px-4 py-3">
      <Button
        variant="icon"
        onClick={onRefresh}
        disabled={!previewUrl}
        title="Refresh preview"
        aria-label="Refresh preview"
      >
        <svg
          className="h-4 w-4"
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

      {previewUrl && (
        <>
          <div className="flex-1 rounded-lg bg-zinc-800 px-3 py-1.5 border border-zinc-700/50">
            <p className="truncate text-xs font-mono text-zinc-400">
              {previewUrl}
            </p>
          </div>
          <a
            href={previewUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg p-2 text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-zinc-200"
            title="Open in new tab"
            aria-label="Open in new tab"
          >
            <svg
              className="h-4 w-4"
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
        </>
      )}
    </div>
  );
}
