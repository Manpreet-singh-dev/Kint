import React, { ReactNode } from "react";

export interface TwoPanelShellProps {
  leftPanel: ReactNode;
  rightPanel: ReactNode;
  className?: string;
}

/**
 * Two-panel layout shell for the Kint AI App Builder.
 * Implements a fixed 340px left panel for chat & agent orchestration status
 * and a flexible right panel for live sandbox preview, built dark-mode first.
 */
export function TwoPanelShell({
  leftPanel,
  rightPanel,
  className = "",
}: TwoPanelShellProps) {
  return (
    <div
      className={`flex h-screen w-full bg-zinc-950 text-zinc-100 overflow-hidden select-none ${className}`}
    >
      {/* Left Panel: 340px Fixed Width */}
      <aside className="w-[340px] shrink-0 border-r border-zinc-800/80 bg-zinc-900/95 flex flex-col h-full overflow-hidden shadow-2xl z-10">
        {leftPanel}
      </aside>

      {/* Right Panel: Flexible Live Preview */}
      <main className="flex-1 min-w-0 bg-zinc-950 flex flex-col h-full overflow-hidden relative">
        {rightPanel}
      </main>
    </div>
  );
}
