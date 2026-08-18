/**
 * Application environment configuration.
 */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const API_ENDPOINTS = {
  GENERATE: `${API_BASE_URL}/generate`,
  HEALTH: `${API_BASE_URL}/health`,
  SANDBOX_TEST: `${API_BASE_URL}/sandbox/test`,
} as const;
