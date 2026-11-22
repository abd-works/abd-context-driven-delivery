import type { ExplorerEntryData, GraphRuleData, GraphRulesCollectionData } from '@cdd/harness/graph/graph';

// One item of the explorer tree as Python sends it: a node's entry, the rules collection under it, or one rule.
export type TreeItem = ExplorerEntryData | GraphRulesCollectionData | GraphRuleData;

// The practice trees the explorer shows, as Python answered them, with each branch read later in the place of the entry
// that left it out. It answers what the page asks of the trees: the rules a node runs, whether an entry breaks one.
export class ExplorerTrees {
  static readonly NONE = new ExplorerTrees([]);

  constructor(readonly entries: ExplorerEntryData[]) {}

  // Whether item is one rule, which carries its status.
  static isRule(item: TreeItem): item is GraphRuleData {
    return 'status' in item;
  }

  // How many entries below item its answer left out; a rules collection and a rule leave none out.
  static leftOutOf(item: TreeItem): number {
    return 'children_left_out' in item ? item.children_left_out : 0;
  }

  // These trees with branch in place of the closed entry it opens: the one that left its children out, its home place.
  withBranch(branch: ExplorerEntryData): ExplorerTrees {
    return new ExplorerTrees(this.entries.map((entry) => opening(entry, branch) as ExplorerEntryData));
  }

  // The rules the node nodeId runs, as the rules collection under it holds them; none for a node the trees do not hold.
  rulesOf(nodeId: string): GraphRuleData[] {
    const node = found(this.entries, nodeId);
    const holder: TreeItem | undefined = node?.children.find((child) => child.type === 'rules');
    return holder ? (holder.children as TreeItem[]).filter(ExplorerTrees.isRule) : [];
  }

  // Whether a rule the entry runs is broken: its rules collection holds a rule that is violating.
  isViolating(entry: TreeItem): boolean {
    return entry.children.some((child) => child.name === 'rules' && child.children.some((hit) => ExplorerTrees.isRule(hit) && hit.status === 'violating'));
  }
}

function opening(entry: TreeItem, branch: ExplorerEntryData): TreeItem {
  if (entry.node_id === branch.node_id && ExplorerTrees.leftOutOf(entry) > 0) return branch;
  if (ExplorerTrees.isRule(entry) || !('children_left_out' in entry)) return entry;
  return { ...entry, children: entry.children.map((child) => opening(child, branch) as ExplorerEntryData | GraphRulesCollectionData) };
}

function found(items: TreeItem[], nodeId: string): TreeItem | null {
  for (const item of items) {
    if (item.node_id === nodeId) return item;
    const below = found(item.children, nodeId);
    if (below) return below;
  }
  return null;
}
