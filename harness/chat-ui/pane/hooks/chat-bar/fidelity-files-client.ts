import type { EngineInterface } from 'claude-code'

import { CHAT_QUERY, projectPageUrl } from '../board-chat/board'
import { runningBoardUrl } from '../board-chat/board-server'
import { openApp } from '../health/app-client'
import { showFailure, shownAsFailure } from '../error-display/failure-client'
import { openInBrowserPane } from '../shared/browser-pane'
import { currentChatBar, type ChatBarClient } from './chat-bar-client'
import type { FidelityProgressClient } from './fidelity-progress-client'

// A fidelity's files, a session's folder and a file another page asks for open in the Files app, the file viewer alone
// as an app of its own, in the desktop app's browser pane beside the chat; a fidelity's report opens in the board's
// report panel. Each is readied as the status row readies its app (Python's App.open, then this chat starts the server
// while it is not running), and opens by a link that names what to show. When the pane does not open, the failure line says why.

// The Files app, harness/files_app: its own server on its own port, readied by Python's App.open as the status
// row readies any app. Its page names the chat that opened it, which its comments are sent to.
const FILES_APP = 'Files'
const BOARD_PAGE = '/'

// A page of the board's server, the board started first when it is not running, naming this chat, which the page sends
// its failures to. Every function here that takes `$` is
// a function declaration: the engine follows `$` only into those, and refuses a module that hides one in a const.
async function openBoardPage($: EngineInterface, what: string, query: Record<string, string>): Promise<void> {
  let url: string
  try {
    url = await runningBoardUrl($)
  } catch (failure) {
    return shownAsFailure($, `${what} did not open: the board is not running and did not start`, `Opening ${what}, starting the board server`)(failure)
  }
  if (!url) return showFailure($, `${what} did not open: the board is not running and did not start`, `Opening ${what}, starting the board server`)
  const link = await projectPageUrl($, new URL(BOARD_PAGE, url).toString(), { [CHAT_QUERY]: await $.session.id(), ...query })
  const problem = await openInBrowserPane($, link)
  if (problem) await showFailure($, `${what} did not open: ${problem}`, `Opening ${link} in Claude's Browser pane`)
}

async function openFilesLink($: EngineInterface, what: string, query: Record<string, string>): Promise<void> {
  let url: string
  try {
    url = (await openApp($, FILES_APP)).url
  } catch (failure) {
    return shownAsFailure($, `${what} did not open: the ${FILES_APP} app did not start`, `Opening ${what}, calling app.open for the ${FILES_APP} app`)(failure)
  }
  const link = await projectPageUrl($, url, { [CHAT_QUERY]: await $.session.id(), ...query })
  const problem = await openInBrowserPane($, link)
  if (problem) await showFailure($, `${what} did not open: ${problem}`, `Opening ${link} in Claude's Browser pane`)
}

async function openBoardLink($: EngineInterface, what: string, query: Record<string, string>): Promise<void> {
  await openBoardPage($, what, query)
}

// One fidelity's files: the files button of a fidelity's folder on the session card.
export async function openFiles($: EngineInterface, fidelity: FidelityProgressClient): Promise<void> {
  await openFilesLink($, `${fidelity.slug} files`, { files: fidelity.progress.ticket.name, fidelity: fidelity.slug })
}

// The shown stage's files, every practice's, for the files button: the Files app lists the files of the practices turned
// on and toggles a practice on or off for the session, which this bar then shows too.
export async function openStageFiles($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  const slugs = chatBar.stageFidelitySlugs.join(',')
  if (!slugs) return
  await openFilesLink($, `${chatBar.shownStages.join(' · ')} files`, { files: chatBar.sessionName, fidelity: slugs })
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
