import { fireEvent, render } from '@testing-library/react';
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
  classDemonstratedThroughExampleGraph,
} from '../helpers/story-graphs';

function customerRow(container: HTMLElement) {
  const name = [...container.querySelectorAll('.tree-name')].find(
    (node) => node.textContent === 'Customer',
  );
  return name?.closest('li') as HTMLElement;
}

const helper = new ExplorePracticeGraphsClientHelper();

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

  scenario('a Class does not list the Example that demonstrates it', ({ given, when, then }) => {
    given('a Class Node demonstrated by a stories Example', () => {});
    when('the Engineer opens that Class', () => {});
    then('the Example is not a relationship on the Class', () => {
      const tree = KnowledgeGraph.fromDto(
        classDemonstratedThroughExampleGraph(),
      ).present().listed_tree;
      const { container } = render(
        <PracticeGraphTree
          roots={tree}
          selectedId={null}
          onSelect={() => undefined}
        />,
      );
      expandNonRuleTwists(container);
      const row = customerRow(container);
      expect(row.textContent ?? '').not.toContain('demonstratedThrough');
      expect(row.textContent ?? '').not.toContain('adder');
      expect(row.querySelector('[data-practice]')).toBeNull();
    });
  });

  scenario('a demonstrated Class opens as a normal Node', ({ given, when, then }) => {
    given('an Example that demonstrates a Class with a property', () => {});
    when('the Engineer expands demonstrates', () => {});
    then('the Class lists its property and its properties', () => {
      const tree = KnowledgeGraph.fromDto({
        id: '55555555-5555-4555-8555-555555555555',
        folder: 'workspace',
        practice_graphs: [
          {
            id: 'practice:stories',
            name: 'stories',
            nodes: [
              {
                node_id: 'epic',
                name: 'Onboard',
                practice: 'stories',
                semantic_type: 'Epic',
                properties: {},
                applicable_rules: [],
                violations: [],
                source: null,
              },
              {
                node_id: 'story',
                name: 'Create Customer',
                practice: 'stories',
                semantic_type: 'Story',
                properties: {},
                applicable_rules: [],
                violations: [],
                source: null,
              },
              {
                node_id: 'bg',
                name: 'each',
                practice: 'stories',
                semantic_type: 'Background',
                properties: {},
                applicable_rules: [],
                violations: [],
                source: {
                  file: 'story.spec.ts',
                  start_line: 2,
                  end_line: 4,
                  text: "    given('a verified account', () => {\n    });",
                },
              },
              {
                node_id: 'example',
                name: 'enteredValidAccountCredentials',
                practice: 'stories',
                semantic_type: 'Example',
                properties: {},
                applicable_rules: [],
                violations: [],
                source: null,
              },
            ],
            relationships: [
              { kind: 'owns', from_id: 'epic', to_id: 'story' },
              { kind: 'owns', from_id: 'story', to_id: 'bg' },
              { kind: 'owns', from_id: 'bg', to_id: 'example' },
              { kind: 'demonstrates', from_id: 'example', to_id: 'class' },
            ],
          },
          {
            id: 'practice:clean_engineering',
            name: 'clean_engineering',
            nodes: [
              {
                node_id: 'class',
                name: 'AccountCredentials',
                practice: 'clean_engineering',
                semantic_type: 'OoadClass',
                properties: { folder: 'domain/customer' },
                applicable_rules: [],
                violations: [],
                source: null,
              },
              {
                node_id: 'email',
                name: 'email',
                practice: 'clean_engineering',
                semantic_type: 'Property',
                properties: {},
                applicable_rules: [],
                violations: [],
                source: null,
              },
            ],
            relationships: [{ kind: 'owns', from_id: 'class', to_id: 'email' }],
          },
        ],
      })
        .filterGraph({ practices: ['stories', 'clean_engineering'] })
        .present().listed_tree;
      const { container } = render(
        <PracticeGraphTree roots={tree} selectedId={null} onSelect={() => undefined} />,
      );
      expandNonRuleTwists(container);
      const relationship = [...container.querySelectorAll('[data-testid="tree-relationship"]')].find(
        (row) =>
          row.textContent?.includes('demonstrates') &&
          row.textContent?.includes('AccountCredentials'),
      );
      expect(relationship?.textContent).toContain('email');
      expect(relationship?.textContent).not.toContain('demonstratedThrough');
      expect(relationship?.textContent).not.toContain('folder');
    });
  });

  scenario('a when step invokes the operation its body calls', ({ given, when, then }) => {
    given('a when step whose body calls customer.load', () => {});
    when('the graph is loaded', () => {});
    then('the step lists invokes load', () => {
      const dto = codeQlClassWithoutSource();
      dto.practice_graphs[0].nodes.push({
        node_id: 'stories:Step:when-load',
        name: 'When My Paradise loads the customer',
        practice: 'stories',
        semantic_type: 'Step',
        keyword: 'When',
        properties: {},
        applicable_rules: [],
        violations: [],
        source: {
          file: '',
          start_line: 1,
          end_line: 3,
          text: 'customer.load(id);',
        },
      });
      dto.practice_graphs[0].relationships.push({
        kind: 'owns',
        from_id: 'ce:Module:domain.customer',
        to_id: 'stories:Step:when-load',
      });
      const tree = KnowledgeGraph.fromDto(overlayWorkspaceTree(dto)).present().listed_tree;
      const step = findTreeNode(tree, 'When My Paradise loads the customer');
      const invokes = step?.relationships?.find((group) => group.kind === 'invokes');
      expect(invokes?.targets.map((target) => target.name)).toContain('load');
      const { container } = render(
        <PracticeGraphTree roots={tree} selectedId={null} onSelect={() => undefined} />,
      );
      expandNonRuleTwists(container);
      const load = [...container.querySelectorAll('li')].find(
        (item) => item.querySelector(':scope > .tree-row .tree-name')?.textContent === 'load',
      );
      expect(load?.querySelector(':scope > .tree-row')?.textContent).toContain('load');
      expect(load?.querySelector(':scope > .tree-row')?.textContent).not.toContain('invokes');
    });
  });

  scenario('an invoke lists the other types it uses', ({ given, when, then }) => {
    given('create takes AccountCredentials and returns Customer', () => {});
    when('the Engineer expands invokes create on CustomerRepository', () => {});
    then('AccountCredentials and Customer are sub nodes', () => {
      const dto = codeQlClassWithoutSource();
      const graph = dto.practice_graphs[0];
      const source = (_name: string, text: string) => ({
        file: 'domain/customer/CustomerRepository.ts',
        start_line: 1,
        end_line: 4,
        text,
      });
      graph.nodes.push(
        {
          node_id: 'ce:OoadClass:CustomerRepository',
          name: 'CustomerRepository',
          practice: 'clean_engineering',
          semantic_type: 'OoadClass',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: source('CustomerRepository', 'export class CustomerRepository {\n  async create(accountCredentials: AccountCredentials): Promise<Customer> {}\n}'),
        },
        {
          node_id: 'ce:Operation:create',
          name: 'create',
          practice: 'clean_engineering',
          semantic_type: 'Operation',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: source('create', 'async create(accountCredentials: AccountCredentials): Promise<Customer> {\n  return created;\n}'),
        },
        {
          node_id: 'ce:OoadClass:AccountCredentials',
          name: 'AccountCredentials',
          practice: 'clean_engineering',
          semantic_type: 'OoadClass',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: source('AccountCredentials', 'export class AccountCredentials {}'),
        },
        {
          node_id: 'stories:Step:when-create',
          name: 'When the User creates their Paradise account',
          practice: 'stories',
          semantic_type: 'Step',
          keyword: 'When',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: { file: '', start_line: 1, end_line: 3, text: 'customerRepository.create(accountCredentials);' },
        },
      );
      graph.relationships.push(
        { kind: 'owns', from_id: 'ce:Module:domain.customer', to_id: 'ce:OoadClass:CustomerRepository' },
        { kind: 'owns', from_id: 'ce:OoadClass:CustomerRepository', to_id: 'ce:Operation:create' },
        { kind: 'owns', from_id: 'ce:Module:domain.customer', to_id: 'ce:OoadClass:AccountCredentials' },
        { kind: 'owns', from_id: 'ce:Module:domain.customer', to_id: 'stories:Step:when-create' },
      );
      const tree = KnowledgeGraph.fromDto(overlayWorkspaceTree(dto)).present().listed_tree;
      const { container } = render(
        <PracticeGraphTree roots={tree} selectedId={null} onSelect={() => undefined} />,
      );
      expandNonRuleTwists(container);
      const row = [...container.querySelectorAll('li')].find(
        (item) => item.querySelector(':scope > .tree-row .tree-name')?.textContent === 'create',
      );
      const names = [...(row?.querySelectorAll('.tree-name') ?? [])].map((item) => item.textContent);
      expect(row?.querySelector(':scope > .tree-row')?.textContent).not.toContain('invokes');
      expect(names).toContain('create');
      expect(names).toContain('AccountCredentials');
      expect(names).toContain('Customer');
    });
  });
});
