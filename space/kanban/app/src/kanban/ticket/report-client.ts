import type { ReportData, ReportRuleData, ViolationData } from '@cdd/space/kanban/ticket'

import type { BoardClient } from '../board/board-client'
import type { BoardPage } from '../board/board-page'
import type { TicketClient } from './ticket-client'

export const locationOf = (violation: ViolationData): string => (violation.line ? `${violation.location}:${violation.line}` : violation.location)

// The failing line is marked, so the agent edits the content validate judged, not a line near it.
const sourceOf = (violation: ViolationData): string[] =>
  violation.source.map(entry => `${entry.number === violation.line ? '>' : ' '} ${entry.number} | ${entry.text}`)

const errorOf = (violation: ViolationData): string[] => [`${locationOf(violation)}: ${violation.message}`, ...sourceOf(violation)]

// A fix in one format alone leaves the fidelity's other formats still breaking the rule, so every fix asks for all of them.
const EVERY_FORMAT = 'Fix every format of the fidelity: its documents, its diagrams, and its code.'

// The agent fixes from the report's own words, so it needs no second validate to find out what failed.
function fixPrompt(rule: ReportRuleData, violations: ViolationData[]): string {
  const slug = rule.fidelity.slug
  const errors = violations.flatMap((violation, index) => ['', `${index + 1}. ${errorOf(violation).join('\n')}`])
  return [
    `Fix ${violations.length === 1 ? 'this violation' : `these ${violations.length} violations`} of the ${slug} rule.`,
    '',
    `${rule.rule.slug}: ${rule.rule.body}`,
    ...errors,
    '',
    `Change each file so the content marked > follows the rule, and change nothing the errors do not name. ${EVERY_FORMAT} Then validate ${slug} with rule ${rule.rule.slug} on the files you changed.`,
  ].join('\n')
}

const fixViolationPrompt = (rule: ReportRuleData, violation: ViolationData): string => fixPrompt(rule, [violation])

const fixRulePrompt = (report: ReportClient, rule: ReportRuleData): string =>
  `Fix all violations of ${rule.rule.slug} found in this report: ${report.path}. ${EVERY_FORMAT}`

// The report already holds every violation, so the chat reads it there rather than from a copy in the message.
const fixReportPrompt = (report: ReportClient): string => `Fix all violations found in this report: ${report.path}. ${EVERY_FORMAT}`

// A Fix button's title says where the fix goes, as the repository's board sends fixes.
export const fixTitleOn = (board: BoardClient): string => (board.sendsFixesDirectly ? 'Send this fix to the chat' : "Put this fix in the chat's prompt to edit and send")

// A report as the side panel reads it, for the ticket whose report it is. ReportData has no generated class, because
// Python returns it as a plain result.
export class ReportClient {
  constructor(
    private readonly report: ReportData,
    private readonly ticket: TicketClient,
    private readonly page: BoardPage,
  ) {}

  // A report's fixes are for its ticket, so they name its session and go to its chat: into its prompt for the person to
  // edit before sending, unless the repository's board sends fixes directly.
  fixViolation(rule: ReportRuleData, violation: ViolationData): Promise<void> {
    return this.deliver(fixViolationPrompt(rule, violation))
  }

  fixRule(rule: ReportRuleData): Promise<void> {
    return this.deliver(fixRulePrompt(this, rule))
  }

  fixReport(): Promise<void> {
    return this.deliver(fixReportPrompt(this))
  }

  private deliver(prompt: string): Promise<void> {
    const text = this.ticket.inSession(prompt)
    return this.page.board.sendsFixesDirectly ? this.ticket.chat.command(text) : this.ticket.chat.fill(text)
  }

  get path(): string {
    return this.report.path
  }

  get text(): string {
    return this.report.text
  }

  get rules(): ReportRuleData[] {
    return this.report.rules
  }

  get hasSavedGraph(): boolean {
    return this.report.has_saved_graph
  }

  get isOutOfDate(): boolean {
    return this.report.is_out_of_date
  }

  // Graph hits and judged findings together, as Python counts them.
  get violationCount(): number {
    return this.report.violation_count
  }
}
