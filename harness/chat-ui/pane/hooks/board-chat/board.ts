import type { EngineInterface } from 'claude-code'

import type { ServerHealthData } from '@cdd/harness/diagnostics/server-health'

import { currentServerHealth, KANBAN, ServerHealthClient } from '../health/server-health-client'

// The board refuses a POST without this header, so another page cannot act on it.
const BOARD_HEADERS = { 'X-CDD-Board': '1', 'Content-Type': 'application/json' }
// One board server serves every repository, so each call names this chat's repository, and the page's link does too.
const PROJECT_HEADER = 'X-CDD-Project'
export const PROJECT_QUERY = 'project'
// The folder an app's page opens on, such as the session's workpath the Graph loads.
export const FOLDER_QUERY = 'folder'
// A page this chat opens names the chat in its link, so it can show a file in this chat's file viewer (cdd-shared's
// CHAT_QUERY; the mod takes only types from the language adapter, so the word is spelled here as PROJECT_QUERY is).
export const CHAT_QUERY = 'chat'

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

// Where the session board answers, as cdd's server health last listed the Kanban app; empty while it is not running, or
// before cdd has answered. Its url names its first port even while it is down, so it is used only while it runs: a
// chat whose board is not running has no one to check in with, which is no failure.
async function boardUrlWhileRunning($: EngineInterface): Promise<string> {
  const { report } = await currentServerHealth($)
  const board = new ServerHealthClient(report as ServerHealthData | null).appLabelled(KANBAN)
  return board?.status === 'running' ? board.url : ''
}

// The repository's own folder, which a chat in a ticket's worktree reaches through the git folder they share: the
// project whose board this chat shows, where the board is installed and built, and what a path from the project is named
// from. Empty outside a repository.
export async function repositoryFolder($: EngineInterface): Promise<string> {
  const { exitCode, stdout } = await $.process.run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'])
  return exitCode === 0 ? stdout.trim().replace(/[\\/]\.git$/, '') : ''
}

// An app's page at url showing this chat's repository, with any further query the link carries, such as a report to
// open. Outside a repository the page shows its server's own project.
export async function projectPageUrl($: EngineInterface, url: string, query: Record<string, string> = {}): Promise<string> {
  const project = await repositoryFolder($)
  const page = new URL(url)
  for (const [name, value] of Object.entries({ ...(project ? { [PROJECT_QUERY]: project } : {}), ...query })) page.searchParams.set(name, value)
  return page.toString()
}

// A chat whose board is not running has nothing to post to, which reads as a board that did not answer.
export async function post($: EngineInterface, { chat, operation, body }: ChatRequest): Promise<{ ok: boolean; text: string }> {
  const url = await boardUrlWhileRunning($)
  if (!url) return { ok: false, text: '' }
  const project = await repositoryFolder($)
  const headers = project ? { ...BOARD_HEADERS, [PROJECT_HEADER]: project } : BOARD_HEADERS
  return $.http.fetch(`${new URL(url).origin}/api/chat/${encodeURIComponent(chat)}/${operation}`, { method: 'POST', headers, body: JSON.stringify(body) })
}
