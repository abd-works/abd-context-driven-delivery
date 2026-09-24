import { fireEvent } from '@testing-library/react';
import {
  KEEP_OPERATIONS_SMALL_FOCUSED,
  type KnowledgeGraphDto,
  type ListedTreeNode,
} from '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';
import { FIXTURE_WORKSPACE } from '../examples/knowledge-graph.examples';

export function expandNonRuleTwists(container: HTMLElement) {
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

export function treeNames(nodes: ListedTreeNode[]): string[] {
  return nodes.flatMap((node) => [node.name, ...treeNames(node.children)]);
}

export function findTreeNode(
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

export function descendantNames(node: ListedTreeNode | undefined): string[] {
  if (!node) {
    return [];
  }
  return node.children.flatMap((child) => [
    child.name,
    ...descendantNames(child),
  ]);
}

export function clonedNameParameterHits(): KnowledgeGraphDto {
  const clone = {
    rule_slug: 'hide-inner-details',
    message: "Operation 'name' reads private attribute '_slugify_class_name'.",
    body: '',
    practice: 'clean_engineering',
    fidelity: 'code',
  };
  const param = (id: string, file: string) => ({
    node_id: id,
    name: 'name',
    practice: 'clean_engineering',
    semantic_type: 'Parameter',
    properties: {},
    applicable_rules: ['hide-inner-details'],
    violations: [clone],
    source: { file, start_line: 1, end_line: 1, text: 'name: str' },
  });
  return {
    id: '11111111-1111-1111-1111-111111111111',
    folder: '',
    practice_graphs: [
      {
        id: 'practice:clean_engineering',
        name: 'clean_engineering',
        nodes: [
          param('param:ql', 'harness/mcp/codeql_server.py'),
          param('param:tools', 'harness/agent_tools/agent_tools.py'),
        ],
        relationships: [],
      },
    ],
  };
}

export function clonedInitHits(): KnowledgeGraphDto {
  const clone = {
    rule_slug: KEEP_OPERATIONS_SMALL_FOCUSED,
    message: "Operation 'Stories.__init__' is 23 lines (max 20).",
    body: '',
    practice: 'clean_engineering',
    fidelity: 'code',
  };
  const init = (
    id: string,
    owner: string,
    file: string,
    start: number,
    end: number,
  ) => ({
    node_id: id,
    name: '__init__',
    practice: 'clean_engineering',
    semantic_type: 'Operation',
    properties: {},
    applicable_rules: [KEEP_OPERATIONS_SMALL_FOCUSED],
    violations: [clone],
    source: { file, start_line: start, end_line: end, text: '' },
  });
  const cls = (id: string, name: string) => ({
    node_id: id,
    name,
    practice: 'clean_engineering',
    semantic_type: 'OoadClass',
    properties: {},
    applicable_rules: [],
    violations: [],
    source: null,
  });
  return {
    id: '11111111-1111-1111-1111-111111111111',
    folder: '',
    practice_graphs: [
      {
        id: 'practice:clean_engineering',
        name: 'clean_engineering',
        nodes: [
          cls('class:host', 'McpHost'),
          cls('class:stories', 'Stories'),
          init('op:host-init', 'McpHost', 'harness/mcp/mcp_server.py', 568, 572),
          init('op:stories-init', 'Stories', 'practices/stories/stories.py', 13, 35),
        ],
        relationships: [
          { kind: 'owns', from_id: 'class:host', to_id: 'op:host-init' },
          { kind: 'owns', from_id: 'class:stories', to_id: 'op:stories-init' },
        ],
      },
    ],
  };
}

export function diskSubfolderGraph(): KnowledgeGraphDto {
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

export function nestedClassGraph(): KnowledgeGraphDto {
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

export function codeQlClassWithoutSource(): KnowledgeGraphDto {
  return {
    id: '11111111-1111-1111-1111-111111111111',
    folder: FIXTURE_WORKSPACE,
    practice_graphs: [
      {
        id: 'practice:workspace',
        name: 'workspace',
        nodes: [
          {
            node_id: 'ce:Module:domain.customer',
            name: 'domain.customer',
            practice: 'clean_engineering',
            semantic_type: 'Module',
            properties: {},
            applicable_rules: [],
            violations: [],
            source: null,
          },
          {
            node_id: 'ce:OoadClass:Customer',
            name: 'Customer',
            practice: 'clean_engineering',
            semantic_type: 'OoadClass',
            properties: {},
            applicable_rules: [],
            violations: [],
            source: null,
          },
          {
            node_id: 'ce:Operation:processEverything',
            name: 'processEverything',
            practice: 'clean_engineering',
            semantic_type: 'Operation',
            properties: {},
            applicable_rules: [],
            violations: [],
            source: null,
          },
        ],
        relationships: [
          {
            kind: 'owns',
            from_id: 'ce:Module:domain.customer',
            to_id: 'ce:OoadClass:Customer',
          },
          {
            kind: 'belongsTo',
            from_id: 'ce:OoadClass:Customer',
            to_id: 'ce:Module:domain.customer',
          },
          {
            kind: 'owns',
            from_id: 'ce:OoadClass:Customer',
            to_id: 'ce:Operation:processEverything',
          },
          {
            kind: 'belongsTo',
            from_id: 'ce:Operation:processEverything',
            to_id: 'ce:OoadClass:Customer',
          },
        ],
      },
    ],
  };
}

export function violatingClassWithPassingOps(): KnowledgeGraphDto {
  const srp = {
    rule_slug: 'keep-classes-single-responsibility',
    message: '5 public operations',
    body: '',
    practice: 'clean_engineering',
    fidelity: 'code',
  };
  function operation(name: string) {
    return {
      node_id: `ce:Operation:${name}`,
      name,
      practice: 'clean_engineering',
      semantic_type: 'Operation',
      properties: {},
      applicable_rules: [KEEP_OPERATIONS_SMALL_FOCUSED],
      violations: [],
      source: null,
    };
  }
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
            node_id: 'ce:OoadClass:GraphClass',
            name: 'GraphClass',
            practice: 'clean_engineering',
            semantic_type: 'OoadClass',
            properties: {},
            applicable_rules: ['keep-classes-single-responsibility'],
            violations: [srp],
            source: null,
          },
          operation('load_property'),
          operation('load_operation'),
          operation('sync_tree_from_legacy'),
          {
            node_id: 'ce:Operation:too_long',
            name: 'too_long',
            practice: 'clean_engineering',
            semantic_type: 'Operation',
            properties: {},
            applicable_rules: [KEEP_OPERATIONS_SMALL_FOCUSED],
            violations: [
              {
                rule_slug: KEEP_OPERATIONS_SMALL_FOCUSED,
                message: 'too_long is 40 lines',
                body: '',
                practice: 'clean_engineering',
                fidelity: 'code',
              },
            ],
            source: null,
          },
          {
            node_id: 'ce:OoadClass:Other',
            name: 'Other',
            practice: 'clean_engineering',
            semantic_type: 'OoadClass',
            properties: {},
            applicable_rules: [],
            violations: [],
            source: null,
          },
          operation('load'),
        ],
        relationships: [
          {
            kind: 'owns',
            from_id: 'ce:Module:harness',
            to_id: 'ce:OoadClass:GraphClass',
          },
          {
            kind: 'owns',
            from_id: 'ce:Module:harness',
            to_id: 'ce:OoadClass:Other',
          },
          {
            kind: 'owns',
            from_id: 'ce:OoadClass:GraphClass',
            to_id: 'ce:Operation:load_property',
          },
          {
            kind: 'owns',
            from_id: 'ce:OoadClass:GraphClass',
            to_id: 'ce:Operation:load_operation',
          },
          {
            kind: 'owns',
            from_id: 'ce:OoadClass:GraphClass',
            to_id: 'ce:Operation:sync_tree_from_legacy',
          },
          {
            kind: 'owns',
            from_id: 'ce:OoadClass:GraphClass',
            to_id: 'ce:Operation:too_long',
          },
          {
            kind: 'owns',
            from_id: 'ce:OoadClass:Other',
            to_id: 'ce:Operation:load',
          },
        ],
      },
    ],
  };
}

