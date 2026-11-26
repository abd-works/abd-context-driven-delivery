import type { EngineInterface, ToolCallInput, ToolCallResult } from 'claude-code'

import { shownAsFailure } from '../error-display/failure-client'
import { callTool } from '../shared/cdd-tool'
import type { ChatBarClient } from './chat-bar-client'
import { refreshChatBar } from './chat-bar-client'

// The file the agent's finished tool call changed, when the call is an edit that went through: Claude Code's Edit and
// Write name it as file_path. Empty for any other call, or an edit refused or failed, which changed nothing.
export function changedArtifactOf(call: ToolCallInput, ran: ToolCallResult): string {
  if (ran.deny !== undefined || ran.isError) return ''
  if (call.tool !== 'Edit' && call.tool !== 'Write') return ''
  return call.file_path
}

// The session runs the graph rules on the changed file for each fidelity the bar shows that declares it, with no explicit
// validate (Session.check_changed_artifact); the bar then reads the board again, so its violation count follows the edit.
export async function checkChangedArtifact($: EngineInterface, chatBar: ChatBarClient, path: string): Promise<void> {
  const session = chatBar.sessionFile
  if (!session || !path) return
  try {
    await callTool($, 'session.check_changed_artifact', { session, path })
  } catch (failure) {
    await shownAsFailure($, `The graph rules did not run on ${path}`, 'Editing a file, calling session.check_changed_artifact')(failure)
    return
  }
  await refreshChatBar($)
}
