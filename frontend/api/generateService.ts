import { apiClient } from "./apiClient";
import { API_ENDPOINTS } from "@/lib/config";
import { GeneratedFiles, GenerateRequest, GenerateResponse, HealthResponse } from "@/types";

/**
 * Send prompt to FastAPI backend for code generation or recursive modification.
 */
export async function generateApp(
  prompt: string,
  currentFiles?: GeneratedFiles
): Promise<GenerateResponse> {
  const payload: GenerateRequest = {
    prompt: prompt.trim(),
    current_files: currentFiles,
  };

  return apiClient<GenerateResponse>(API_ENDPOINTS.GENERATE, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/**
 * Check health status of backend service.
 */
export async function checkBackendHealth(): Promise<HealthResponse> {
  return apiClient<HealthResponse>(API_ENDPOINTS.HEALTH, {
    method: "GET",
  });
}
