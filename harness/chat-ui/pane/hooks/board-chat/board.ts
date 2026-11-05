import type { EngineInterface } from 'claude-code'

// Where the session board answers, shared by the chat relay and the board server.
export const BOARD_URL = 'http://127.0.0.1:8778'
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

export function post($: EngineInterface, { chat, operation, body }: ChatRequest) {
  return $.http.fetch(`${BOARD_URL}/api/chat/${encodeURIComponent(chat)}/${operation}`, { method: 'POST', headers: BOARD_HEADERS, body: JSON.stringify(body) })
}
