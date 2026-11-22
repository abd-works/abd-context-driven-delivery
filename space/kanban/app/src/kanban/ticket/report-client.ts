import type { ReportData, ReportRuleData, ViolationData } from '@cdd/space/kanban/ticket'

import type { BoardClient } from '../board/board-client'
import type { BoardPage } from '../board/board-page'
import type { TicketClient } from './ticket-client'

export const locationOf = (violation: ViolationData): string => (violation.line ? `${violation.location}:${violation.line}` : violation.location)

// What a violation's Fix and False send, which Python writes beside each violation of a rule, in the same order.
const promptsOf = (rule: ReportRuleData, violation: ViolationData) => rule.violation_prompts[rule.violations.indexOf(violation)]

// A Fix button's title says where the fix goes, as the repository's board sends fixes.
export const fixTitleOn = (board: BoardClient): string => (board.sendsFixesDirectly ? 'Send this fix to the chat' : "Put this fix in the chat's prompt to edit and send")

// A False button's title says what it asks and where that goes.
export const falseTitleOn = (board: BoardClient): string =>
  board.sendsFixesDirectly ? 'Say this violation is false: the chat investigates the rule' : "Say this violation is false: put the request to investigate the rule in the chat's prompt"

export const ACCEPT_TITLE = 'Accept this violation as it is: no later validation reports it while it stays the same'
export const TAKE_BACK_TITLE = 'Take this acceptance back: the violation is reported again'

// A report as the side panel reads it, for the ticket whose report it is. ReportData has no generated class, because
// Python returns it as a plain result.
export class ReportClient {
  constructor(
    private readonly report: ReportData,
    private readonly ticket: TicketClient,
    private readonly page: BoardPage,
  ) {}

  // A report's fixes are for its ticket, so they go to its chat in the words Python wrote, which name its session: into
  // its prompt for the person to edit before sending, unless the repository's board sends fixes directly.
  fixViolation(rule: ReportRuleData, violation: ViolationData): Promise<void> {
    return this.deliver(promptsOf(rule, violation)?.fix ?? '')
  }

  // The person says the finding is wrong: the chat investigates the rule, in the same place a fix would go.
  reportFalseViolation(rule: ReportRuleData, violation: ViolationData): Promise<void> {
    return this.deliver(promptsOf(rule, violation)?.false ?? '')
  }

  // The person accepts the finding as it is. Python keeps the acceptance, by the rule and the id of the node the
  // violation is on, and decides what it covers; the page names the violation as the report showed it and reads the
  // open report again.
  async acceptViolation(rule: ReportRuleData, violation: ViolationData): Promise<void> {
    const kept = await this.progressOf(rule)?.acceptViolation(rule.rule.slug, violation.message, violation.location, violation.line ?? 0, violation.node_id)
    if (kept) await this.page.panels.reload()
  }

  // The person takes an acceptance back, so the violation is reported again.
  async reopenViolation(rule: ReportRuleData, violation: ViolationData): Promise<void> {
    const reopened = await this.progressOf(rule)?.reopenViolation(rule.rule.slug, violation.message, violation.location, violation.line ?? 0, violation.node_id)
    if (reopened) await this.page.panels.reload()
  }

  // A rule names its fidelity, since a ticket's report lists the rules of several; the fidelity's progress keeps its report.
  private progressOf(rule: ReportRuleData) {
    return this.ticket.work.progressNamed(rule.fidelity.slug)
  }

  fixRule(rule: ReportRuleData): Promise<void> {
    return this.deliver(rule.fix_prompt)
  }

  fixReport(): Promise<void> {
    return this.deliver(this.report.fix_prompt)
  }

  private deliver(prompt: string): Promise<void> {
    return this.page.board.sendsFixesDirectly ? this.ticket.chat.command(prompt) : this.ticket.chat.fill(prompt)
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

  // Graph hits and judged findings together, as Python counts them, without the ones a person accepted.
  get violationCount(): number {
    return this.report.violation_count
  }

  // The violations a person accepted, under the rule each breaks, which Python leaves out of the rules and the count.
  get accepted(): ReportRuleData[] {
    return this.report.accepted
  }

  get acceptedCount(): number {
    return this.report.accepted_count
  }
}
