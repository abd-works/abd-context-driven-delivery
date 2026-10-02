import { RELATIONSHIP_KINDS } from '../../../packages/explore-knowledge-graph/knowledge-graph/catalog';
import { KnowledgeGraph } from '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';

function node(id: string, name: string, practice: string, semanticType: string) {
  return {
    node_id: id,
    name,
    practice,
    semantic_type: semanticType,
    properties: {},
    applicable_rules: [],
    violations: [],
    source: null,
  };
}

describe('cascading filters', () => {
  const graph = KnowledgeGraph.fromDto({
    id: '11111111-1111-4111-8111-111111111111',
    folder: 'workspace',
    practice_graphs: [
      {
        id: 'practice:stories',
        name: 'stories',
        nodes: [
          node('epic', 'Onboard', 'stories', 'Epic'),
          node('story', 'Create customer', 'stories', 'Story'),
        ],
        relationships: [{ kind: 'owns', from_id: 'epic', to_id: 'story' }],
      },
      {
        id: 'practice:ce',
        name: 'clean_engineering',
        nodes: [node('class', 'Customer', 'clean_engineering', 'OoadClass')],
        relationships: [{ kind: 'invokes', from_id: 'class', to_id: 'class' }],
      },
    ],
  });

  it('keeps node types and relationships to the selected practice', () => {
    const options = graph.filterGraph({ practices: ['stories'] }).present().filter_options;
    expect(options.node_types).toEqual(
      expect.arrayContaining(['Epic', 'Story', 'Scenario', 'Step', 'Example']),
    );
    expect(options.node_types).not.toContain('OoadClass');
    expect(options.relationship_types).toEqual([...RELATIONSHIP_KINDS]);
    expect(options.stages).toEqual(['discovery', 'specification', 'implementation']);
  });

  it('lists the DDD building blocks when only that practice is selected', () => {
    const options = graph.filterGraph({ practices: ['ddd'] }).present().filter_options;
    expect(options.node_types).toEqual(
      expect.arrayContaining([
        'BoundedContext',
        'Aggregate',
        'Entity',
        'EntityRoot',
        'ValueObject',
        'Repository',
        'DomainEvent',
        'DomainService',
        'Specification',
      ]),
    );
  });

  it('keeps relationships to the selected node type', () => {
    const options = graph
      .filterGraph({ practices: ['stories'], nodeTypes: ['Epic'] })
      .present().filter_options;
    expect(options.relationship_types).toEqual([...RELATIONSHIP_KINDS]);
    expect(options.node_types).toEqual(
      expect.arrayContaining(['Epic', 'Story', 'Scenario', 'Step']),
    );
  });
});

describe('practice filter keeps each model’s own links', () => {
  const graph = KnowledgeGraph.fromDto({
    id: '22222222-2222-4222-8222-222222222222',
    folder: 'workspace',
    practice_graphs: [
      {
        id: 'practice:stories',
        name: 'stories',
        nodes: [
          node('epic', 'Onboard', 'stories', 'Epic'),
          node('step', 'When the customer confirms', 'stories', 'Step'),
        ],
        relationships: [
          { kind: 'owns', from_id: 'epic', to_id: 'step' },
          { kind: 'invokes', from_id: 'step', to_id: 'load' },
          { kind: 'invokes', from_id: 'step', to_id: 'class' },
        ],
      },
      {
        id: 'practice:ce',
        name: 'clean_engineering',
        nodes: [
          node('class', 'Customer', 'clean_engineering', 'OoadClass'),
          node('load', 'load', 'clean_engineering', 'Operation'),
          node('save', 'save', 'clean_engineering', 'Operation'),
        ],
        relationships: [
          { kind: 'owns', from_id: 'class', to_id: 'load' },
          { kind: 'owns', from_id: 'class', to_id: 'save' },
          { kind: 'invokes', from_id: 'class', to_id: 'load' },
          { kind: 'invokes', from_id: 'load', to_id: 'save' },
        ],
      },
      {
        id: 'practice:ddd',
        name: 'ddd',
        nodes: [
          node('context', 'Customer', 'ddd', 'BoundedContext'),
          node('cart', 'Cart', 'ddd', 'Aggregate'),
        ],
        relationships: [
          { kind: 'owns', from_id: 'context', to_id: 'cart' },
          { kind: 'invokes', from_id: 'cart', to_id: 'class' },
        ],
      },
      {
        id: 'practice:bdd',
        name: 'bdd',
        nodes: [node('spec', 'Confirm identity', 'bdd', 'Description')],
        relationships: [{ kind: 'invokes', from_id: 'spec', to_id: 'load' }],
      },
    ],
  });

  function findNode(nodes: { node_id: string; children?: { node_id: string; children?: never[] }[] }[], id: string): { relationships: { kind: string; targets: { practice: string; semantic_type: string }[] }[] } | null {
    for (const entry of nodes) {
      if (entry.node_id === id) {
        return entry as { relationships: { kind: string; targets: { practice: string; semantic_type: string }[] }[] };
      }
      const nested = findNode(entry.children ?? [], id);
      if (nested) {
        return nested;
      }
    }
    return null;
  }

  it('omits invokes on a class when only the class model is selected', () => {
    const tree = graph.filterGraph({ practices: ['clean_engineering'] }).present().listed_tree;
    const customer = findNode(tree, 'class');
    const load = findNode(tree, 'load');
    expect(customer?.relationships.some((group) => group.kind === 'invokes')).toBe(false);
    expect(
      load?.relationships.flatMap((group) => group.targets).some((target) => target.semantic_type === 'Step'),
    ).toBe(false);
    expect(
      load?.relationships.some(
        (group) => group.kind === 'invokes' && group.targets.some((target) => target.name === undefined || target.semantic_type === 'Operation'),
      ),
    ).toBe(true);
  });

  it('omits invoked classes and operations when only stories are selected', () => {
    const tree = graph.filterGraph({ practices: ['stories'] }).present().listed_tree;
    const step = findNode(tree, 'step');
    const targets = step?.relationships.flatMap((group) => group.targets) ?? [];
    expect(targets.some((target) => target.semantic_type === 'OoadClass' || target.semantic_type === 'Operation')).toBe(false);
  });

  it('omits class-model targets when only DDD or BDD is selected', () => {
    const ddd = findNode(
      graph.filterGraph({ practices: ['ddd'] }).present().listed_tree,
      'cart',
    );
    const bdd = findNode(
      graph.filterGraph({ practices: ['bdd'] }).present().listed_tree,
      'spec',
    );
    expect(ddd?.relationships.flatMap((group) => group.targets).some((target) => target.practice === 'clean_engineering')).toBe(false);
    expect(bdd?.relationships.flatMap((group) => group.targets).some((target) => target.practice === 'clean_engineering')).toBe(false);
  });
});
