import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { FileEntryData } from '@cdd/space/kanban/fidelity-progress'
import type { FileTextData } from '@cdd/space/session/session'

import type { FidelityFilesJson } from '../../types'
import { projectPageUrl, repositoryFolder } from '../board-chat/board'
import { runningBoardUrl } from '../board-chat/board-server'
import { openAppBesideChat } from '../health/app-client'
import { openInBrowser } from '../shared/browser'
import { reasonOf } from '../shared/failure'
import { callTool, currentChatBar } from './chat-bar-client'
import { runAction, type FidelityProgressClient } from './fidelity-progress-client'

// The files view of one fidelity: a tab per file fidelity-progress.files declares, each tab's text read by session.read_file.
// It opens in a pane of its own beside the chat, as the board's files panel does, never above the prompt in the chat.
export const FILES_PANE = 'cdd-files'
const fidelityFiles = atom({ plugin: 'cdd-board', key: 'fidelityFiles' } as const, null as FidelityFilesJson, { shape: 'fidelity-files-3' })

// A diagram is drawn in the draw.io editor, not as text, so its XML, often too long for one tool answer, is never read.
export const isDiagram = (path: string): boolean => path.endsWith('.drawio')

async function openPane($: EngineInterface, title: string): Promise<void> {
  const opened = await $.ui.open({ id: FILES_PANE, title })
  if (!opened.isPlaced) $.ui.log(`cdd-board: the files pane waits to be placed: ${opened.reason}`, { to: 'debug' })
}

// Atom fidelityFiles, declared in pane/types/index.d.ts and kept in this file.
export function currentFidelityFiles($: EngineInterface) {
  return read($, fidelityFiles)
}

// One tab per file the fidelity declares, in the order fidelity-progress.files sends its formats (markdown, then code,
// then diagrams); the first tab's text is read straight away.
export async function openFiles($: EngineInterface, fidelity: FidelityProgressClient): Promise<void> {
  await openFilesOf($, [fidelity])
}

// Every file of several fidelities, each once, as tabs of one files pane: the files button opens the files of every
// selected fidelity together.
export async function openFilesOf($: EngineInterface, fidelities: FidelityProgressClient[]): Promise<void> {
  const [first] = fidelities
  if (!first) return
  const named = fidelities.map(fidelity => fidelity.slug).join(', ')
  try {
    const read = await Promise.all(fidelities.map(fidelity => callTool<Record<string, FileEntryData[]>>($, 'fidelity-progress.files', { ticket: fidelity.progress.ticket.name, fidelity: fidelity.slug })))
    const entries = read.flatMap((files, index) => Object.values(files).flat().map(entry => ({ ...entry, editor: fidelities[index]?.editor?.label ?? null })))
    const paths = [...new Set(entries.map(entry => entry.path))]
    const exists = (path: string) => entries.some(entry => entry.path === path && entry.exists)
    const editor = (path: string) => entries.find(entry => entry.path === path)?.editor ?? null
    const tabs = paths.map(path => ({ path, text: null, exists: exists(path), editor: editor(path) }))
    const { designView } = await currentChatBar($)
    await update($, fidelityFiles, () => ({ fidelity: first.slug, tabs, shown: paths[0] ?? null, isOutOfDate: false, designView }))
    await openPane($, `${named} files`)
    if (paths[0]) await showFile($, paths[0])
  } catch (failure) {
    $.ui.toast(`${named} files: ${reasonOf(failure)}`)
  }
}

// The fidelity's latest validation report in the board's own report panel, with its findings and Fix buttons, opened in
// the person's browser by the board's ?report=&fidelity= link, the board started first when it is not running. The
// report's text never comes into the chat: a report can run to many thousands of characters, past what one tool answer
// holds. With no board to open, the toast says so and names the report's file.
export async function openReport($: EngineInterface, fidelity: FidelityProgressClient): Promise<void> {
  const url = await runningBoardUrl($).catch(() => '')
  const link = url && (await projectPageUrl($, url, { report: fidelity.progress.ticket.name, fidelity: fidelity.slug }))
  if (link && (await openInBrowser($, link))) return
  const why = url ? `the browser did not open ${link}` : 'the board is not running and did not start'
  $.ui.toast(`${fidelity.slug} report: ${why}. The report is ${fidelity.progress.report_file || 'not saved yet'}`)
}

// The fidelity's help in the board's own help panel, as the ? on its board tile opens it, by the board's
// ?help=&fidelity= link, the board started first when it is not running.
export async function openHelp($: EngineInterface, fidelity: FidelityProgressClient): Promise<void> {
  const url = await runningBoardUrl($).catch(() => '')
  const link = url && (await boardPageUrl($, url, { help: fidelity.progress.ticket.name, fidelity: fidelity.slug }))
  if (link && (await openInBrowser($, link))) return
  $.ui.toast(`${fidelity.slug} help: ${url ? `the browser did not open ${link}` : 'the board is not running and did not start'}`)
}

// A file the server refuses shows the server's reason in its tab. A diagram's tab shows only its draw.io button.
export async function showFile($: EngineInterface, path: string): Promise<void> {
  if (isDiagram(path)) return update($, fidelityFiles, files => (files ? { ...files, shown: path } : files))
  const chatBar = await currentChatBar($)
  let text: string
  try {
    text = (await callTool<FileTextData>($, 'session.read_file', { session: chatBar.sessionFile, path })).text
  } catch (failure) {
    text = reasonOf(failure)
  }
  await update($, fidelityFiles, files => (files ? { ...files, shown: path, tabs: files.tabs.map(tab => (tab.path === path ? { ...tab, text } : tab)) } : files))
}

// A press on a file's editor tile opens the file in that app beside the chat, readied as a press on it in the status
// row readies it (App.open): the Story UI editor opens a Stories file at its page's ?file= link. A refusal shows in the
// server health panel, as a status row press's does.
export async function openInEditorApp($: EngineInterface, editor: string, path: string): Promise<void> {
  await openAppBesideChat($, editor, url => projectPageUrl($, url, { file: path }))
}

// The session's design view opens in Claude Design, in the browser, by its claude.ai link.
export async function openDesignView($: EngineInterface, link: string): Promise<void> {
  if (!(await openInBrowser($, link))) $.ui.toast(`The design view did not open: no program took ${link}`)
}

// A press on the shown file's title opens it in the editor the system opens its kind of file with, by its file:// link.
// A path from the project is named from the repository's own folder; an absolute one, such as a report's, is as it is.
const ABSOLUTE_PATH = /^([A-Za-z]:[\\/]|\/)/
export async function openFileInEditor($: EngineInterface, path: string): Promise<void> {
  const absolute = ABSOLUTE_PATH.test(path) ? path : `${await repositoryFolder($)}/${path}`
  const link = `file:///${absolute.split('\\').join('/').replace(/^\//, '')}`
  if (!(await openInBrowser($, link))) $.ui.toast(`${path} did not open: no program took ${link}`)
}

// A report whose saved graph is out of date has lost its graph's rules, so its fidelity is validated again to find them.
export async function validateAgain($: EngineInterface, slug: string): Promise<void> {
  const fidelity = (await currentChatBar($)).fidelities.find(entry => entry.slug === slug)
  if (fidelity) await runAction($, fidelity, 'validate')
}

export async function closeFiles($: EngineInterface): Promise<void> {
  await update($, fidelityFiles, () => null)
  await $.ui.close({ id: FILES_PANE })
}

// The person closed the pane with its own mark: the files view is forgotten, so the next open starts afresh.
export async function forgetFiles($: EngineInterface): Promise<void> {
  await update($, fidelityFiles, () => null)
}
