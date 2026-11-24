import type { GraphRuleData, ViolationData } from '@cdd/harness/graph/graph';

// One place a selected rule is broken: what it says is wrong there and the lines it names, which the source view marks
// and offers Fix this one for.
export type ViolationPlace = {
  message: string;
  startLine?: number;
  endLine?: number;
  // The words of the comment Fix this one puts on the place's lines, as Python wrote them beside a file's violation; a
  // page that sends the whole fix asks Python for it instead.
  correctionComment?: string;
};

// The rule a person selected, with every place it is broken.
export type ViolationFocus = {
  rule: string;
  places: ViolationPlace[];
  // A rule that requires a judge listed it for a reading; nothing has decided it is wrong.
  isCandidate?: boolean;
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

// The rule selected on a node in the Graph app: one place, at its first violation's lines, saying every message it
// gives there, since the Graph app's fix of a rule on a node is one fix of all of them.
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
          places: [{ message: hits.map((hit) => hit.message).filter(Boolean).join('\n'), startLine: first?.line ?? undefined, endLine: first?.end_line ?? undefined }],
          isCandidate,
        }
      : undefined,
  };
}
