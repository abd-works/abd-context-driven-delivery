import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { FileEntryData, ReportData } from '@cdd/space/kanban/fidelity-progress'
import type { FileTextData } from '@cdd/space/session/session'

import type { FidelityFilesJson } from '../../types'
import { reasonOf } from '../shared/failure'
import { callTool, currentChatBar } from './chat-bar-client'
import type { FidelityProgressClient } from './fidelity-progress-client'

// The files view of one fidelity: a tab per file fidelity-progress.files declares, each tab's text read by session.read_file.
// It opens in a pane of its own beside the chat, as the board's files panel does, never above the prompt in the chat.
export const FILES_PANE = 'cdd-files'
const fidelityFiles = atom({ plugin: 'cdd-board', key: 'fidelityFiles' } as const, null as FidelityFilesJson)

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
  try {
    const files = await callTool<Record<string, FileEntryData[]>>($, 'fidelity-progress.files', { ticket: fidelity.progress.ticket.name, fidelity: fidelity.slug })
    const paths = [...new Set(Object.values(files).flat().map(entry => entry.path))]
    await update($, fidelityFiles, () => ({ fidelity: fidelity.slug, tabs: paths.map(path => ({ path, text: null })), shown: paths[0] ?? null }))
    await openPane($, `${fidelity.slug} files`)
    if (paths[0]) await showFile($, paths[0])
  } catch (failure) {
    $.ui.toast(`${fidelity.slug} files: ${reasonOf(failure)}`)
  }
}

// The fidelity's latest validation report in its own tab of the files pane, as the board opens it in its side panel
// from a violation count, so the person reads the violations before telling the agent to fix them.
export async function openReport($: EngineInterface, fidelity: FidelityProgressClient): Promise<void> {
  try {
    const report = await callTool<ReportData>($, 'fidelity-progress.report', { ticket: fidelity.progress.ticket.name, fidelity: fidelity.slug })
    await update($, fidelityFiles, () => ({ fidelity: fidelity.slug, tabs: [{ path: report.path, text: report.text }], shown: report.path }))
    await openPane($, `${fidelity.slug} report`)
  } catch (failure) {
    $.ui.toast(`${fidelity.slug} report: ${reasonOf(failure)}`)
  }
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
  await update($, fidelityFiles, files => (files ? { ...files, shown: path, tabs: files.tabs.map(tab => (tab.path === path ? { path, text } : tab)) } : files))
}

// The chat cannot draw a diagram, so the agent opens it in the draw.io editor in the browser pane, as the drawio-viewer
// rule says.
export async function openInDrawio($: EngineInterface, path: string): Promise<void> {
  const answer = await $.prompt.submit({ text: `Open ${path} in the draw.io viewer.`, asUser: true })
  if (answer.drop !== undefined) $.ui.toast(`${path} did not open: ${answer.drop || 'the chat dropped it'}`)
}

export async function closeFiles($: EngineInterface): Promise<void> {
  await update($, fidelityFiles, () => null)
  await $.ui.close({ id: FILES_PANE })
}

// The person closed the pane with its own mark: the files view is forgotten, so the next open starts afresh.
export async function forgetFiles($: EngineInterface): Promise<void> {
  await update($, fidelityFiles, () => null)
}
