import type { ExplorerEntryData, GraphRuleData, GraphRulesCollectionData, ViolationData } from '@cdd/harness/graph/graph';
import type { ViolationFocus } from '../source/violation-prompt';

// One item of the explorer tree as Python sends it: a node's entry, the rules collection under it, or one rule.
export type TreeItem = ExplorerEntryData | GraphRulesCollectionData | GraphRuleData;

export function isRule(item: TreeItem): item is GraphRuleData {
  return 'status' in item;
}

export function childrenOf(item: TreeItem): TreeItem[] {
  return item.children;
}

// How many entries below an explorer entry its answer left out; a rules collection and a rule leave none out.
export function childrenLeftOut(item: TreeItem): number {
  return 'children_left_out' in item ? item.children_left_out : 0;
}

// The trees with branch in place of the closed entry it opens: the one that left its children out, its home place.
export function withBranch(trees: ExplorerEntryData[], branch: ExplorerEntryData): ExplorerEntryData[] {
  return trees.map((tree) => opening(tree, branch) as ExplorerEntryData);
}

function opening(item: TreeItem, branch: ExplorerEntryData): TreeItem {
  if (item.node_id === branch.node_id && childrenLeftOut(item) > 0) return branch;
  if (isRule(item) || !('children_left_out' in item)) return item;
  return { ...item, children: item.children.map((child) => opening(child, branch) as ExplorerEntryData | GraphRulesCollectionData) };
}

export type GraphSelection = {
  nodeId: string;
  rule?: string;
  violation?: ViolationFocus;
};

export function ruleHits(node: { violation?: string; violations?: ViolationData[] }): ViolationData[] {
  if (node.violations?.length) {
    return node.violations;
  }
  if (node.violation) {
    return [{ rule: '', practice: '', node_id: '', subject: '', location: '', line: 0, end_line: 0, message: node.violation, severity: 'error', source: [] }];
  }
  return [];
}

export function selectionForRule(ownerId: string, node: GraphRuleData): GraphSelection {
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
          startLine: first?.line ?? undefined,
          endLine: first?.end_line ?? undefined,
        }
      : undefined,
  };
}
