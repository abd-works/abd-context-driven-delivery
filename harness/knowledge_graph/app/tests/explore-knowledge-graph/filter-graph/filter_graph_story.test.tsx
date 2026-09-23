import { fireEvent, render } from '@testing-library/react';
import { vi } from 'vitest';
import { story, scenario } from '../../story-test';
import { PracticeGraphTree } from '../../../packages/explore-knowledge-graph/PracticeGraphTree';
import { KnowledgeGraph } from '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';
import { overlayWorkspaceTree } from '../../../packages/explore-knowledge-graph/knowledge-graph/workspace-overlay';
import { SelectedNodePane } from '../../../packages/explore-knowledge-graph/SelectedNodePane';
import { ExplorePracticeGraphsClientHelper } from '../helpers/explore-practice-graphs.client';
import {
  KEEP_OPERATIONS_SMALL_FOCUSED,
  failingProcessEverythingOperation,
  passingLoadOperation,
} from '../helpers/explore-practice-graphs.base';
import {
  expandNonRuleTwists,
  treeNames,
  findTreeNode,
  descendantNames,
  clonedNameParameterHits,
  clonedInitHits,
  diskSubfolderGraph,
  nestedClassGraph,
  codeQlClassWithoutSource,
  violatingClassWithPassingOps,
} from '../helpers/story-graphs';

const helper = new ExplorePracticeGraphsClientHelper();

