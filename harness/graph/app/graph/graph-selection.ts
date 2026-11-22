import type { GraphRuleData, ViolationData } from '@cdd/harness/graph/graph';

// The violation a selected rule found, with the lines it was found on, which the source view marks.
export type ViolationFocus = {
  rule: string;
  message: string;
  startLine?: number;
  endLine?: number;
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
  const violating = rule.status === 'violating' && hits.length > 0;
  return {
    nodeId: ownerId,
    rule: rule.name,
    violation: violating
      ? {
          rule: rule.name,
          message: hits.map((hit) => hit.message).filter(Boolean).join('\n'),
          startLine: first?.line ?? undefined,
          endLine: first?.end_line ?? undefined,
        }
      : undefined,
  };
}
