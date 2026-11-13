import type { EngineInterface } from 'claude-code'

import { boardPageUrl } from '../board-chat/board'
import { openPage, runningBoardUrl } from '../board-chat/board-server'
import { currentChatBar } from './chat-bar-client'
import type { FidelityProgressClient } from './fidelity-progress-client'

// A fidelity's files, a session's folder and a fidelity's report open in the board's own panels, in the desktop app's
// browser pane beside the chat: the board's file viewer, with its practice filters, comments and change marks, is the
// one viewer, so the chat bar never draws a second. Each opens by a board link, the board started first when it is not
// running. When the pane does not open it, it opens in the person's own browser, and the toast says why.

async function openBoardLink($: EngineInterface, what: string, query: Record<string, string>): Promise<void> {
  const url = await runningBoardUrl($).catch(() => '')
  if (!url) return $.ui.toast(`${what} did not open: the board is not running and did not start`)
  const link = await boardPageUrl($, url, query)
  const said = await openPage($, link)
  if (said) $.ui.toast(`${what} at ${link}: ${said}`)
}

// One fidelity's files: the files button of a fidelity's folder on the session card.
export async function openFiles($: EngineInterface, fidelity: FidelityProgressClient): Promise<void> {
  await openFilesOf($, [fidelity])
}

// The files of the stage, with the practices of these fidelities turned on: the bar's files button.
export async function openFilesOf($: EngineInterface, fidelities: FidelityProgressClient[]): Promise<void> {
  const [first] = fidelities
  if (!first) return
  const slugs = fidelities.map(fidelity => fidelity.slug).join(',')
  await openBoardLink($, `${slugs} files`, { files: first.progress.ticket.name, fidelity: slugs })
}

// Every file in the chat's session folder, .sessions/<session>: a ticket chat's session name opens it.
export async function openSessionFolder($: EngineInterface): Promise<void> {
  const chatBar = await currentChatBar($)
  await openBoardLink($, `.sessions/${chatBar.sessionName}`, { 'session-folder': chatBar.sessionName })
}

// The fidelity's latest validation report in the board's report panel, with its findings and Fix buttons. The report's
// text never comes into the chat: a report can run to many thousands of characters, past what one tool answer holds.
export async function openReport($: EngineInterface, fidelity: FidelityProgressClient): Promise<void> {
  await openBoardLink($, `${fidelity.slug} report (${fidelity.progress.report_file || 'not saved yet'})`, { report: fidelity.progress.ticket.name, fidelity: fidelity.slug })
}
