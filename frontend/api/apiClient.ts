import { ApiErrorResponse } from "@/types";

export class ApiError extends Error {
  status: number;
  data?: ApiErrorResponse;

  constructor(message: string, status: number, data?: ApiErrorResponse) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

/**
 * Standard HTTP client with error handling and JSON parsing.
 */
export async function apiClient<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const defaultHeaders: HeadersInit = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorData: ApiErrorResponse | undefined;
    try {
      errorData = await response.json();
    } catch {
      // Body may not be valid JSON
    }

    const message =
      errorData?.message ||
      errorData?.detail ||
      `HTTP error ${response.status}: ${response.statusText}`;

    throw new ApiError(message, response.status, errorData);
  }

  return response.json();
}
