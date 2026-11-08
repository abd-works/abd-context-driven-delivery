import type { EngineInterface } from 'claude-code'

import type { ServerHealthData } from '@cdd/harness/diagnostics/server-health'

import { currentServerHealth, ServerHealthClient } from '../health/server-health-client'

// The board refuses a POST without this header, so another page cannot act on it.
const BOARD_HEADERS = { 'X-CDD-Board': '1', 'Content-Type': 'application/json' }

// One call on the board's chat routes, each with the body that chat tool takes.
export type ChatRequest = { chat: string } & (
  | { operation: 'check-in'; body: { is_busy: boolean; name: string; folder: string } }
  | { operation: 'confirm'; body: { message: string; is_shown: boolean; reason: string } }
  | { operation: 'finish'; body: { message: string } }
)

// Resolves to answer once milliseconds have passed on the engine's clock.
export function after($: EngineInterface, milliseconds: number, answer: string): Promise<string> {
  return new Promise(resolve => $.clock.after(milliseconds, () => resolve(answer)))
}

// Where the session board answers, as cdd's server health last gave it; empty until cdd has answered.
export async function boardUrl($: EngineInterface): Promise<string> {
  const { report } = await currentServerHealth($)
  return new ServerHealthClient(report as ServerHealthData | null).kanbanAppUrl
}

// A chat with no board address yet has nothing to post to, which reads as a board that did not answer.
export async function post($: EngineInterface, { chat, operation, body }: ChatRequest): Promise<{ ok: boolean; text: string }> {
  const url = await boardUrl($)
  if (!url) return { ok: false, text: '' }
  return $.http.fetch(`${url}/api/chat/${encodeURIComponent(chat)}/${operation}`, { method: 'POST', headers: BOARD_HEADERS, body: JSON.stringify(body) })
}
