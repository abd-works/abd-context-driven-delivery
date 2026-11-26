import { useState } from 'react';
import type { Held } from './held';
import type { NodeSourceData } from '@cdd/harness/graph/graph';
import { reasonOf } from '@cdd/cdd-page-failures';
import { failures, graphs } from '../graph/graph-page';
import type { ExplorerTrees } from '../graph/explorer-trees';
import { ruleHits, selectionForRule, type GraphSelection, type ViolationFocus } from '../graph/graph-selection';
import type { SourceRule } from '../source/SourceView';

interface SourcePaneState {
  selectedId: Held<string>;
  activeRule: Held<string>;
  violation: Held<ViolationFocus | null>;
  source: Held<NodeSourceData | null>;
  // Why the source pane shows no source for the selected node: the graph holds none, or reading it failed.
  note: Held<string>;
}

// The node a person chose in the tree, the rule and violation they chose on it, and its source.
export class SourcePane {
  constructor(private readonly state: SourcePaneState) {}

  get selectedId(): string {
    return this.state.selectedId[0];
  }

  get activeRule(): string {
    return this.state.activeRule[0];
  }

  get violation(): ViolationFocus | null {
    return this.state.violation[0];
  }

  get source(): NodeSourceData | null {
    return this.state.source[0];
  }

  get note(): string {
    return this.state.note[0];
  }

  async choose(selection: GraphSelection): Promise<void> {
    this.state.selectedId[1](selection.nodeId);
    this.state.activeRule[1](selection.rule ?? '');
    this.state.violation[1](selection.violation ?? null);
    this.state.note[1]('');
    try {
      const opened = await graphs.source(selection.nodeId);
      const shown = opened?.text != null && opened.file != null ? opened : null;
      this.state.source[1](shown);
      if (!shown) this.state.note[1]('The graph holds no source for this node. Load the folder again if it should.');
    } catch (cause) {
      this.state.source[1](null);
      this.state.note[1](`The source did not open: ${reasonOf(cause)}`);
      failures.fail(reasonOf(cause), `Opening the source of ${selection.nodeId} in the Graph app`);
    }
  }

  // The rules the selected node in trees runs, as the source pane lists them.
  rulesIn(trees: ExplorerTrees): SourceRule[] {
    return trees.rulesOf(this.selectedId).map((rule) => ({
      name: rule.name,
      status: rule.status,
      messages: ruleHits(rule).map((hit) => hit.message).filter(Boolean),
    }));
  }

  // Choose the rule called name on the selected node in trees.
  chooseRule(trees: ExplorerTrees, name: string): void {
    const rule = trees.rulesOf(this.selectedId).find((child) => child.name === name);
    if (rule) void this.choose(selectionForRule(this.selectedId, rule));
  }
}

export function useSourcePane(): SourcePane {
  return new SourcePane({
    selectedId: useState(''),
    activeRule: useState(''),
    violation: useState<ViolationFocus | null>(null),
    source: useState<NodeSourceData | null>(null),
    note: useState(''),
  });
}
