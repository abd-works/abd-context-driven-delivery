import type { ExplorerEntryData, GraphRuleData, GraphRulesCollectionData, ViolationData } from '@cdd/harness/graph/graph';

// One item of the explorer tree as Python sends it: a node's entry, the rules collection under it, or one rule.
export type TreeItem = ExplorerEntryData | GraphRulesCollectionData | GraphRuleData;

export function isRule(entry: TreeItem): entry is GraphRuleData {
  return 'status' in entry;
}

export function childrenOf(entry: TreeItem): TreeItem[] {
  return entry.children;
}

// How many entries below an explorer entry its answer left out; a rules collection and a rule leave none out.
export function childrenLeftOut(entry: TreeItem): number {
  return 'children_left_out' in entry ? entry.children_left_out : 0;
}

// The trees with branch in place of the closed entry it opens: the one that left its children out, its home place.
export function withBranch(trees: ExplorerEntryData[], branch: ExplorerEntryData): ExplorerEntryData[] {
  return trees.map((tree) => opening(tree, branch) as ExplorerEntryData);
}

function opening(entry: TreeItem, branch: ExplorerEntryData): TreeItem {
  if (entry.node_id === branch.node_id && childrenLeftOut(entry) > 0) return branch;
  if (isRule(entry) || !('children_left_out' in entry)) return entry;
  return { ...entry, children: entry.children.map((child) => opening(child, branch) as ExplorerEntryData | GraphRulesCollectionData) };
}

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
