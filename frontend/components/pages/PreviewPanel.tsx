"use client";

import React, { useState } from "react";
import { PreviewHeader, ViewportMode } from "@/components/layout";

export interface PreviewPanelProps {
  previewUrl: string | null;
  onRefresh: () => void;
  isLoading?: boolean;
}

export function PreviewPanel({
  previewUrl,
  onRefresh,
  isLoading = false,
}: PreviewPanelProps) {
  const [viewportMode, setViewportMode] = useState<ViewportMode>("desktop");

  const getViewportWidthClass = () => {
    switch (viewportMode) {
      case "mobile":
        return "w-[390px] h-[800px] max-h-[92%] rounded-3xl border-4 border-zinc-800 bg-white shadow-2xl shadow-black/80";
      case "tablet":
        return "w-[768px] h-[960px] max-h-[95%] rounded-2xl border-2 border-zinc-800 bg-white shadow-2xl shadow-black/80";
      case "desktop":
      default:
        return "w-full h-full rounded-xl border border-zinc-800/80 bg-white shadow-2xl";
    }
  };

  return (
    <div className="flex flex-1 flex-col bg-zinc-950 h-full overflow-hidden">
      <PreviewHeader
        previewUrl={previewUrl}
        onRefresh={onRefresh}
        isLoading={isLoading}
        viewportMode={viewportMode}
        onViewportChange={setViewportMode}
      />

      <div className="flex flex-1 items-center justify-center p-4 md:p-6 overflow-hidden bg-radial from-zinc-900/30 via-zinc-950 to-zinc-950">
        {previewUrl ? (
          <div
            className={`transition-all duration-300 ease-out flex items-center justify-center w-full h-full ${
              viewportMode !== "desktop" ? "py-2" : ""
            }`}
          >
            <iframe
              src={previewUrl}
              className={`transition-all duration-300 ${getViewportWidthClass()}`}
              title="Application Live Preview"
              sandbox="allow-scripts allow-same-origin allow-forms"
            />
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center max-w-lg text-center px-4 select-none">
            {/* Visual Chrome Illustration */}
            <div className="relative mb-6">
              <div className="absolute -inset-2 rounded-3xl bg-gradient-to-r from-indigo-500/20 via-purple-500/20 to-pink-500/20 blur-xl opacity-50" />
              <div className="relative flex h-24 w-40 flex-col rounded-2xl border border-zinc-800 bg-zinc-900/90 shadow-2xl p-2.5 backdrop-blur-md">
                <div className="flex items-center gap-1.5 border-b border-zinc-800/80 pb-2">
                  <span className="h-2 w-2 rounded-full bg-zinc-700" />
                  <span className="h-2 w-2 rounded-full bg-zinc-700" />
                  <span className="h-2 w-2 rounded-full bg-zinc-700" />
                  <div className="ml-2 h-2 flex-1 rounded bg-zinc-800" />
                </div>
                <div className="flex flex-1 items-center justify-center gap-1.5 pt-2">
                  <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-indigo-500/20 text-indigo-400 text-xs">
                    ⚡
                  </span>
                  <div className="space-y-1 text-left">
                    <div className="h-1.5 w-14 rounded bg-zinc-700/80" />
                    <div className="h-1.5 w-10 rounded bg-zinc-800" />
                  </div>
                </div>
              </div>
            </div>

            <h2 className="text-base font-semibold text-zinc-100 tracking-tight">
              Live Sandbox Preview
            </h2>
            <p className="mt-1.5 text-xs text-zinc-400 leading-relaxed max-w-sm">
              Describe an application in the chat panel. Kint will plan, generate,
              and execute it inside an isolated cloud sandbox, rendering live here.
            </p>

            {/* Feature Highlights Grid */}
            <div className="mt-6 grid grid-cols-3 gap-2.5 w-full">
              <div className="flex flex-col items-center rounded-xl border border-zinc-800/80 bg-zinc-900/60 p-3 text-center transition-all hover:bg-zinc-900/90">
                <span className="text-sm mb-1">🚀</span>
                <span className="text-[11px] font-medium text-zinc-200">
                  E2B Sandbox
                </span>
                <span className="text-[10px] text-zinc-500 mt-0.5">
                  Isolated Cloud VM
                </span>
              </div>

              <div className="flex flex-col items-center rounded-xl border border-zinc-800/80 bg-zinc-900/60 p-3 text-center transition-all hover:bg-zinc-900/90">
                <span className="text-sm mb-1">📱</span>
                <span className="text-[11px] font-medium text-zinc-200">
                  Multi-Device
                </span>
                <span className="text-[10px] text-zinc-500 mt-0.5">
                  Desktop & Mobile
                </span>
              </div>

              <div className="flex flex-col items-center rounded-xl border border-zinc-800/80 bg-zinc-900/60 p-3 text-center transition-all hover:bg-zinc-900/90">
                <span className="text-sm mb-1">🔄</span>
                <span className="text-[11px] font-medium text-zinc-200">
                  Live Reload
                </span>
                <span className="text-[10px] text-zinc-500 mt-0.5">
                  Hot refresh
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
