import { apiClient } from "./apiClient";
import { API_ENDPOINTS } from "@/lib/config";
import { GenerateRequest, GenerateResponse, HealthResponse } from "@/types";

/**
 * Send prompt to FastAPI backend for code generation.
 */
export async function generateApp(prompt: string): Promise<GenerateResponse> {
  const payload: GenerateRequest = { prompt: prompt.trim() };

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
