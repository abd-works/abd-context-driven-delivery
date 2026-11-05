// Model shell for the chat bar (patterns-cdd-claude-mod). Classes only display; actions are plain functions, $ first,
// one MCP call each. Sources: harness/chat-ui/.context/story-map.md, cdr/0001-stage-strip-band.md, design/StageStrip.dc.html.
import type { EngineInterface } from 'claude-code'

import type { FidelityClient } from './fidelity-client'
import type { StageClient } from './stage-client'
import { ServerHealthClient } from '../health/server-health-client'

// The active session's line: health mark, session name, fidelity dots, action button, stage icons.
export class ChatBarClient {
  declare readonly serverHealth: ServerHealthClient // reused: props, reconnect, runInstall, openDetails
  declare readonly sessionName: string
  declare readonly fidelities: FidelityClient[]
  declare readonly stages: StageClient[]
}

// Atom chatBar, declared in pane/types/index.d.ts and kept in this file: the active session's TicketData.
export function currentChatBar($: EngineInterface): ChatBarClient | null { return null }

export async function refreshChatBar($: EngineInterface): Promise<void> {} // -> board.show
export async function moveNext($: EngineInterface, chatBar: ChatBarClient): Promise<void> {} // -> ticket.move_next
export async function runHandoff($: EngineInterface, chatBar: ChatBarClient): Promise<void> {} // $.prompt.fill the handoff
export async function switchSession($: EngineInterface, sessionName: string): Promise<void> {} // -> ticket.activate or ticket.create
export async function closeSession($: EngineInterface, chatBar: ChatBarClient): Promise<void> {} // -> ticket.close
