import type { EngineInterface } from 'claude-code'

import { callToolText } from '../shared/cdd-tool'

// A page this chat opens names its repository, so one app server can serve every repository.
export const PROJECT_QUERY = 'project'
// The folder an app's page opens on, such as the session's workpath the Graph loads.
export const FOLDER_QUERY = 'folder'
// A page this chat opens names the chat in its link, so it can show a file in this chat's file viewer (cdd-shared's
// CHAT_QUERY; the mod takes only types from the language adapter, so the word is spelled here as PROJECT_QUERY is).
export const CHAT_QUERY = 'chat'

// One call on a chat tool (chat.check_in, chat.confirm, chat.finish), each with the body that tool takes.
export type ChatRequest = { chat: string } & (
  | { operation: 'check-in'; body: { is_busy: boolean; name: string; folder: string } }
  | { operation: 'confirm'; body: { message: string; is_shown: boolean; reason: string } }
  | { operation: 'finish'; body: { message: string } }
)

// The checkout this chat works in: the main checkout, or a ticket's worktree. The cdd server picks a project's lane from
// it, so a page naming a worktree is answered by the dev lane on the ticket's code, and one naming the main checkout by
// the stable lane; the worktree shares the repository's board and sessions. Outside a repository, the chat's own folder.
export async function checkoutFolder($: EngineInterface): Promise<string> {
  const { exitCode, stdout } = await $.process.run(['git', 'rev-parse', '--show-toplevel'])
  return exitCode === 0 ? stdout.trim() : await $.session.root()
}

// An app's page at url showing this chat's checkout, with any further query the link carries, such as a report to
// open. Outside a repository the project is the folder the chat works in, which holds its tickets and sessions.
export async function projectPageUrl($: EngineInterface, url: string, query: Record<string, string> = {}): Promise<string> {
  const project = await checkoutFolder($)
  const page = new URL(url)
  for (const [name, value] of Object.entries({ ...(project ? { [PROJECT_QUERY]: project } : {}), ...query })) page.searchParams.set(name, value)
  return page.toString()
}

// A chat call goes to the cdd server every chat shares, as each chat tool does, so a chat checks in, confirms and
// finishes whether or not any app, the Kanban board included, is running, and the selection it holds is the one state
// the chat bar and its pages show. A failed call is the server's own text.
export async function post($: EngineInterface, { chat, operation, body }: ChatRequest): Promise<{ ok: boolean; text: string }> {
  const tool = `chat.${operation.replace('-', '_')}`
  return { ok: true, text: await callToolText($, tool, { chat, ...body }) }
}
