import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { ChatBarViewJson } from '../../types'

// Which of the chat bar's boxes is open above the line: the session list, the pinned session card, the activation
// dialog and the close dialog. These change with the layout; the session actions that open them are in chat-bar-client.ts.
const chatBarView = atom({ plugin: 'cdd-board', key: 'chatBarView' } as const, {
  isSessionListOpen: false,
  isCardOpen: false,
  switchTo: null,
  closing: null,
} as ChatBarViewJson)

// Atom chatBarView, declared in pane/types/index.d.ts and kept in this file.
export function currentChatBarView($: EngineInterface) {
  return read($, chatBarView)
}

export async function toggleSessionList($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, isSessionListOpen: !view.isSessionListOpen, isCardOpen: false }))
}

// Hovering the session name shows the card; a press pins it open.
export async function toggleCard($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, isCardOpen: !view.isCardOpen, isSessionListOpen: false }))
}

// Picking a session opens the activation dialog on it; the session opens only once the person confirms.
export async function pickSession($: EngineInterface, sessionName: string): Promise<void> {
  await update($, chatBarView, view => ({ ...view, isSessionListOpen: false, switchTo: sessionName }))
}

export async function cancelSwitch($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, switchTo: null }))
}

// hasBranch says whether the close dialog offers to commit and push the session's work.
export async function showClose($: EngineInterface, hasBranch: boolean): Promise<void> {
  await update($, chatBarView, view => ({ ...view, closing: { hasBranch } }))
}

export async function cancelClose($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, closing: null }))
}
