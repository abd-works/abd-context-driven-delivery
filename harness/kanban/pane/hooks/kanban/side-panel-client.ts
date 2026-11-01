import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type {
  FilesPanelJson,
  FileTextJson,
  HelpJson,
  ReportJson,
  ReportPanelJson,
  SidePanelJson,
  TicketFilesJson,
} from '../../types'
import { callTool } from './board-client'

const DEFAULT_WIDTH = 60
export const SMALLEST_WIDTH = 30
const TAB_ORDER = ['drawio', 'markdown']

const sidePanels = atom({ plugin: 'cdd-board', key: 'sidePanels' } as const, [] as SidePanelJson[], { shape: 'panels-1' })

export function currentPanels($: EngineInterface) {
  return read($, sidePanels)
}

const replacing = (panels: SidePanelJson[], panel: SidePanelJson): SidePanelJson[] => [
  ...panels.filter(entry => entry.kind !== panel.kind),
  panel,
]

export async function openReport($: EngineInterface, ticket: string, fidelity: string): Promise<void> {
  const report = await callTool<ReportJson>($, 'ticket.report', { ticket, fidelity })
  if (!report) return
  await update($, sidePanels, panels => replacing(panels, { kind: 'report', ticket, fidelity, report, width: DEFAULT_WIDTH, isExpanded: false }))
}

// A fix changes the report on disk, so an open report is read again with the board.
export async function reloadReport($: EngineInterface): Promise<void> {
  const open = (await read($, sidePanels)).find((panel): panel is ReportPanelJson => panel.kind === 'report')
  if (!open) return
  const report = await callTool<ReportJson>($, 'ticket.report', { ticket: open.ticket, fidelity: open.fidelity })
  if (report) await update($, sidePanels, panels => panels.map(panel => (panel.kind === 'report' ? { ...panel, report } : panel)))
}

// One tab per format the fidelity offers, generated or not: a story map always shows its markdown and its diagram.
const offeredTabs = (files: TicketFilesJson, slugs: string[]): string[] =>
  slugs.flatMap(slug =>
    [...TAB_ORDER, ...Object.keys(files[slug] ?? {}).filter(label => !TAB_ORDER.includes(label))].flatMap(label =>
      (files[slug]?.[label] ?? []).map(entry => entry.path),
    ),
  )

async function textOf($: EngineInterface, ticket: string, path: string, existing: boolean): Promise<string> {
  if (!existing) return ''
  return (await callTool<FileTextJson>($, 'ticket.read_file', { ticket, path }))?.text ?? ''
}

const existsIn = (panel: { files: TicketFilesJson }, path: string): boolean =>
  Object.values(panel.files).some(formats => Object.values(formats).some(entries => entries.some(entry => entry.path === path && entry.exists)))

export async function openFiles($: EngineInterface, ticket: string, slugs: string[], mode: string): Promise<void> {
  const files = await callTool<TicketFilesJson>($, 'ticket.files', { ticket })
  if (!files) return
  const panel: FilesPanelJson = { kind: 'files', ticket, slugs, files, mode, tabs: [], activeTab: '', texts: {}, width: DEFAULT_WIDTH, isExpanded: false }
  await update($, sidePanels, panels => replacing(panels, panel))
  if (mode === 'files') await chooseFilesMode($, mode)
}

function updateFiles($: EngineInterface, change: (panel: FilesPanelJson) => FilesPanelJson) {
  return update($, sidePanels, panels => panels.map(panel => (panel.kind === 'files' ? change(panel) : panel)))
}

async function filesPanel($: EngineInterface) {
  return (await read($, sidePanels)).find((panel): panel is FilesPanelJson => panel.kind === 'files')
}

export async function chooseFilesMode($: EngineInterface, mode: string): Promise<void> {
  const panel = await filesPanel($)
  if (!panel) return
  const tabs = mode === 'files' && !panel.tabs.length ? offeredTabs(panel.files, panel.slugs) : panel.tabs
  await updateFiles($, entry => ({ ...entry, mode, tabs, activeTab: entry.activeTab || tabs[0] || '' }))
  if (mode === 'files' && tabs[0]) await openFileTab($, panel.activeTab || tabs[0])
}

export async function openFileTab($: EngineInterface, path: string): Promise<void> {
  const panel = await filesPanel($)
  if (!panel) return
  const text = await textOf($, panel.ticket, path, existsIn(panel, path))
  await updateFiles($, entry => ({
    ...entry,
    mode: 'files',
    tabs: entry.tabs.includes(path) ? entry.tabs : [...entry.tabs, path],
    activeTab: path,
    texts: { ...entry.texts, [path]: text },
  }))
}

export function closeFileTab($: EngineInterface, path: string) {
  return updateFiles($, entry => {
    const tabs = entry.tabs.filter(tab => tab !== path)
    return { ...entry, tabs, mode: tabs.length ? 'files' : 'list', activeTab: entry.activeTab === path ? tabs[0] ?? '' : entry.activeTab }
  })
}

export async function openHelp($: EngineInterface, practice: string, fidelity: string): Promise<void> {
  const help = await callTool<HelpJson>($, 'board.help', { practice, fidelity })
  if (!help) return
  await update($, sidePanels, panels => replacing(panels, { kind: 'help', help, width: DEFAULT_WIDTH, isExpanded: false }))
}

export function closePanel($: EngineInterface, kind: string) {
  return update($, sidePanels, panels => panels.filter(panel => panel.kind !== kind))
}

// One panel is expanded at a time.
export function togglePanelExpanded($: EngineInterface, kind: string) {
  return update($, sidePanels, panels => panels.map(panel => ({ ...panel, isExpanded: panel.kind === kind && !panel.isExpanded })))
}

export function setPanelWidth($: EngineInterface, kind: string, width: number) {
  return update($, sidePanels, panels => panels.map(panel => (panel.kind === kind ? { ...panel, width: Math.max(width, SMALLEST_WIDTH) } : panel)))
}
