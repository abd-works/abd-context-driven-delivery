import type { EngineInterface } from 'claude-code'

import { projectPageUrl } from '../board-chat/board'
import { runningBoardUrl } from '../board-chat/board-server'
import { openApp } from '../health/app-client'
import { FILES } from '../health/server-health-client'
import { openInBrowserPane } from '../shared/browser-pane'
import { currentChatBar } from './chat-bar-client'
import type { FidelityProgressClient } from './fidelity-progress-client'

// A fidelity's files, a session's folder and a file another page asks for open in the Files app, the file viewer alone
// as an app of its own, in the desktop app's browser pane beside the chat; a fidelity's report opens in the board's
// report panel. Each is readied as the status row readies its app (Python's App.open, then this chat starts the server
// while it is not running), and opens by a link that names what to show. When the pane does not open, the toast says why.

async function openLink($: EngineInterface, what: string, appUrl: () => Promise<string>, query: Record<string, string>): Promise<void> {
  const url = await appUrl().catch(() => '')
  if (!url) return $.ui.toast(`${what} did not open: its app is not running and did not start`)
  const link = await projectPageUrl($, url, query)
  const problem = await openInBrowserPane($, link)
  if (problem) $.ui.toast(`${what} did not open at ${link}: ${problem}`)
}

const filesAppUrl = ($: EngineInterface) => async (): Promise<string> => (await openApp($, FILES)).url

const openFilesLink = ($: EngineInterface, what: string, query: Record<string, string>) => openLink($, what, filesAppUrl($), query)

const openBoardLink = ($: EngineInterface, what: string, query: Record<string, string>) => openLink($, what, () => runningBoardUrl($), query)

// One fidelity's files: the files button of a fidelity's folder on the session card.
export async function openFiles($: EngineInterface, fidelity: FidelityProgressClient): Promise<void> {
  await openFilesOf($, [fidelity])
}

// The files of the stage, with the practices of these fidelities turned on: the bar's files button.
export async function openFilesOf($: EngineInterface, fidelities: FidelityProgressClient[]): Promise<void> {
  const [first] = fidelities
  if (!first) return
  const slugs = fidelities.map(fidelity => fidelity.slug).join(',')
  await openFilesLink($, `${slugs} files`, { files: first.progress.ticket.name, fidelity: slugs })
}

// Every file in the chat's session folder, .sessions/<session>: a ticket chat's session name opens it.
export async function openSessionFolder($: EngineInterface): Promise<void> {
  const chatBar = await currentChatBar($)
  await openFilesLink($, `.sessions/${chatBar.sessionName}`, { 'session-folder': chatBar.sessionName })
}

// A file another page asked this chat to show (Chat.send open_file), such as a story's acceptance test the Story UI
// editor links: the session's folder in the Files app, with that file open.
export async function openFileInViewer($: EngineInterface, path: string): Promise<void> {
  const chatBar = await currentChatBar($)
  await openFilesLink($, path, { 'session-folder': chatBar.sessionName, file: path })
}

// The fidelity's latest validation report in the board's report panel, with its findings and Fix buttons. The report's
// text never comes into the chat: a report can run to many thousands of characters, past what one tool answer holds.
export async function openReport($: EngineInterface, fidelity: FidelityProgressClient): Promise<void> {
  await openBoardLink($, `${fidelity.slug} report (${fidelity.progress.report_file || 'not saved yet'})`, { report: fidelity.progress.ticket.name, fidelity: fidelity.slug })
}
