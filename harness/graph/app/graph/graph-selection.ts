import type { GraphRuleData, ViolationData } from '@cdd/harness/graph/graph';

// The violation a selected rule found, with the lines it was found on, which the source view marks.
export type ViolationFocus = {
  rule: string;
  message: string;
  startLine?: number;
  endLine?: number;
  // A rule that requires a judge listed it for a reading; nothing has decided it is wrong.
  isCandidate?: boolean;
  // The words of the comment Correct puts on the violation's lines, as Python wrote them beside a file's violation; a
  // page that sends the whole correction asks Python for it instead.
  correctionComment?: string;
};

export type GraphSelection = {
  nodeId: string;
  rule?: string;
  violation?: ViolationFocus;
};

// The violations rule found on its node; none for a rule that passes.
export function ruleHits(rule: GraphRuleData): ViolationData[] {
  return rule.violations ?? [];
}

export function selectionForRule(ownerId: string, rule: GraphRuleData): GraphSelection {
  const hits = ruleHits(rule);
  const first = hits[0];
  const isCandidate = rule.status === 'candidate';
  const violating = (rule.status === 'violating' || isCandidate) && hits.length > 0;
  return {
    nodeId: ownerId,
    rule: rule.name,
    violation: violating
      ? {
          rule: rule.name,
          message: hits.map((hit) => hit.message).filter(Boolean).join('\n'),
          startLine: first?.line ?? undefined,
          endLine: first?.end_line ?? undefined,
          isCandidate,
        }
      : undefined,
  };
}
