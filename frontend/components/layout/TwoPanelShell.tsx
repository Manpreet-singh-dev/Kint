"use client";

import React, { ReactNode, useState, useEffect, useCallback, useRef } from "react";

export interface TwoPanelShellProps {
  leftPanel: ReactNode;
  rightPanel: ReactNode;
  className?: string;
  hasPreview?: boolean;
}

const MIN_PANEL_WIDTH = 280;
const MAX_PANEL_WIDTH = 600;
const DEFAULT_PANEL_WIDTH = 340;

/**
 * Two-panel layout shell for the Kint AI App Builder.
 * Features an interactive draggable resize splitter to adjust left sidebar width,
 * with mobile tab navigation for responsive screens.
 * Uses CSS variables for width to ensure perfect SSR hydration without mismatch.
 */
export function TwoPanelShell({
  leftPanel,
  rightPanel,
  className = "",
  hasPreview = false,
}: TwoPanelShellProps) {
  const [mobileTab, setMobileTab] = useState<"chat" | "preview">("chat");
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const isDraggingRef = useRef(false);
  const currentWidthRef = useRef(DEFAULT_PANEL_WIDTH);

  // Restore saved width from localStorage directly into CSS variable after mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem("kint_sidebar_width");
      if (saved && containerRef.current) {
        const parsed = parseInt(saved, 10);
        if (
          !isNaN(parsed) &&
          parsed >= MIN_PANEL_WIDTH &&
          parsed <= MAX_PANEL_WIDTH
        ) {
          currentWidthRef.current = parsed;
          containerRef.current.style.setProperty(
            "--sidebar-width",
            `${parsed}px`
          );
        }
      }
    } catch {
      // Ignore localStorage access errors
    }
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    isDraggingRef.current = true;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  }, []);

  const handleDoubleClick = useCallback(() => {
    currentWidthRef.current = DEFAULT_PANEL_WIDTH;
    if (containerRef.current) {
      containerRef.current.style.setProperty(
        "--sidebar-width",
        `${DEFAULT_PANEL_WIDTH}px`
      );
    }
    try {
      localStorage.setItem("kint_sidebar_width", String(DEFAULT_PANEL_WIDTH));
    } catch {
      // Ignore
    }
  }, []);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDraggingRef.current) return;
      const newWidth = Math.min(
        Math.max(e.clientX, MIN_PANEL_WIDTH),
        MAX_PANEL_WIDTH
      );
      currentWidthRef.current = newWidth;
      if (containerRef.current) {
        containerRef.current.style.setProperty(
          "--sidebar-width",
          `${newWidth}px`
        );
      }
    };

    const handleMouseUp = () => {
      if (isDraggingRef.current) {
        isDraggingRef.current = false;
        setIsDragging(false);
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
        try {
          localStorage.setItem(
            "kint_sidebar_width",
            String(currentWidthRef.current)
          );
        } catch {
          // Ignore
        }
      }
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, []);

  return (
    <div
      ref={containerRef}
      style={
        {
          "--sidebar-width": `${DEFAULT_PANEL_WIDTH}px`,
        } as React.CSSProperties
      }
      className={`flex flex-col md:flex-row h-screen w-full bg-zinc-950 text-zinc-100 overflow-hidden select-none relative ${className}`}
    >
      {/* Overlay to capture mouse events when dragging over iframe */}
      {isDragging && (
        <div className="absolute inset-0 z-50 cursor-col-resize bg-transparent" />
      )}

      {/* Mobile Top Navigation Tab Switcher */}
      <div className="flex md:hidden items-center justify-between border-b border-zinc-800 bg-zinc-900 px-4 py-2 shrink-0 z-20">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 text-[10px] font-bold text-white">
            K
          </div>
          <span className="text-xs font-semibold text-zinc-200">
            Kint Builder
          </span>
        </div>

        <div className="flex items-center rounded-lg bg-zinc-950 border border-zinc-800 p-0.5">
          <button
            type="button"
            onClick={() => setMobileTab("chat")}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-all ${
              mobileTab === "chat"
                ? "bg-zinc-800 text-zinc-100 shadow-xs"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            💬 Chat
          </button>
          <button
            type="button"
            onClick={() => setMobileTab("preview")}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-all ${
              mobileTab === "preview"
                ? "bg-zinc-800 text-zinc-100 shadow-xs"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            🌐 Preview
            {hasPreview && (
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            )}
          </button>
        </div>
      </div>

      {/* Left Panel: Resizable on Desktop via CSS variable, Full-width on Mobile */}
      <aside
        className={`w-full md:w-[var(--sidebar-width)] shrink-0 border-r border-zinc-800/80 bg-zinc-900/95 flex flex-col h-full overflow-hidden shadow-2xl z-10 ${
          mobileTab === "chat" ? "flex" : "hidden md:flex"
        }`}
      >
        {leftPanel}
      </aside>

      {/* Desktop Draggable Resize Splitter Handle */}
      <div
        onMouseDown={handleMouseDown}
        onDoubleClick={handleDoubleClick}
        title="Drag to resize panel (Double-click to reset)"
        className={`hidden md:flex items-center justify-center w-1.5 shrink-0 bg-zinc-900/80 hover:bg-indigo-500/50 cursor-col-resize transition-colors relative z-20 group ${
          isDragging ? "bg-indigo-500" : ""
        }`}
      >
        <div
          className={`h-8 w-1 rounded-full bg-zinc-700 group-hover:bg-indigo-400 transition-colors ${
            isDragging ? "bg-indigo-300" : ""
          }`}
        />
      </div>

      {/* Right Panel: Flexible Live Preview */}
      <main
        className={`flex-1 min-w-0 bg-zinc-950 flex flex-col h-full overflow-hidden relative ${
          mobileTab === "preview" ? "flex" : "hidden md:flex"
        }`}
      >
        {rightPanel}
      </main>
    </div>
  );
}
