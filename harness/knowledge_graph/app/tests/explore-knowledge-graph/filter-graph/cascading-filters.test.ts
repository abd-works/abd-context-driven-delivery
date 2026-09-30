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
    expect(options.node_types.sort()).toEqual(['Epic', 'Story']);
    expect(options.relationship_types).toEqual(['owns']);
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
    expect(options.relationship_types).toEqual(['owns']);
    expect(options.node_types.sort()).toEqual(['Epic', 'Story']);
  });
});
