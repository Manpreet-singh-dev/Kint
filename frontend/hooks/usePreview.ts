"use client";

import { useState, useCallback } from "react";

/**
 * Custom hook to manage the preview URL and iframe refresh operations.
 */
export function usePreview(initialUrl: string | null = null) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(initialUrl);

  const refreshPreview = useCallback(() => {
    if (previewUrl) {
      const baseUrl = previewUrl.split("?")[0];
      setPreviewUrl(`${baseUrl}?t=${Date.now()}`);
    }
  }, [previewUrl]);

  return {
    previewUrl,
    setPreviewUrl,
    refreshPreview,
  };
}
