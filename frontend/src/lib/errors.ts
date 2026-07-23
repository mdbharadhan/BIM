import { AxiosError } from "axios";

/**
 * FastAPI's HTTPException serializes to { detail: string | object }.
 * This maps that (plus network failures) to a single human-readable string.
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    if (!error.response) {
      return "Network error: could not reach the backend API. Is it running?";
    }
    const status = error.response.status;
    const detail = error.response.data?.detail;

    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      // FastAPI validation error (422) shape: [{ loc, msg, type }, ...]
      return detail
        .map((d: { loc?: string[]; msg?: string }) =>
          d?.msg ? `${d.loc?.[d.loc.length - 1] ?? "field"}: ${d.msg}` : "Validation error"
        )
        .join("; ");
    }
    if (status === 404) return "Resource not found.";
    if (status >= 500) return "Server error. Please try again later.";
    return `Request failed (${status}).`;
  }
  if (error instanceof Error) return error.message;
  return "An unexpected error occurred.";
}
