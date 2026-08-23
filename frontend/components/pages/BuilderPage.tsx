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
    clearChat,
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
          onClearChat={clearChat}
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