export function fileParkingLotGraph(): KnowledgeGraphDto {
  const file = 'actions/grill_context/grill_context.py';
  return {
    id: '11111111-1111-1111-1111-111111111111',
    folder: 'workspace',
    practice_graphs: [
      {
        id: 'practice:workspace',
        name: 'workspace',
        nodes: [
          {
            node_id: 'pkg:actions',
            name: 'actions',
            practice: '',
            semantic_type: 'Package',
            properties: { folder: 'actions' },
            applicable_rules: [],
            violations: [],
            source: null,
          },
          {
            node_id: 'pkg:actions/grill_context',
            name: 'grill_context',
            practice: '',
            semantic_type: 'Package',
            properties: { folder: 'actions/grill_context' },
            applicable_rules: [],
            violations: [],
            source: null,
          },
          {
            node_id: 'ce:File:grill_context.py',
            name: file,
            practice: 'clean_engineering',
            semantic_type: 'File',
            properties: {},
            applicable_rules: [],
            violations: [],
            source: { file, start_line: 1, end_line: 40, text: '' },
          },
          {
            node_id: 'ce:OoadClass:GrillContext',
            name: 'GrillContext',
            practice: 'clean_engineering',
            semantic_type: 'OoadClass',
            properties: {},
            applicable_rules: [],
            violations: [],
            source: { file, start_line: 10, end_line: 30, text: 'class GrillContext: pass' },
          },
          {
            node_id: 'ce:Operation:ask',
            name: 'ask',
            practice: 'clean_engineering',
            semantic_type: 'Operation',
            properties: {},
            applicable_rules: [],
            violations: [],
            source: { file, start_line: 34, end_line: 38, text: 'def ask(): pass' },
          },
          {
            node_id: 'ce:Property:ROOT',
            name: 'ROOT',
            practice: 'clean_engineering',
            semantic_type: 'Property',
            properties: {},
            applicable_rules: [],
            violations: [],
            source: { file, start_line: 3, end_line: 3, text: 'ROOT = Path(__file__)' },
          },
        ],
        relationships: [
          {
            kind: 'owns',
            from_id: 'pkg:actions/grill_context',
            to_id: 'ce:File:grill_context.py',
          },
          {
            kind: 'owns',
            from_id: 'ce:File:grill_context.py',
            to_id: 'ce:OoadClass:GrillContext',
          },
          {
            kind: 'owns',
            from_id: 'ce:File:grill_context.py',
            to_id: 'ce:Operation:ask',
          },
          {
            kind: 'owns',
            from_id: 'ce:File:grill_context.py',
            to_id: 'ce:Property:ROOT',
          },
        ],
      },
    ],
  };
}

