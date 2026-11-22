import { describe, expect, it } from 'vitest';

import type { ExplorerEntryData, GraphRuleData } from '@cdd/harness/graph/graph';

import { ExplorerTrees } from './explorer-trees';

const rule = (name: string, status: string): GraphRuleData => ({ type: 'Rule', name, node_id: '', slug: name, body: '', status, violations: [], children: [] }) as unknown as GraphRuleData;
const entry = (nodeId: string, children: unknown[] = [], leftOut = 0): ExplorerEntryData =>
  ({ type: 'OoadClass', name: nodeId, node_id: nodeId, children, children_left_out: leftOut }) as unknown as ExplorerEntryData;
const rules = (...held: GraphRuleData[]) => ({ type: 'rules', name: 'rules', node_id: '', children: held });

// The practice trees the Graph app's explorer shows: each branch read later takes the place of the entry that left it
// out, and the trees answer the rules a node runs and whether an entry breaks one.
describe('the explorer trees', () => {
  const trees = new ExplorerTrees([entry('Cart', [entry('Cart.total', [rules(rule('use-typed-signatures', 'violating'), rule('verb-noun-format', 'passing'))]), entry('Cart.add', [], 2)])]);

  it('should answer the rules a node runs', () => {
    expect(trees.rulesOf('Cart.total').map((each) => each.name)).toEqual(['use-typed-signatures', 'verb-noun-format']);
  });

  it('should answer no rules for a node they do not hold', () => {
    expect(trees.rulesOf('Order')).toEqual([]);
  });

  it('should say an entry is violating when a rule it runs is broken', () => {
    expect([trees.isViolating(trees.entries[0]!.children[0]!), trees.isViolating(trees.entries[0]!)]).toEqual([true, false]);
  });

  describe('with a branch read for an entry that left its children out', () => {
    const opened = trees.withBranch(entry('Cart.add', [entry('Cart.add.line')]));

    it('should put the branch in the place of that entry', () => {
      expect(opened.entries[0]!.children[1]!.children.map((child) => child.name)).toEqual(['Cart.add.line']);
    });

    it('should leave the trees it was made from as they were', () => {
      expect(trees.entries[0]!.children[1]!.children).toEqual([]);
    });
  });
});
