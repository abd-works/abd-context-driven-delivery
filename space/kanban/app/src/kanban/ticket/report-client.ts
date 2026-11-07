import type { ReportData, ReportRuleData, ViolationData } from '@cdd/space/kanban/ticket'


export const locationOf = (violation: ViolationData): string => (violation.line ? `${violation.location}:${violation.line}` : violation.location)

// The failing line is marked, so the agent edits the content validate judged, not a line near it.
const sourceOf = (violation: ViolationData): string[] =>
  violation.source.map(entry => `${entry.number === violation.line ? '>' : ' '} ${entry.number} | ${entry.text}`)

const errorOf = (violation: ViolationData): string[] => [`${locationOf(violation)}: ${violation.message}`, ...sourceOf(violation)]

// A fix in one format alone leaves the fidelity's other formats still breaking the rule, so every fix asks for all of them.
const EVERY_FORMAT = 'Fix every format of the fidelity: its documents, its diagrams, and its code.'

// The agent fixes from the report's own words, so it needs no second validate to find out what failed.
function fixPrompt(rule: ReportRuleData, violations: ViolationData[]): string {
  const slug = rule.fidelity
  const errors = violations.flatMap((violation, index) => ['', `${index + 1}. ${errorOf(violation).join('\n')}`])
  return [
    `Fix ${violations.length === 1 ? 'this violation' : `these ${violations.length} violations`} of the ${slug} rule.`,
    '',
    `${rule.name}: ${rule.description}`,
    ...errors,
    '',
    `Change each file so the content marked > follows the rule, and change nothing the errors do not name. ${EVERY_FORMAT} Then validate ${slug} with rule ${rule.name} on the files you changed.`,
  ].join('\n')
}

export const fixViolationPrompt = (rule: ReportRuleData, violation: ViolationData): string => fixPrompt(rule, [violation])

export const fixRulePrompt = (report: ReportClient, rule: ReportRuleData): string =>
  `Fix all violations of ${rule.name} found in this report: ${report.path}. ${EVERY_FORMAT}`

// The report already holds every violation, so the chat reads it there rather than from a copy in the message.
export const fixReportPrompt = (report: ReportClient): string => `Fix all violations found in this report: ${report.path}. ${EVERY_FORMAT}`

// A report as the side panel reads it. ReportData has no generated class, because Python returns it as a plain result.
export class ReportClient {
  constructor(private readonly data: ReportData) {}

  get path(): string {
    return this.data.path
  }

  get text(): string {
    return this.data.text
  }

  get rules(): ReportRuleData[] {
    return this.data.rules
  }

  get hasSavedGraph(): boolean {
    return this.data.has_saved_graph
  }

  get violationCount(): number {
    return this.rules.reduce((total, rule) => total + rule.count, 0)
  }
}
