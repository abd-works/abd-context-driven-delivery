// What a failure says of itself: an error's message, or anything else thrown, as text.
export const reasonOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// What a cdd answer that is no result says: its own text, the error it names, or the whole answer as JSON.
export const saidBy = (answer: unknown): string => {
  if (typeof answer === 'string') return answer
  const error = (answer as { error?: unknown } | null)?.error
  return error !== undefined ? String(error) : JSON.stringify(answer)
}
