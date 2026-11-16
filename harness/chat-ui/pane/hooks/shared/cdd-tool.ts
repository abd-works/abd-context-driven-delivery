import type { EngineInterface } from 'claude-code'

// The cdd plugin declares the server, and Claude Code names a plugin's server plugin:{plugin}:{server}.
export const SERVER = 'plugin:cdd:cdd'

// The arguments a cdd tool takes, each by the name its Python operation gives it.
export type ToolArguments = { readonly [argument: string]: unknown }

// A cdd tool answered with isError, or with no JSON. tool names it; the message is the server's own text. A call that
// cannot reach cdd at all, which is still connecting or down, throws the host's own failure instead.
export class CddToolFailed extends Error {
  constructor(
    readonly tool: string,
    reason: string,
  ) {
    super(reason)
  }
}

// The one place this mod calls cdd: a reply that is not JSON, or one flagged isError, is a CddToolFailed carrying the
// server's own text. Every call names the folder the chat works in now as chat_folder, so the server reads the sessions
// of that folder's branch and worktree, not of the folder the chat connected from, and names the chat as
// conversation_id, so the server answers with the session this chat has open, as it does for the agent's own calls.
export async function callTool<T>($: EngineInterface, tool: string, args: ToolArguments): Promise<T> {
  const text = await callToolText($, tool, args)
  try {
    return JSON.parse(text) as T
  } catch {
    throw new CddToolFailed(tool, text || `${tool} sent back nothing`)
  }
}

// A tool that answers in prose, such as repos.open, read as its text; one flagged isError is a CddToolFailed.
export async function callToolText($: EngineInterface, tool: string, args: ToolArguments): Promise<string> {
  const result = await $.mcp.call(SERVER, tool, { ...args, chat_folder: await $.session.root(), conversation_id: await $.session.id() })
  const text = result.content[0]?.text ?? ''
  if (result.isError) throw new CddToolFailed(tool, text || `${tool} failed`)
  return text
}
