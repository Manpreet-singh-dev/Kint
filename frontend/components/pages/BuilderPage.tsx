"use client";

import React from "react";
import { useAppGeneration } from "@/hooks";
import { TwoPanelShell } from "@/components/layout";
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
    <TwoPanelShell
      leftPanel={
        <ChatPanel
          messages={messages}
          isLoading={isLoading}
          onSend={handleGenerate}
        />
      }
      rightPanel={
        <PreviewPanel
          previewUrl={previewUrl}
          onRefresh={refreshPreview}
        />
      }
    />
  );
}
