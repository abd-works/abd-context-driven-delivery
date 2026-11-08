import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { ChatBarViewJson } from '../../types'

// Which of the chat bar's boxes is open above the line: the session list, the pinned session card, the activation
// dialog and the close dialog, with what each dialog chose. These change with the layout; the session actions that
// open them are in session-client.ts.
const chatBarView = atom(
  { plugin: 'cdd-board', key: 'chatBarView' } as const,
  {
    isSessionListOpen: false,
    isCardOpen: false,
    switchTo: null,
    closing: null,
    leaving: [],
    opening: [],
  } as ChatBarViewJson,
  { shape: 'chat-bar-view-2' },
)

// What the board's activation dialog chooses first: write a handoff for the session left, commit and push its work,
// and open the new one on its own branch and worktree. Merge waits for the person to choose it.
const FIRST_LEAVING = ['handoff', 'commit', 'push']
const FIRST_OPENING = ['branch', 'worktree']
// Closing chooses a handoff always, and commit and push only while the branch its work is on is checked out.
const HANDOFF_ONLY = ['handoff']
// The order Ticket.leave reads them in, so a choice sent reads the same however the person pressed.
const LEAVING_ORDER = ['handoff', 'commit', 'push', 'merge']
const OPENING_ORDER = ['branch', 'worktree']

const toggled = (chosen: string[], choice: string, order: string[]): string[] =>
  order.filter(entry => (entry === choice ? !chosen.includes(entry) : chosen.includes(entry)))

// Atom chatBarView, declared in pane/types/index.d.ts and kept in this file.
export function currentChatBarView($: EngineInterface) {
  return read($, chatBarView)
}

export async function toggleSessionList($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, isSessionListOpen: !view.isSessionListOpen, isCardOpen: false }))
}

// Hovering the session name shows the card; a press pins it open.
export async function closeCard($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, isCardOpen: false }))
}

export async function toggleCard($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, isCardOpen: !view.isCardOpen, isSessionListOpen: false }))
}

// Picking a session opens the activation dialog on it with its first choices; the session opens only once the person
// confirms.
export async function pickSession($: EngineInterface, sessionName: string): Promise<void> {
  await update($, chatBarView, view => ({ ...view, isSessionListOpen: false, switchTo: sessionName, leaving: FIRST_LEAVING, opening: FIRST_OPENING }))
}

export async function cancelSwitch($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, switchTo: null }))
}

// branch names the branch the session's work is on while it is checked out, which the close dialog offers to commit
// and push; null when nothing checked out is the session's.
export async function showClose($: EngineInterface, branch: string | null): Promise<void> {
  await update($, chatBarView, view => ({ ...view, closing: { branch }, leaving: branch ? FIRST_LEAVING.filter(choice => choice !== 'merge') : HANDOFF_ONLY }))
}

export async function cancelClose($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, closing: null }))
}

// A press on a choice of the dialog turns it on or off.
export async function toggleLeaving($: EngineInterface, choice: string): Promise<void> {
  await update($, chatBarView, view => ({ ...view, leaving: toggled(view.leaving, choice, LEAVING_ORDER) }))
}

export async function toggleOpening($: EngineInterface, choice: string): Promise<void> {
  await update($, chatBarView, view => ({ ...view, opening: toggled(view.opening, choice, OPENING_ORDER) }))
}
