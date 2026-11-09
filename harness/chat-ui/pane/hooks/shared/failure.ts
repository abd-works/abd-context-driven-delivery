// The words a failure carries, for a toast or a log: the server's own text for a failed cdd tool, a thrown error's
// message otherwise.
export function reasonOf(failure: unknown): string {
  return failure instanceof Error ? failure.message : String(failure)
}
