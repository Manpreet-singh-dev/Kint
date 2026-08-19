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
    agentTrail,
    handleGenerate,
    refreshPreview,
  } = useAppGeneration();

  return (
    <TwoPanelShell
      hasPreview={!!previewUrl}
      leftPanel={
        <ChatPanel
          messages={messages}
          isLoading={isLoading}
          onSend={handleGenerate}
          agentTrail={agentTrail}
        />
      }
      rightPanel={
        <PreviewPanel
          previewUrl={previewUrl}
          onRefresh={refreshPreview}
          isLoading={isLoading}
        />
      }
    />
  );
}