story('Filter Graph', () => {
  scenario('tree lists only Nodes that match the filters', ({ given, when, then }) => {
    given('a KnowledgeGraph whose source includes a Node that passes keep-operations-small-focused', async () => {
      await helper.seed();
    }).and(
      'whose source includes a Node that fails keep-operations-small-focused',
      async () => {},
    );
    when('the Engineer filters the KnowledgeGraph using violations', async () => {
      await helper.filterGraph();
    }).and('using keep-operations-small-focused', async () => {});
    then('the failing Node is listed', () => {
      expect(helper.failingNode()?.node_id).toBe(
        failingProcessEverythingOperation.node_id,
      );
    }).and('the passing Node is not listed', () => {
      expect(helper.passingNode()).toBeUndefined();
    });
  });
  scenario('keep ancestors of a violating Node', ({ given, when, then }) => {
    given('the same KnowledgeGraph', async () => {
      await helper.seed();
    });
    when('the Engineer filters using violations', async () => {
      await helper.filterGraph();
    });
    then('ancestors of the failing Node remain', () => {
      const names = treeNames(helper.listed?.listed_tree ?? []);
      expect(names).toContain('processEverything');
      expect(names).toContain('domain');
    }).and('passing siblings drop out', () => {
      expect(treeNames(helper.listed?.listed_tree ?? [])).not.toContain('load');
    });
  });
  scenario('opening rules lists only the violating rule', ({ given, when, then }) => {
    given('a violating Node with more than one applicable rule', async () => {
      await helper.seed();
    });
    when('the Engineer filters using violations', async () => {
      await helper.filterGraph();
    });
    then('the Node rules list only the violating rule', () => {
      const failing = findTreeNode(
        helper.listed?.listed_tree ?? [],
        'processEverything',
      );
      expect(failing?.rules.map((rule) => rule.slug)).toEqual([
        KEEP_OPERATIONS_SMALL_FOCUSED,
      ]);
      expect(failing?.rules.every((rule) => rule.status === 'violating')).toBe(
        true,
      );
      const { container } = render(
        <PracticeGraphTree
          roots={helper.listed?.listed_tree ?? []}
          selectedId={null}
          onSelect={() => undefined}
        />,
      );
      expandNonRuleTwists(container);
      for (let step = 0; step < 20; step += 1) {
        const closed = container.querySelector(
          '[data-testid="tree-expand-rules"][aria-expanded="false"]',
        );
        if (!closed) {
          break;
        }
        fireEvent.click(closed);
      }
      expect(container.querySelector('.rule-status.passing')).toBeNull();
      expect(container.querySelectorAll('.rule-status.violating').length).toBeGreaterThan(
        0,
      );
    }).and('the right pane lists only violating rules', async () => {
      await helper.selectNode(failingProcessEverythingOperation.node_id);
      const rules = helper.listed?.selected_node?.rules ?? [];
      expect(rules.length).toBeGreaterThan(0);
      expect(rules.every((rule) => rule.status === 'violating')).toBe(true);
      expect(rules.some((rule) => rule.status === 'passing')).toBe(false);
    });
  });
  scenario('parents show failed over total and stay red', ({ given, when, then }) => {
    given('a violating Node under a parent', async () => {
      await helper.seed();
    });
    when('the Engineer filters using violations', async () => {
      await helper.filterGraph();
    });
    then('the failing Node and its parents are red', () => {
      const { container } = render(
        <PracticeGraphTree
          roots={helper.listed?.listed_tree ?? []}
          selectedId={null}
          onSelect={() => undefined}
        />,
      );
      expect(container.querySelector('.tree-violating')).not.toBeNull();
    }).and('(failed / total) sits beside the name', () => {
      const domain = helper.listed?.listed_tree[0];
      expect(domain?.failed).toBeGreaterThan(0);
      expect(domain?.total).toBeGreaterThanOrEqual(domain?.failed ?? 0);
      const { container } = render(
        <PracticeGraphTree
          roots={helper.listed?.listed_tree ?? []}
          selectedId={null}
          onSelect={() => undefined}
        />,
      );
      expect(container.textContent ?? '').toMatch(/\(\d+\/\d+\)/);
    });
  });
  scenario('a folder pane lists nested violating Nodes', ({ given, when, then }) => {
    given('a violating Node under a parent folder', async () => {
      await helper.seed();
    });
    when('the Engineer filters using violations', async () => {
      await helper.filterGraph();
    });
    then('selecting the folder lists the violating operations underneath', async () => {
      const folder = helper.listed?.listed_tree[0];
      expect(folder).toBeTruthy();
      await helper.selectNode(folder!.node_id);
      const names = treeNames(helper.listed?.selected_tree ? [helper.listed.selected_tree] : []);
      expect(names).toContain('processEverything');
      expect(
        helper.listed?.selected_tree?.rules.every((rule) => rule.status === 'violating') ?? true,
      ).toBe(true);
    });
  });
  scenario('a violating class lists only violating operations', ({ given, when, then }) => {
    given('a class that fails keep-classes-single-responsibility with mixed operations', () => {});
    when('the Engineer filters using violations', () => {});
    then('only operations with violations sit underneath the class', () => {
      const presented = KnowledgeGraph.fromDto(violatingClassWithPassingOps())
        .filterGraph({ violations: true })
        .present();
      const cls = findTreeNode(presented.listed_tree, 'GraphClass');
      expect(cls).toBeTruthy();
      const childNames = cls!.children.map((child) => child.name);
      expect(childNames).toContain('too_long');
      expect(childNames).not.toContain('load_property');
      expect(childNames).not.toContain('load_operation');
      expect(childNames).not.toContain('sync_tree_from_legacy');
      expect(treeNames(presented.listed_tree)).not.toContain('load');
    });
  });
  scenario('copy info to prompt copies node and violation for chat', ({ given, when, then }) => {
    given('a violating operation is open in the source pane', () => {});
    when('the Engineer copies info to prompt', () => {});
    then('the clipboard holds node, rule, and violation text', async () => {
      const writeText = vi.fn().mockResolvedValue(undefined);
      Object.assign(navigator, { clipboard: { writeText } });
      const presented = KnowledgeGraph.fromDto(violatingClassWithPassingOps())
        .selectNode('ce:Operation:too_long')
        .present();
      const { getByTestId } = render(
        <SelectedNodePane
          selectedNode={presented.selected_node}
          selectedTree={presented.selected_tree}
          selectedRule={null}
          sourceFile={presented.source_file}
        />,
      );
      fireEvent.click(getByTestId('copy-info-to-prompt'));
      expect(writeText).toHaveBeenCalled();
      const copied = String(writeText.mock.calls[0][0]);
      expect(copied).toContain('harness.GraphClass.too_long');
      expect(copied).toContain(KEEP_OPERATIONS_SMALL_FOCUSED);
      expect(copied).toContain('too_long is 40 lines');
    });
  });
});
