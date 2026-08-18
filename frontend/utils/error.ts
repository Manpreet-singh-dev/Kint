/**
 * Safely extract a human-readable error message from an unknown error object.
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === "string") {
    return error;
  }
  if (
    error &&
    typeof error === "object" &&
    "detail" in error &&
    typeof (error as { detail: unknown }).detail === "string"
  ) {
    return (error as { detail: string }).detail;
  }
  return "An unexpected error occurred. Please check your backend connection.";
}
