import { BoardClientGenerated } from '@cdd/space/kanban/board'

import type { FidelityProgressClient } from '../ticket/fidelity-progress-client'
import type { TicketClient } from '../ticket/ticket-client'
import type { BoardApi } from './board-api'
import type { BoardStore, ReportPanel } from '../shared/board-store'
import type { PracticeClient } from './practice-client'

const DEFAULT_WIDTH = 640
export const SMALLEST_WIDTH = 360
const LARGEST_WIDTH = 1200

// The panels beside the board, and the report and help panels. The files panel has its own client.
export class SidePanelClient {
  constructor(
    private readonly store: BoardStore,
    private readonly api: BoardApi,
  ) {}

  private changeReport(change: (panel: ReportPanel) => ReportPanel): void {
    this.store.changePanel('report', change)
  }

  widthOf(kind: string): number {
    return this.store.state.panelWidths[kind] ?? DEFAULT_WIDTH
  }

  setWidth(kind: string, wanted: number): void {
    const width = Math.min(Math.max(wanted, SMALLEST_WIDTH), LARGEST_WIDTH)
    this.store.change(state => ({ panelWidths: { ...state.panelWidths, [kind]: width } }))
  }

  // With no fidelity's progress, a report panel holds the violations of every fidelity of its ticket.
  async openReport(ticket: TicketClient, progress: FidelityProgressClient | null): Promise<void> {
    const report = await ticket.work.reportOf(progress)
    if (report) this.store.showPanel({ kind: 'report', ticket, progress, report, closedRules: [], isExpanded: false })
  }

  // rule is its fidelity and name, because one report can list a rule on two fidelities.
  toggleRule(rule: string): void {
    this.changeReport(panel => {
      const isClosed = panel.closedRules.includes(rule)
      return { ...panel, closedRules: isClosed ? panel.closedRules.filter(name => name !== rule) : [...panel.closedRules, rule] }
    })
  }

  // A practice's help comes from the board, which holds the practices.
  async openPracticeHelp(practice: PracticeClient): Promise<void> {
    const help = await new BoardClientGenerated(this.api).help(practice.key)
    if (help) this.store.showPanel({ kind: 'help', help, isExpanded: false })
  }

  // A fidelity's help comes from its progress on the ticket, which holds the fidelity and its stage.
  async openFidelityHelp(progress: FidelityProgressClient): Promise<void> {
    const help = await progress.help()
    if (help) this.store.showPanel({ kind: 'help', help, isExpanded: false })
  }

  close(kind: string): void {
    this.store.change(state => ({ panels: state.panels.filter(panel => panel.kind !== kind) }))
  }

  // A ticket let go of takes its report and files panels with it; each board read makes new ticket clients, so a panel
  // holds the ticket it was opened on under the same name.
  closeTicketPanels(ticket: TicketClient): void {
    this.store.change(state => ({ panels: state.panels.filter(panel => panel.kind === 'help' || panel.ticket.name !== ticket.name) }))
  }

  // One panel is expanded at a time.
  toggleExpanded(kind: string): void {
    this.store.change(state => ({ panels: state.panels.map(panel => ({ ...panel, isExpanded: panel.kind === kind && !panel.isExpanded })) }))
  }

  // A fix changes the report on disk, so an open report is read again with the board.
  async reload(): Promise<void> {
    const open = this.store.panelOf('report')
    if (!open) return
    const report = await open.ticket.work.reportOf(open.progress)
    if (report) this.changeReport(panel => ({ ...panel, report }))
  }
}
