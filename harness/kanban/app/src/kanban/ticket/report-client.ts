import type { ReportData, ReportRuleData, ViolationData } from '@cdd/harness/kanban/ticket'

import { guidanceSlug } from '../board/board-brand'

export const locationOf = (violation: ViolationData): string => (violation.line ? `${violation.location}:${violation.line}` : violation.location)

// The failing line is marked, so the agent edits the content validate judged, not a line near it.
const sourceOf = (violation: ViolationData): string[] =>
  violation.source.map(entry => `${entry.number === violation.line ? '>' : ' '} ${entry.number} | ${entry.text}`)

const errorOf = (violation: ViolationData): string[] => [`${locationOf(violation)}: ${violation.message}`, ...sourceOf(violation)]

// The agent fixes from the report's own words, so it needs no second validate to find out what failed.
function fixPrompt(rule: ReportRuleData, violations: ViolationData[]): string {
  const slug = guidanceSlug(rule.fidelity)
  const errors = violations.flatMap((violation, index) => ['', `${index + 1}. ${errorOf(violation).join('\n')}`])
  return [
    `Fix ${violations.length === 1 ? 'this violation' : `these ${violations.length} violations`} of the ${slug} rule.`,
    '',
    `${rule.name}: ${rule.description}`,
    ...errors,
    '',
    `Change each file so the content marked > follows the rule, and change nothing the errors do not name. Then validate ${slug} with rule ${rule.name} on the files you changed.`,
  ].join('\n')
}

export const fixViolationPrompt = (rule: ReportRuleData, violation: ViolationData): string => fixPrompt(rule, [violation])

export const fixRulePrompt = (rule: ReportRuleData): string => fixPrompt(rule, rule.violations)

// Every violation in one message, grouped under its rule, so one command clears the whole report.
export function fixReportPrompt(rules: ReportRuleData[]): string {
  const count = rules.reduce((total, rule) => total + rule.violations.length, 0)
  const slugs = [...new Set(rules.map(rule => guidanceSlug(rule.fidelity)))]
  const sections = rules.flatMap(rule => [
    '',
    `${rule.name}: ${rule.description}`,
    ...rule.violations.flatMap((violation, index) => ['', `${index + 1}. ${errorOf(violation).join('\n')}`]),
  ])
  return [
    `Fix these ${count} violations of ${rules.length} rules.`,
    ...sections,
    '',
    `Change each file so the content marked > follows its rule, and change nothing the errors do not name. Then validate ${slugs.join(' ')} on the files you changed.`,
  ].join('\n')
}

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
