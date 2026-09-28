import { KnowledgeGraph } from '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';

describe('rule source filter', () => {
  it('lists only the project rule when ruleSources is project', () => {
    const graph = KnowledgeGraph.fromDto({
      id: '11111111-1111-4111-8111-111111111111',
      folder: 'workspace',
      practice_graphs: [
        {
          id: 'practice:stories',
          name: 'stories',
          nodes: [
            {
              node_id: 'story:load',
              name: 'Load customer',
              practice: 'stories',
              semantic_type: 'Story',
              properties: {},
              applicable_rules: ['shared-rule'],
              rule_catalog: [
                { slug: 'shared-rule', tag: 'base' },
                { slug: 'shared-rule', tag: 'project' },
              ],
              rule_tags: { 'shared-rule': 'project' },
              violations: [
                {
                  rule_slug: 'shared-rule',
                  message: 'base hit',
                  practice: 'stories',
                  fidelity: 'story_map',
                  tag: 'base',
                },
                {
                  rule_slug: 'shared-rule',
                  message: 'project hit',
                  practice: 'stories',
                  fidelity: 'story_map',
                  tag: 'project',
                },
              ],
              source: null,
            },
          ],
          relationships: [],
        },
      ],
    });

    const listed = graph
      .selectNode('story:load')
      .filterGraph({ ruleSources: ['project'] })
      .present();
    const rules = listed.selected_node?.rules ?? [];

    expect(rules.map((rule) => rule.tag)).toEqual(['project']);
    expect(rules.map((rule) => rule.slug)).toEqual(['shared-rule']);
    expect(listed.filter_options.rule_sources).toEqual(['base', 'project']);
  });
});