export function classDemonstratedThroughExampleGraph(): KnowledgeGraphDto {
  return {
    id: '11111111-1111-1111-1111-111111111111',
    folder: 'workspace',
    practice_graphs: [
      {
        id: 'practice:clean_engineering',
        name: 'clean_engineering',
        nodes: [
          {
            node_id: 'ce:OoadClass:Customer',
            name: 'Customer',
            practice: 'clean_engineering',
            semantic_type: 'OoadClass',
            properties: { folder: 'domain/customer' },
            applicable_rules: [],
            violations: [],
            source: {
              file: 'domain/customer/Customer.ts',
              start_line: 1,
              end_line: 20,
              text: 'export class Customer {}',
            },
          },
        ],
        relationships: [],
      },
      {
        id: 'practice:stories',
        name: 'stories',
        nodes: [
          {
            node_id: 'st:Example:adder',
            name: 'adder',
            practice: 'stories',
            semantic_type: 'Example',
            properties: {},
            applicable_rules: [],
            violations: [],
            source: {
              file: 'practices/stories/catalog-examples/adder.ts',
              start_line: 1,
              end_line: 8,
              text: 'export const adder = { left: 1, right: 2 };',
            },
          },
        ],
        relationships: [
          {
            kind: 'demonstrates',
            from_id: 'st:Example:adder',
            to_id: 'ce:OoadClass:Customer',
          },
        ],
      },
    ],
  };
}
