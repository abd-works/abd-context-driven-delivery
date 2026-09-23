import { fireEvent, render } from '@testing-library/react';
import { story, scenario } from '../../story-test';
import { PracticeGraphTree } from '../../../packages/explore-knowledge-graph/PracticeGraphTree';
import {
  KnowledgeGraph,
  type KnowledgeGraphDto,
  type ListedTreeNode,
} from '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';
import { ExplorePracticeGraphsClientHelper } from './helpers/explore-practice-graphs.client';
import {
  KEEP_OPERATIONS_SMALL_FOCUSED,
  failingProcessEverythingOperation,
  passingLoadOperation,
} from './helpers/explore-practice-graphs.base';

const helper = new ExplorePracticeGraphsClientHelper();

story('Browse Practice Graphs', () => {
  scenario('KnowledgeGraph lists PracticeGraphs and Nodes', ({ given, when, then }) => {
    given('a KnowledgeGraph whose source includes a Node that passes keep-operations-small-focused', async () => {
      await helper.seed();
    }).and(
      'whose source includes a Node that fails keep-operations-small-focused',
      async () => {},
    );
    when('the Engineer browses the KnowledgeGraph', async () => {
      await helper.browse();
    });
    then('the passing Node lists keep-operations-small-focused as passing', () => {
      expect(helper.passingNode()?.rule_statuses[KEEP_OPERATIONS_SMALL_FOCUSED]).toBe(
        'passing',
      );
    }).and('the failing Node lists keep-operations-small-focused as violating', () => {
      expect(helper.failingNode()?.rule_statuses[KEEP_OPERATIONS_SMALL_FOCUSED]).toBe(
        'violating',
      );
    }).and('the tree keeps operations inside the domain folder', () => {
      const roots = helper.listed?.listed_tree ?? [];
      expect(roots.map((node) => node.name)).toEqual(['domain']);
      expect(roots.some((node) => node.name === 'load')).toBe(false);
    }).and('classes sit in their subfolder, not the parent module', () => {
      const harness = KnowledgeGraph.fromDto(nestedClassGraph())
        .present()
        .listed_tree.find((node) => node.name === 'harness');
      expect(harness?.children.map((node) => node.name)).toEqual(['guidance']);
      expect(descendantNames(harness)).toContain('Guidance');
    }).and('disk folders show under harness even when they are only Packages', () => {
      const harness = KnowledgeGraph.fromDto(diskSubfolderGraph())
        .present()
        .listed_tree.find((node) => node.name === 'harness');
      expect(harness?.children.map((node) => node.name)).toEqual(['guidance', 'mcp']);
      const guidance = harness?.children.find((node) => node.name === 'guidance');
      expect(guidance?.children.map((node) => node.name)).toContain('Guidance');
      expect(harness?.children.map((node) => node.name)).not.toContain('Guidance');
    }).and('children sit one indent level under their parent', () => {
      const { container } = render(
        <PracticeGraphTree
          roots={helper.listed?.listed_tree ?? []}
          selectedId={null}
          onSelect={() => undefined}
        />,
      );
      const parent = container.querySelector('li[data-depth="0"]');
      expect(parent?.querySelector('li[data-depth="1"]')).not.toBeNull();
    }).and('the Node icon tooltip names the Node type', () => {
      const { container } = render(
        <PracticeGraphTree
          roots={helper.listed?.listed_tree ?? []}
          selectedId={null}
          onSelect={() => undefined}
        />,
      );
      for (let step = 0; step < 20; step += 1) {
        const closed = container.querySelector(
          '[data-testid="tree-expand"][aria-expanded="false"]',
        );
        if (!closed) {
          break;
        }
        fireEvent.click(closed);
      }
      const root = container.querySelector('li[data-depth="0"] > .tree-row > button[title]');
      expect(root?.getAttribute('title')).toBe('Package');
      expect(
        container.querySelector(
          'button[title="Module"], button[title="File"], button[title="Operation"]',
        ),
      ).not.toBeNull();
    }).and('rules stay collapsed until the rules node is opened', () => {
      const { container } = render(
        <PracticeGraphTree
          roots={helper.listed?.listed_tree ?? []}
          selectedId={null}
          onSelect={() => undefined}
        />,
      );
      expandNonRuleTwists(container);
      expect(container.textContent ?? '').not.toContain(KEEP_OPERATIONS_SMALL_FOCUSED);
      const rulesTwist = container.querySelector('[data-testid="tree-expand-rules"]');
      expect(rulesTwist).not.toBeNull();
      fireEvent.click(rulesTwist!);
      expect(container.textContent ?? '').toContain(KEEP_OPERATIONS_SMALL_FOCUSED);
    }).and('violating subtrees mark ancestors red with failed over total', () => {
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
      expect(container.querySelector('.tree-violating .tree-counts')?.textContent).toMatch(
        /\(\d+\/\d+\)/,
      );
    });
  });
});

