import type { EngineInterface } from 'claude-code'

import { SERVER } from '../health/server-health-client'

// A page this chat opens names its repository, so one app server can serve every repository.
export const PROJECT_QUERY = 'project'
// The folder an app's page opens on, such as the session's workpath the Graph loads.
export const FOLDER_QUERY = 'folder'
// A page this chat opens names the chat in its link, so it can show a file in this chat's file viewer (cdd-shared's
// CHAT_QUERY; the mod takes only types from the language adapter, so the word is spelled here as PROJECT_QUERY is).
export const CHAT_QUERY = 'chat'

// One call on a chat tool (chat.check_in, chat.confirm, chat.finish, chat.select, chat.show, chat.show_stages, chat.list_stages), each with
// the body that tool takes.
export type ChatRequest = { chat: string } & (
  | { operation: 'check-in'; body: { is_busy: boolean; name: string; folder: string } }
  | { operation: 'select'; body: { selected_fidelities: string[] } }
  | { operation: 'show'; body: Record<string, never> }
  | { operation: 'show-stages'; body: { shown_stages: string[] } }
  | { operation: 'list-stages'; body: { stages: Record<string, string[]> } }
  | { operation: 'confirm'; body: { message: string; is_shown: boolean; reason: string } }
  | { operation: 'finish'; body: { message: string } }
)

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

// A chat call goes to the cdd server every chat shares, as each chat tool does, so a chat checks in, confirms and
// finishes whether or not any app, the Kanban board included, is running, and the selection it holds is the one state
// the chat bar and its pages show. A failed call is the server's own text.
export async function post($: EngineInterface, { chat, operation, body }: ChatRequest): Promise<{ ok: boolean; text: string }> {
  const tool = `chat.${operation.replace('-', '_')}`
  const result = await $.mcp.call(SERVER, tool, { chat, ...body })
  const text = result.content[0]?.text ?? ''
  if (result.isError) throw new ChatCallFailed(`${tool} failed: ${text || 'cdd sent back no reason'}`)
  return { ok: true, text }
}

export class ChatCallFailed extends Error {}
