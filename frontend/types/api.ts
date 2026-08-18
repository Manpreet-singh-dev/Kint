import { GeneratedFiles } from "./message";

export interface GenerateRequest {
  prompt: string;
}

export interface GenerateResponse {
  message: string;
  files: GeneratedFiles;
  preview_url: string | null;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface ApiErrorResponse {
  error?: string;
  message?: string;
  detail?: string;
}
