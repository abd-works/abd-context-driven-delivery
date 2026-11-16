// The words a failure carries: the server's own text for a failed cdd tool, a thrown error's message otherwise.
export function reasonOf(failure: unknown): string {
  return failure instanceof Error ? failure.message : String(failure)
}
