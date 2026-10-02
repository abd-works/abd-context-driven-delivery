import { describe, expect, it } from 'vitest';
import { KnowledgeGraph } from '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';

function moduleOnly() {
  return KnowledgeGraph.fromDto({
    id: '33333333-3333-4333-8333-333333333333',
    folder: 'workspace',
    practice_graphs: [
      {
        id: 'practice:clean_engineering',
        name: 'clean_engineering',
        nodes: [
          {
            node_id: 'apps',
            name: 'apps',
            practice: 'clean_engineering',
            semantic_type: 'Module',
            properties: { folder: 'apps' },
            applicable_rules: [],
            violations: [],
            source: null,
          },
        ],
        relationships: [],
      },
    ],
  });
}

describe('practice node types stay on the filter when the graph is modules', () => {
  it('lists class, story, and DDD types with no practice selected', () => {
    const options = moduleOnly().present().filter_options;
    expect(options.node_types).toEqual(
      expect.arrayContaining([
        'Module',
        'OoadClass',
        'Operation',
        'Epic',
        'Story',
        'BoundedContext',
        'Aggregate',
      ]),
    );
  });

  it('keeps class types when only clean engineering is selected', () => {
    const options = moduleOnly()
      .filterGraph({ practices: ['clean_engineering'] })
      .present().filter_options;
    expect(options.node_types).toEqual(
      expect.arrayContaining(['Module', 'OoadClass', 'Operation']),
    );
    expect(options.node_types).not.toContain('Epic');
  });
});
