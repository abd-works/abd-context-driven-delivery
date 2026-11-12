import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { LeaveChoicesData } from '@cdd/space/kanban/ticket'

import type { ChatBarViewJson, RepoRowJson } from '../../types'

// Which of the chat bar's boxes is open above the line: the session list, the pinned session card and the close dialog,
// with the choices the Python Ticket offers the close dialog and what the person chose. These change with the layout;
// the session actions that open them are in session-client.ts.
const chatBarView = atom(
  { plugin: 'cdd-board', key: 'chatBarView' } as const,
  {
    isSessionListOpen: false,
    isCardOpen: false,
    closing: null,
    leaveChoices: [],
    leaveBranch: '',
    leaveOwnBranch: '',
    leaving: [],
    repos: [],
  } as ChatBarViewJson,
  { shape: 'chat-bar-view-8' },
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

// The repositories the session list offers below the tickets, read each time it opens.
export async function showRepos($: EngineInterface, repos: RepoRowJson[]): Promise<void> {
  await update($, chatBarView, view => ({ ...view, repos }))
}

export async function closeSessionList($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, isSessionListOpen: false }))
}

// Hovering the session name shows the card; a press pins it open.
export async function closeCard($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, isCardOpen: false }))
}

export async function toggleCard($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, isCardOpen: !view.isCardOpen, isSessionListOpen: false }))
}

// The close dialog offers what ticket.close_choices answers, with those chosen at first, and the branch closing commits
// and pushes, or none when nothing checked out is the session's.
export async function showClose($: EngineInterface, choices: LeaveChoicesData): Promise<void> {
  await update($, chatBarView, view => ({ ...view, closing: { branch: choices.branch || null }, leaveChoices: choices.choices, leaveBranch: choices.branch, leaveOwnBranch: choices.own_branch, leaving: choices.chosen }))
}

export async function cancelClose($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, closing: null }))
}

// A press on a choice of the close dialog turns it on or off.
export async function toggleLeaving($: EngineInterface, choice: string): Promise<void> {
  await update($, chatBarView, view => ({ ...view, leaving: toggled(view.leaving, choice, view.leaveChoices) }))
}
