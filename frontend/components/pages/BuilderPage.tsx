"use client";

import React from "react";
import { useAppGeneration } from "@/hooks";
import { ChatPanel } from "./ChatPanel";
import { PreviewPanel } from "./PreviewPanel";

export function BuilderPage() {
  const {
    messages,
    isLoading,
    previewUrl,
    handleGenerate,
    refreshPreview,
  } = useAppGeneration();

  return (
    <div className="flex h-screen w-full bg-zinc-950 overflow-hidden">
      <ChatPanel
        messages={messages}
        isLoading={isLoading}
        onSend={handleGenerate}
      />
      <PreviewPanel
        previewUrl={previewUrl}
        onRefresh={refreshPreview}
      />
    </div>
  );
}
