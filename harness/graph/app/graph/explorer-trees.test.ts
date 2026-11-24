import { describe, expect, it } from 'vitest';

import type { ExplorerEntryData, GraphRuleData } from '@cdd/harness/graph/graph';

import { ExplorerTrees, labelOf } from './explorer-trees';

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

  // A rule that requires a judge lists candidates: places to read, which nothing has decided are wrong.
  describe('with an entry whose rule that requires a judge listed it as a candidate', () => {
    const listed = new ExplorerTrees([entry('Press The Mark', [rules(rule('when-names-intent-not-interface-gesture', 'candidate'))])]);

    it('should say the entry holds a candidate', () => {
      expect(listed.hasCandidate(listed.entries[0]!)).toBe(true);
    });

    it('should not say the entry is violating', () => {
      expect(listed.isViolating(listed.entries[0]!)).toBe(false);
    });

    it('should say an entry whose rule is broken holds no candidate', () => {
      expect(trees.hasCandidate(trees.entries[0]!.children[0]!)).toBe(false);
    });
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

// What a row of the tree shows: the label Python gives an entry, which tells it apart from those beside it, and the
// name of a rules collection or a rule, which carry no label.
describe('the label of a tree item', () => {
  it('should be the label the graph gives an entry', () => {
    expect(labelOf({ ...entry('ordering/order.py:Order'), name: 'Order', label: 'Order (order.py)' } as ExplorerEntryData)).toBe('Order (order.py)');
  });

  it('should be the name of a rule', () => {
    expect(labelOf(rule('verb-noun-format', 'passing'))).toBe('verb-noun-format');
  });
});