story('Open Node Source', () => {
  scenario('file Node opens source and highlights range', ({ given, when, then }) => {
    given('a KnowledgeGraph with a file Node that has a source file and range', async () => {
      await helper.seed();
    });
    when('the Engineer selects the file Node', async () => {
      await helper.selectNode(passingLoadOperation.node_id);
    });
    then('the source file is shown', () => {
      expect(helper.listed?.source_file?.file).toBe(passingLoadOperation.source?.file);
    }).and('the Node range is highlighted', () => {
      expect(helper.listed?.source_file?.start_line).toBe(
        passingLoadOperation.source?.start_line,
      );
    });
  });
});

story('Follow Relationship', () => {
  scenario('following a Relationship focuses the target Node', ({ given, when, then }) => {
    given('a Node with a Relationship to a target Node', async () => {
      await helper.seed();
    });
    when('the Engineer follows the Relationship', async () => {
      await helper.followRelationship(passingLoadOperation.node_id);
    });
    then('the target Node is selected', () => {
      expect(helper.listed?.selected_node?.node_id).toBe(passingLoadOperation.node_id);
    }).and('the target source file is shown when the target is a file', () => {
      expect(helper.listed?.source_file?.file).toBe('domain/customer/Customer.ts');
    });
  });
});

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
    }).and('the tree keeps ancestors of the violating Node', () => {
      const names = treeNames(helper.listed?.listed_tree ?? []);
      expect(names).toContain('processEverything');
      expect(names).not.toContain('load');
      expect(names).toContain('domain');
    }).and('rules on a violating Node list only the violating rule', () => {
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
    }).and('parents show failed over total and stay red', () => {
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
      expect(container.querySelector('.tree-violating')).not.toBeNull();
      expect(container.textContent ?? '').toMatch(/\(\d+\/\d+\)/);
    });
  });
});

story('Select Working Folder', () => {
  scenario('selecting a folder scans it into the KnowledgeGraph', ({ given, when, then }) => {
    given('a folder whose source includes a Node that passes keep-operations-small-focused', async () => {
      await helper.seed();
    }).and(
      'whose source includes a Node that fails keep-operations-small-focused',
      async () => {},
    );
    when('the Engineer selects that folder', async () => {
      await helper.selectFolder();
    });
    then('the passing Node lists keep-operations-small-focused as passing', () => {
      expect(helper.passingNode()?.rule_statuses[KEEP_OPERATIONS_SMALL_FOCUSED]).toBe(
        'passing',
      );
    }).and('the failing Node lists keep-operations-small-focused as violating', () => {
      expect(helper.failingNode()?.rule_statuses[KEEP_OPERATIONS_SMALL_FOCUSED]).toBe(
        'violating',
      );
    });
  });
});

function expandNonRuleTwists(container: HTMLElement) {
  for (let step = 0; step < 20; step += 1) {
    const closed = container.querySelector(
      '[data-testid="tree-expand"][aria-expanded="false"]',
    );
    if (!closed) {
      return;
    }
    fireEvent.click(closed);
  }
}

