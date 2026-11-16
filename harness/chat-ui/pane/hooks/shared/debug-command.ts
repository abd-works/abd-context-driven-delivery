// The command the chat bar's debug button and its Fix buttons put to the chat: capture what went wrong, then fix it or
// request help. Fix names the failure as its details and the fix as its choice, so the chat goes straight to fixing it.
export function debugCommandOf(session: string, failure: string = ''): string {
  const parts = ['/space-session-debug-session', failure ? 'choice=fix' : '', session ? `session=${session}` : '', failure ? `details=${JSON.stringify(failure)}` : '']
  return parts.filter(Boolean).join(' ')
}
