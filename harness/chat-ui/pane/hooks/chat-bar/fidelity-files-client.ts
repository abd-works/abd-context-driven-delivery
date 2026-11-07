import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { FileEntryData } from '@cdd/space/kanban/fidelity-progress'
import type { FileTextData } from '@cdd/space/session/session'

import type { FidelityFilesJson } from '../../types'
import { reasonOf } from '../failure'
import { callTool, currentChatBar } from './chat-bar-client'
import type { FidelityProgressClient } from './fidelity-progress-client'

// The files view of one fidelity: a tab per file fidelity-progress.files declares, each tab's text read by session.read_file.
const fidelityFiles = atom({ plugin: 'cdd-board', key: 'fidelityFiles' } as const, null as FidelityFilesJson)

// The files view orders a fidelity's files as the board does: markdown, then code, then diagrams.
const fileOrder = (path: string): number => (path.endsWith('.md') ? 0 : path.endsWith('.drawio') ? 2 : 1)

// Atom fidelityFiles, declared in pane/types/index.d.ts and kept in this file.
export function currentFidelityFiles($: EngineInterface) {
  return read($, fidelityFiles)
}

// One tab per file the fidelity declares; the first tab's text is read straight away.
export async function openFiles($: EngineInterface, fidelity: FidelityProgressClient): Promise<void> {
  const chatBar = await currentChatBar($)
  try {
    const files = await callTool<Record<string, FileEntryData[]>>($, 'fidelity-progress.files', { ticket: fidelity.progress.ticket.name, fidelity: fidelity.slug })
    const paths = [...new Set(Object.values(files).flat().map(entry => entry.path))].sort((a, b) => fileOrder(a) - fileOrder(b))
    await update($, fidelityFiles, () => ({ fidelity: fidelity.slug, tabs: paths.map(path => ({ path, text: null })), shown: paths[0] ?? null }))
    if (paths[0]) await showFile($, paths[0])
  } catch (failure) {
    $.ui.toast(`${fidelity.slug} files: ${reasonOf(failure)}`)
  }
}

// A file the server refuses shows the server's reason in its tab.
export async function showFile($: EngineInterface, path: string): Promise<void> {
  const chatBar = await currentChatBar($)
  let text: string
  try {
    text = (await callTool<FileTextData>($, 'session.read_file', { session: chatBar.sessionFile, path })).text
  } catch (failure) {
    text = reasonOf(failure)
  }
  await update($, fidelityFiles, files => (files ? { ...files, shown: path, tabs: files.tabs.map(tab => (tab.path === path ? { path, text } : tab)) } : files))
}

export async function closeFiles($: EngineInterface): Promise<void> {
  await update($, fidelityFiles, () => null)
}