function treeNames(nodes: ListedTreeNode[]): string[] {
  return nodes.flatMap((node) => [node.name, ...treeNames(node.children)]);
}

function findTreeNode(
  nodes: ListedTreeNode[],
  name: string,
): ListedTreeNode | undefined {
  for (const node of nodes) {
    if (node.name === name) {
      return node;
    }
    const nested = findTreeNode(node.children, name);
    if (nested) {
      return nested;
    }
  }
  return undefined;
}

function descendantNames(node: ListedTreeNode | undefined): string[] {
  if (!node) {
    return [];
  }
  return node.children.flatMap((child) => [
    child.name,
    ...descendantNames(child),
  ]);
}

function diskSubfolderGraph(): KnowledgeGraphDto {
  return {
    id: '11111111-1111-1111-1111-111111111111',
    folder: 'workspace',
    practice_graphs: [
      {
        id: 'practice:workspace',
        name: 'workspace',
        nodes: [
          {
            node_id: 'ce:Module:harness',
            name: 'harness',
            practice: 'clean_engineering',
            semantic_type: 'Module',
            properties: { folder: 'harness' },
            applicable_rules: [],
            violations: [],
            source: null,
          },
          {
            node_id: 'pkg:harness/guidance',
            name: 'guidance',
            practice: '',
            semantic_type: 'Package',
            properties: { folder: 'harness/guidance' },
            applicable_rules: [],
            violations: [],
            source: null,
          },
          {
            node_id: 'pkg:harness/mcp',
            name: 'mcp',
            practice: '',
            semantic_type: 'Package',
            properties: { folder: 'harness/mcp' },
            applicable_rules: [],
            violations: [],
            source: null,
          },
          {
            node_id: 'ce:OoadClass:Guidance',
            name: 'Guidance',
            practice: 'clean_engineering',
            semantic_type: 'OoadClass',
            properties: {},
            applicable_rules: [],
            violations: [],
            source: {
              file: 'harness/guidance/guidance.py',
              start_line: 1,
              end_line: 10,
              text: 'class Guidance: pass',
            },
          },
        ],
        relationships: [
          {
            kind: 'owns',
            from_id: 'ce:Module:harness',
            to_id: 'ce:OoadClass:Guidance',
          },
        ],
      },
    ],
  };
}

function nestedClassGraph(): KnowledgeGraphDto {
  return {
    id: '11111111-1111-1111-1111-111111111111',
    folder: 'workspace',
    practice_graphs: [
      {
        id: 'practice:workspace',
        name: 'workspace',
        nodes: [
          {
            node_id: 'ce:Module:harness',
            name: 'harness',
            practice: 'clean_engineering',
            semantic_type: 'Module',
            properties: { folder: 'harness' },
            applicable_rules: ['honor-every-rule-in-the-artifact'],
            violations: [],
            source: null,
          },
          {
            node_id: 'ce:Module:harness/guidance',
            name: 'guidance',
            practice: 'clean_engineering',
            semantic_type: 'Module',
            properties: { folder: 'harness/guidance' },
            applicable_rules: [],
            violations: [],
            source: null,
          },
          {
            node_id: 'ce:OoadClass:harness/guidance/guidance.py:Guidance',
            name: 'Guidance',
            practice: 'clean_engineering',
            semantic_type: 'OoadClass',
            properties: {},
            applicable_rules: [],
            violations: [],
            source: {
              file: 'harness/guidance/guidance.py',
              start_line: 1,
              end_line: 10,
              text: 'class Guidance: pass',
            },
          },
        ],
        relationships: [
          {
            kind: 'owns',
            from_id: 'ce:Module:harness',
            to_id: 'ce:OoadClass:harness/guidance/guidance.py:Guidance',
          },
        ],
      },
    ],
  };
}
