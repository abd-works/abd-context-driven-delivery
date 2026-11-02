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
import { FORMAT_GROUPS } from './brand'

const DEFAULT_WIDTH = 60
export const SMALLEST_WIDTH = 30
const TAB_GROUPS = ['markdown', 'code', 'diagram']
const TAB_ORDER = TAB_GROUPS.flatMap(label => FORMAT_GROUPS.find(group => group.label === label)?.formats ?? [])

const sidePanels = atom({ plugin: 'cdd-board', key: 'sidePanels' } as const, [] as SidePanelJson[], { shape: 'panels-4' })
const panelWidths = atom({ plugin: 'cdd-board', key: 'panelWidths' } as const, {} as Record<string, number>)

export function currentPanels($: EngineInterface) {
  return read($, sidePanels)
}

const replacing = (panels: SidePanelJson[], panel: SidePanelJson): SidePanelJson[] => [
  ...panels.filter(entry => entry.kind !== panel.kind),
  panel,
]

// A panel opens at the width a person last dragged it to.
async function widthOf($: EngineInterface, kind: string): Promise<number> {
  return (await read($, panelWidths))[kind] ?? DEFAULT_WIDTH
}

async function showReport($: EngineInterface, ticket: string, fidelity: string, report: ReportJson): Promise<void> {
  const width = await widthOf($, 'report')
  await update($, sidePanels, panels => replacing(panels, { kind: 'report', ticket, fidelity, report, closedRules: [], width, isExpanded: false }))
}

export async function openReport($: EngineInterface, ticket: string, fidelity: string): Promise<void> {
  const report = await callTool<ReportJson>($, 'ticket.report', { ticket, fidelity })
  if (report) await showReport($, ticket, fidelity, report)
}

// A report panel with no fidelity holds the violations of every fidelity of its ticket.
export async function openViolations($: EngineInterface, ticket: string): Promise<void> {
  const report = await callTool<ReportJson>($, 'ticket.violations', { ticket })
  if (report) await showReport($, ticket, '', report)
}

// A fix changes the report on disk, so an open report is read again with the board.
export async function reloadReport($: EngineInterface): Promise<void> {
  const open = (await read($, sidePanels)).find((panel): panel is ReportPanelJson => panel.kind === 'report')
  if (!open) return
  const report = open.fidelity
    ? await callTool<ReportJson>($, 'ticket.report', { ticket: open.ticket, fidelity: open.fidelity })
    : await callTool<ReportJson>($, 'ticket.violations', { ticket: open.ticket })
  if (report) await update($, sidePanels, panels => panels.map(panel => (panel.kind === 'report' ? { ...panel, report } : panel)))
}

// rule is its fidelity and name, because one report can list a rule on two fidelities.
export function toggleRule($: EngineInterface, rule: string) {
  return update($, sidePanels, panels =>
    panels.map(panel => {
      if (panel.kind !== 'report') return panel
      const isClosed = panel.closedRules.includes(rule)
      return { ...panel, closedRules: isClosed ? panel.closedRules.filter(name => name !== rule) : [...panel.closedRules, rule] }
    }),
  )
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
  const files = await callTool<TicketFilesJson>($, 'ticket.files', { ticket, fidelities: slugs })
  if (!files) {
    $.ui.toast(`The files of ${ticket} could not be read`)
    return
  }
  const panel: FilesPanelJson = { kind: 'files', ticket, slugs, files, mode, tabs: [], activeTab: '', texts: {}, lines: {}, width: await widthOf($, 'files'), isExpanded: false }
  await update($, sidePanels, panels => replacing(panels, panel))
  if (mode === 'files') await chooseFilesMode($, mode)
}

// Tabs follow what is offered now; one a person closed stays closed, and one a violation opened stays open.
function withFiles(entry: FilesPanelJson, files: TicketFilesJson): FilesPanelJson {
  const before = offeredTabs(entry.files, entry.slugs)
  const after = offeredTabs(files, entry.slugs)
  const kept = entry.tabs.filter(tab => after.includes(tab) || !before.includes(tab))
  const added = entry.tabs.length ? after.filter(tab => !before.includes(tab) && !kept.includes(tab)) : []
  const tabs = [...kept, ...added]
  return { ...entry, files, tabs, activeTab: tabs.includes(entry.activeTab) ? entry.activeTab : tabs[0] ?? '' }
}

// Generating changes what exists, so an open Files panel is read again with the board.
export async function reloadFiles($: EngineInterface): Promise<void> {
  const panel = await filesPanel($)
  if (!panel) return
  const files = await callTool<TicketFilesJson>($, 'ticket.files', { ticket: panel.ticket, fidelities: panel.slugs })
  if (files) await updateFiles($, entry => withFiles(entry, files))
}

export async function reloadFileText($: EngineInterface): Promise<void> {
  const panel = await filesPanel($)
  if (panel?.mode !== 'files' || !panel.activeTab) return
  const path = panel.activeTab
  const text = await textOf($, panel.ticket, path, existsIn(panel, path) || Boolean(panel.texts[path]))
  await updateFiles($, entry => ({ ...entry, texts: { ...entry.texts, [path]: text } }))
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

const showingTab = (entry: FilesPanelJson, path: string, text: string, line: number): FilesPanelJson => ({
  ...entry,
  mode: 'files',
  tabs: entry.tabs.includes(path) ? entry.tabs : [...entry.tabs, path],
  activeTab: path,
  texts: { ...entry.texts, [path]: text },
  lines: { ...entry.lines, [path]: line },
})

export async function openFileTab($: EngineInterface, path: string): Promise<void> {
  const panel = await filesPanel($)
  if (!panel) return
  const text = await textOf($, panel.ticket, path, existsIn(panel, path))
  await updateFiles($, entry => showingTab(entry, path, text, 0))
}

// A violation can name a file its fidelity does not declare, so its text is read whatever the panel lists.
export async function openFileAtLine($: EngineInterface, ticket: string, fidelity: string, path: string, line: number): Promise<void> {
  if ((await filesPanel($))?.ticket !== ticket) await openFiles($, ticket, [fidelity], 'list')
  const text = await textOf($, ticket, path, true)
  await updateFiles($, entry => showingTab(entry, path, text, line))
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
  const width = await widthOf($, 'help')
  await update($, sidePanels, panels => replacing(panels, { kind: 'help', help, width, isExpanded: false }))
}

export function closePanel($: EngineInterface, kind: string) {
  return update($, sidePanels, panels => panels.filter(panel => panel.kind !== kind))
}

export function closeTicketPanels($: EngineInterface, ticket: string) {
  return update($, sidePanels, panels => panels.filter(panel => panel.kind === 'help' || panel.ticket !== ticket))
}

// One panel is expanded at a time.
export function togglePanelExpanded($: EngineInterface, kind: string) {
  return update($, sidePanels, panels => panels.map(panel => ({ ...panel, isExpanded: panel.kind === kind && !panel.isExpanded })))
}

export async function setPanelWidth($: EngineInterface, kind: string, width: number): Promise<void> {
  const kept = Math.max(width, SMALLEST_WIDTH)
  await update($, panelWidths, widths => ({ ...widths, [kind]: kept }))
  await update($, sidePanels, panels => panels.map(panel => (panel.kind === kind ? { ...panel, width: kept } : panel)))
}
