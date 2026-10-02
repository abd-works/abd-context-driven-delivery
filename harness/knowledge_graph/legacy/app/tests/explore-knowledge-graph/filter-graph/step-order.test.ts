import { KnowledgeGraph, stepTitle } from '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';

function node(
  id: string,
  name: string,
  semanticType: string,
  extra: {
    sequential_order?: number;
    keyword?: string;
    practice?: string;
    properties?: Record<string, string>;
    source?: { file: string; start_line: number; end_line: number; text: string } | null;
  } = {},
) {
  return {
    node_id: id,
    name,
    practice: 'stories',
    semantic_type: semanticType,
    properties: {},
    applicable_rules: [],
    violations: [],
    source: null,
    ...extra,
  };
}

describe('scenario step order', () => {
  it('lists steps in scenario order with Given, When, or Then', () => {
    const graph = KnowledgeGraph.fromDto({
      id: '11111111-1111-4111-8111-111111111111',
      folder: 'workspace',
      practice_graphs: [
        {
          id: 'practice:stories',
          name: 'stories',
          nodes: [
            node('epic', 'Onboard', 'Epic'),
            node('story', 'Create customer', 'Story'),
            node('scenario', 'customer signs up', 'Scenario'),
            node('then', 'the customer exists', 'Step', { sequential_order: 3, keyword: 'Then' }),
            node('and', 'the cart is stored', 'Step', { sequential_order: 4, keyword: 'And' }),
            node('given', 'a plan is selected', 'Step', { sequential_order: 1, keyword: 'Given' }),
            node('when', 'the customer submits', 'Step', { sequential_order: 2, keyword: 'When' }),
          ],
          relationships: [
            { kind: 'owns', from_id: 'epic', to_id: 'story' },
            { kind: 'owns', from_id: 'story', to_id: 'scenario' },
            { kind: 'owns', from_id: 'scenario', to_id: 'then' },
            { kind: 'owns', from_id: 'scenario', to_id: 'and' },
            { kind: 'owns', from_id: 'scenario', to_id: 'given' },
            { kind: 'owns', from_id: 'scenario', to_id: 'when' },
          ],
        },
      ],
    });
    const tree = graph.filterGraph({ practices: ['stories'] }).present().listed_tree;
    const scenario = tree[0]?.children[0]?.children[0]?.children[0];
    expect(scenario?.name).toBe('customer signs up');
    expect(
      stepTitle(
        'the customer exists',
        'Step',
        '',
        "      then('the customer exists', () => {\n",
      ),
    ).toBe('Then the customer exists');
    expect(scenario?.children.map((step) => step.name)).toEqual([
      'Given a plan is selected',
      'When the customer submits',
      'Then the customer exists',
      'And the cart is stored',
    ]);
  });

  it('folds a background Given and its And lines into the background node', () => {
    const source = (text: string, start: number, end: number) => ({
      file: 'story.spec.ts',
      start_line: start,
      end_line: end,
      text,
    });
    const graph = KnowledgeGraph.fromDto({
      id: '22222222-2222-4222-8222-222222222222',
      folder: 'workspace',
      practice_graphs: [
        {
          id: 'practice:stories',
          name: 'stories',
          nodes: [
            node('epic', 'Onboard', 'Epic'),
            node('story', 'Create customer', 'Story'),
            node('bg', 'each', 'Background'),
            node('given', 'a token exists', 'Step', {
              source: source("    given('a token exists', () => {\n    });", 2, 4),
            }),
            node('and', 'the cart is empty', 'Step', {
              source: source("    .and('the cart is empty', () => {\n    });", 5, 7),
            }),
            node('scenario', 'signs up', 'Scenario'),
          ],
          relationships: [
            { kind: 'owns', from_id: 'epic', to_id: 'story' },
            { kind: 'owns', from_id: 'story', to_id: 'bg' },
            { kind: 'owns', from_id: 'story', to_id: 'scenario' },
            { kind: 'owns', from_id: 'bg', to_id: 'given' },
            { kind: 'owns', from_id: 'bg', to_id: 'and' },
          ],
        },
      ],
    });
    const story = graph
      .filterGraph({ practices: ['stories'] })
      .present()
      .listed_tree[0]?.children[0]?.children[0];
    const background = story?.children.find((child) => child.semantic_type === 'Background');
    expect(background?.name).toBe('Given a token exists');
    expect(background?.children.map((child) => child.semantic_type)).toEqual([]);
    expect(background?.source?.text).toContain(".and('the cart is empty'");
    expect(story?.children.some((child) => child.name === 'signs up')).toBe(true);
  });

  it('lists an example under the Given, not under the story', () => {
    const graph = KnowledgeGraph.fromDto({
      id: '44444444-4444-4444-8444-444444444444',
      folder: 'workspace',
      practice_graphs: [
        {
          id: 'practice:stories',
          name: 'stories',
          nodes: [
            node('epic', 'Onboard', 'Epic'),
            node('story', 'Create Customer', 'Story'),
            node('bg', 'each', 'Background', {
              source: {
                file: 'story.spec.ts',
                start_line: 2,
                end_line: 4,
                text: "    given('a verified account', () => {\n    });",
              },
            }),
            node('example', 'enteredValidAccountCredentials', 'Example'),
          ],
          relationships: [
            { kind: 'owns', from_id: 'epic', to_id: 'story' },
            { kind: 'owns', from_id: 'story', to_id: 'bg' },
            { kind: 'demonstratedThrough', from_id: 'story', to_id: 'example' },
            { kind: 'demonstratedThrough', from_id: 'bg', to_id: 'example' },
          ],
        },
      ],
    });
    const story = graph
      .filterGraph({ practices: ['stories'] })
      .present()
      .listed_tree[0]?.children[0]?.children[0];
    const given = story?.children.find((child) => child.semantic_type === 'Background');
    expect(story?.children.map((child) => child.name)).not.toContain('enteredValidAccountCredentials');
    expect(given?.children.map((child) => child.name)).toEqual(['enteredValidAccountCredentials']);
  });

  it('lists a scenario in the order the steps appear in the file', () => {
    const line = (start: number, keyword: string, text: string) => ({
      file: 'create_customer_story.spec.ts',
      start_line: start,
      end_line: start,
      text: `    ${keyword}('${text}', () => {});`,
    });
    const graph = KnowledgeGraph.fromDto({
      id: '33333333-3333-4333-8333-333333333333',
      folder: 'workspace',
      practice_graphs: [
        {
          id: 'practice:stories',
          name: 'stories',
          nodes: [
            node('epic', 'Onboard', 'Epic'),
            node('story', 'Create Customer', 'Story'),
            node('scenario', 'Create customer', 'Scenario'),
            node('and', 'My Paradise stores the customer id on the Cognito user', 'Step', {
              source: line(76, '.and', 'My Paradise stores the customer id on the Cognito user'),
            }),
            node('then-id', 'the customer has a Mavenir customer id', 'Step', {
              source: line(72, 'then', 'the customer has a Mavenir customer id'),
            }),
            node('when-create', 'the User creates their Paradise account', 'Step', {
              source: line(63, 'when', 'the User creates their Paradise account'),
            }),
            node('then-send', 'My Paradise sends the correct create request to Mavenir', 'Step', {
              source: line(66, 'then', 'My Paradise sends the correct create request to Mavenir'),
            }),
            node('when-mavenir', 'Mavenir creates the customer', 'Step', {
              source: line(69, 'when', 'Mavenir creates the customer'),
            }),
          ],
          relationships: [
            { kind: 'owns', from_id: 'epic', to_id: 'story' },
            { kind: 'owns', from_id: 'story', to_id: 'scenario' },
            { kind: 'owns', from_id: 'scenario', to_id: 'and' },
            { kind: 'owns', from_id: 'scenario', to_id: 'then-id' },
            { kind: 'owns', from_id: 'scenario', to_id: 'when-create' },
            { kind: 'owns', from_id: 'scenario', to_id: 'then-send' },
            { kind: 'owns', from_id: 'scenario', to_id: 'when-mavenir' },
          ],
        },
      ],
    });
    const scenario = graph
      .filterGraph({ practices: ['stories'] })
      .present()
      .listed_tree[0]?.children[0]?.children[0]?.children.find(
        (child) => child.name === 'Create customer',
      );
    expect(scenario?.children.map((step) => step.name)).toEqual([
      'When the User creates their Paradise account',
      'Then My Paradise sends the correct create request to Mavenir',
      'When Mavenir creates the customer',
      'Then the customer has a Mavenir customer id',
      'And My Paradise stores the customer id on the Cognito user',
    ]);
  });
});
