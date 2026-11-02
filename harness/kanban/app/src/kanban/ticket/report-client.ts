import type { ReportData, ReportRuleData, ViolationData } from '@cdd/harness/kanban/ticket'

export const locationOf = (violation: ViolationData): string => (violation.line ? `${violation.location}:${violation.line}` : violation.location)

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
