import type { EngineInterface, ToolCallInput } from 'claude-code'

// The cdd server's tools, as the cdd plugin connects them or as an older install named the server.
const CDD_TOOL = /^mcp__(?:plugin_cdd_)?cdd__/

// session.log names the chat behind each action. A chat's id is its transcript's file name, which the cdd server finds
// from the id, so a cdd tool call carries it.
export async function withChatNamed($: EngineInterface, call: ToolCallInput): Promise<ToolCallInput> {
  if (!CDD_TOOL.test(call.tool)) return call
  return { ...call, conversation_id: await $.session.id() } as ToolCallInput
}
