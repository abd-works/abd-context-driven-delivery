import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { LeaveChoicesData, OpenChoicesData } from '@cdd/space/kanban/ticket'

import type { ChatBarViewJson } from '../../types'

// Which of the chat bar's boxes is open above the line: the session list, the pinned session card, the activation
// dialog and the close dialog, with the choices the Python Ticket offers each dialog and what the person chose. These
// change with the layout; the session actions that open them are in session-client.ts.
const chatBarView = atom(
  { plugin: 'cdd-board', key: 'chatBarView' } as const,
  {
    isSessionListOpen: false,
    isCardOpen: false,
    switchTo: null,
    closing: null,
    leaveChoices: [],
    leaveBranch: '',
    leaveOwnBranch: '',
    leaving: [],
    openChoices: [],
    candidateBranches: [],
    opening: [],
  } as ChatBarViewJson,
  { shape: 'chat-bar-view-6' },
)

// A press turns choice on or off; the chosen stay in the order the Ticket offers them, so a choice sent reads the same
// however the person pressed.
const toggled = (chosen: string[], choice: string, offered: string[]): string[] =>
  offered.filter(entry => (entry === choice ? !chosen.includes(entry) : chosen.includes(entry)))

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

// The activation dialog on the ticket called name, with the choices the Python Tickets answer: what leaving the active
// one can do now, none while no session is active, and what opening this one can create now, each with those chosen at
// first. The session opens only once the person confirms.
export async function showSwitch($: EngineInterface, name: string, leaving: LeaveChoicesData | null, opening: OpenChoicesData): Promise<void> {
  await update($, chatBarView, view => ({
    ...view,
    isSessionListOpen: false,
    switchTo: name,
    leaveChoices: leaving?.choices ?? [],
    leaveBranch: leaving?.branch ?? '',
    leaveOwnBranch: leaving?.own_branch ?? '',
    leaving: leaving?.chosen ?? [],
    openChoices: opening.choices,
    candidateBranches: opening.candidate_branches,
    opening: opening.chosen,
  }))
}

export async function cancelSwitch($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, switchTo: null }))
}

// The close dialog offers what ticket.close_choices answers, with those chosen at first, and the branch closing commits
// and pushes, or none when nothing checked out is the session's.
export async function showClose($: EngineInterface, choices: LeaveChoicesData): Promise<void> {
  await update($, chatBarView, view => ({ ...view, closing: { branch: choices.branch || null }, leaveChoices: choices.choices, leaveBranch: choices.branch, leaveOwnBranch: choices.own_branch, leaving: choices.chosen }))
}

export async function cancelClose($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, closing: null }))
}

// A press on a choice of the dialog turns it on or off.
export async function toggleLeaving($: EngineInterface, choice: string): Promise<void> {
  await update($, chatBarView, view => ({ ...view, leaving: toggled(view.leaving, choice, view.leaveChoices) }))
}

// The ways of opening are alternatives, as OpenChoices offers them, so a press picks one.
export async function toggleOpening($: EngineInterface, choice: string): Promise<void> {
  await update($, chatBarView, view => ({ ...view, opening: [choice] }))
}
