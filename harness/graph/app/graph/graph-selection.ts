import type { GraphTree, RuleHit } from '../filter/FilterClient';
import type { ViolationFocus } from '../source/violation-prompt';

export type GraphSelection = {
  nodeId: string;
  rule?: string;
  violation?: ViolationFocus;
};

export function ruleHits(node: { violation?: string; violations?: RuleHit[] }): RuleHit[] {
  if (node.violations?.length) {
    return node.violations;
  }
  if (node.violation) {
    return [{ message: node.violation }];
  }
  return [];
}

export function selectionForRule(ownerId: string, node: GraphTree): GraphSelection {
  const hits = ruleHits(node);
  const first = hits[0];
  const violating = node.status === 'violating' && hits.length > 0;
  return {
    nodeId: ownerId,
    rule: node.name,
    violation: violating
      ? {
          rule: node.name,
          message: hits.map((hit) => hit.message).filter(Boolean).join('\n'),
          ruleText: node.text || undefined,
          startLine: first?.start,
          endLine: first?.end,
        }
      : undefined,
  };
}
