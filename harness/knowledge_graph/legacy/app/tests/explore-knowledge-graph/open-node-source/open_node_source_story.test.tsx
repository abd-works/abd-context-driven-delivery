import { fireEvent, render } from '@testing-library/react';
import { callBodiesIn, classBodiesIn, displayedCallSource } from '../../../packages/explore-knowledge-graph/call-expansion';
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
  scenario('class Node shows the whole class', ({ given, when, then }) => {
    given('a class Node whose graph source is missing or only the header', () => {});
    when('the Engineer selects the class Node', () => {});
    then('the source pane shows the whole class body', () => {
      const graph = KnowledgeGraph.fromDto(
        overlayWorkspaceTree(codeQlClassWithoutSource()),
      ).selectNode('ce:OoadClass:Customer');
      const source = graph.present().source_file;
      expect(source?.text).toContain('export class Customer');
      expect(source?.text).toContain('processEverything');
      expect(source?.end_line).toBeGreaterThan(source?.start_line ?? 0);
    }).and('rule problems sit below that excerpt', () => {
      const graph = KnowledgeGraph.fromDto(
        overlayWorkspaceTree(codeQlClassWithoutSource()),
      ).selectNode('ce:OoadClass:Customer');
      const presented = graph.present();
      const { getByTestId, queryAllByTestId } = render(
        <SelectedNodePane
          selectedNode={presented.selected_node}
          selectedTree={presented.selected_tree}
          selectedRule={null}
          sourceFile={presented.source_file}
        />,
      );
      const excerpt = getByTestId('source-excerpt');
      expect(excerpt.textContent).toContain('processEverything');
      expect(queryAllByTestId('child-node-report')).toHaveLength(0);
    });
  });
  scenario('operation Node shows the whole operation', ({ given, when, then }) => {
    given('an operation Node whose graph source is missing or only the header', () => {});
    when('the Engineer selects the operation Node', () => {});
    then('the source pane shows the whole operation', () => {
      const graph = KnowledgeGraph.fromDto(
        overlayWorkspaceTree(codeQlClassWithoutSource()),
      ).selectNode('ce:Operation:processEverything');
      const source = graph.present().source_file;
      expect(source?.text).toContain('processEverything');
      expect(source?.text).toContain('return u');
    }).and('the pane keeps the recorded line span', () => {
      const dto = codeQlClassWithoutSource();
      const operation = dto.practice_graphs[0]?.nodes.find(
        (node) => node.node_id === 'ce:Operation:processEverything',
      );
      if (operation) {
        operation.source = {
          file: 'domain/customer/Customer.ts',
          start_line: 6,
          end_line: 29,
          text: '',
        };
      }
      const graph = KnowledgeGraph.fromDto(
        overlayWorkspaceTree(dto),
      ).selectNode('ce:Operation:processEverything');
      const source = graph.present().source_file;
      expect(source?.start_line).toBe(6);
      expect(source?.end_line).toBe(29);
      expect(source?.text).toContain('processEverything');
      expect(source?.text).toContain('return u');
      expect(source?.text).not.toContain('load(');
    });
  });
  scenario('a DDD node shows the class of the same name', ({ given, when, then }) => {
    given('a Repository with no source and a class of the same name', () => {});
    when('the Engineer selects the Repository', () => {});
    then('the source pane shows that class', () => {
      const presented = KnowledgeGraph.fromDto({
        id: '11111111-1111-1111-1111-111111111111',
        folder: '',
        practice_graphs: [
          {
            id: 'practice:workspace',
            name: 'workspace',
            nodes: [
              {
                node_id: 'ddd:BoundedContext:cart',
                name: 'Cart',
                practice: 'ddd',
                semantic_type: 'BoundedContext',
                properties: {},
                applicable_rules: [],
                violations: [],
                source: null,
              },
              {
                node_id: 'ddd:Repository:CartRepository',
                name: 'CartRepository',
                practice: 'ddd',
                semantic_type: 'Repository',
                properties: {},
                applicable_rules: [],
                violations: [],
                source: null,
              },
              {
                node_id: 'ce:OoadClass:CartRepository',
                name: 'CartRepository',
                practice: 'clean_engineering',
                semantic_type: 'OoadClass',
                properties: {},
                applicable_rules: [],
                violations: [],
                source: {
                  file: 'domain/cart/Cart.ts',
                  start_line: 260,
                  end_line: 351,
                  text: 'export class CartRepository {\n  load() {}\n}',
                },
              },
            ],
            relationships: [
              {
                kind: 'owns',
                from_id: 'ddd:BoundedContext:cart',
                to_id: 'ddd:Repository:CartRepository',
              },
            ],
          },
        ],
      })
        .filterGraph({ practice: 'ddd' })
        .selectNode('ddd:Repository:CartRepository')
        .present();
      expect(presented.source_file?.file).toBe('domain/cart/Cart.ts');
      expect(presented.source_file?.start_line).toBe(260);
      expect(presented.selected_tree?.source?.text).toContain('export class CartRepository');
      const { getByTestId } = render(
        <SelectedNodePane
          selectedNode={presented.selected_node}
          selectedTree={presented.selected_tree}
          selectedRule={null}
          sourceFile={presented.source_file}
        />,
      );
      expect(getByTestId('source-excerpt').textContent).toContain('CartRepository');
    });
  });
  scenario('an invoked operation shows its class and referenced types', ({ given, when, then }) => {
    given('a when step invokes load, and load returns Account', () => {});
    when('the Engineer opens that invokes target', () => {});
    then('the pane shows the operation without extra class sections', () => {
      const dto = overlayWorkspaceTree(codeQlClassWithoutSource());
      dto.practice_graphs[0].nodes.push({
        node_id: 'ce:OoadClass:Account',
        name: 'Account',
        practice: 'clean_engineering',
        semantic_type: 'OoadClass',
        properties: {},
        applicable_rules: [],
        violations: [],
        source: {
          file: 'domain/account/Account.ts',
          start_line: 1,
          end_line: 3,
          text: 'export class Account {\n  id: string;\n}',
        },
      });
      const customer = dto.practice_graphs[0].nodes.find(
        (node) => node.semantic_type === 'OoadClass' && node.name === 'Customer',
      );
      if (customer?.source?.text) {
        customer.source = {
          ...customer.source,
          text: customer.source.text.replace(
            'load(id: string): Customer',
            'load(id: string): Account',
          ),
        };
      }
      const load = dto.practice_graphs[0].nodes.find(
        (node) => node.semantic_type === 'Operation' && node.name === 'load',
      );
      const presented = KnowledgeGraph.fromDto(dto).selectNode(load?.node_id ?? '').present();
      const { getByTestId, getAllByTestId, queryAllByTestId } = render(
        <SelectedNodePane
          selectedNode={presented.selected_node}
          selectedTree={presented.selected_tree}
          selectedRule={null}
          sourceFile={presented.source_file}
        />,
      );
      expect(getByTestId('source-excerpt').textContent).toContain('1. load');
      expect(getAllByTestId('source-excerpt')).toHaveLength(1);
      expect(queryAllByTestId('child-node-report')).toHaveLength(0);
    });
  });
  scenario('a class pane lists nested operations', ({ given, when, then }) => {
    given('a class Node that owns operations', () => {});
    when('the Engineer selects the class Node', () => {});
    then('the source pane lists those operations under the class', () => {
      const presented = KnowledgeGraph.fromDto(
        overlayWorkspaceTree(codeQlClassWithoutSource()),
      )
        .selectNode('ce:OoadClass:Customer')
        .present();
      expect(
        presented.selected_tree?.children.some((node) => node.semantic_type === 'Operation'),
      ).toBe(false);
      const { getByTestId, queryAllByTestId } = render(
        <SelectedNodePane
          selectedNode={presented.selected_node}
          selectedTree={presented.selected_tree}
          selectedRule={null}
          sourceFile={presented.source_file}
        />,
      );
      expect(getByTestId('source-excerpt').textContent).toContain('processEverything');
      expect(queryAllByTestId('child-node-report')).toHaveLength(0);
    });
  });
  scenario('a step and its example show the classes they use', ({ given, when, then }) => {
    given('an example demonstrates Customer and a step owns that example', () => {});
    when('the Engineer selects the example and the step', () => {});
    then('both panels include the Customer class', () => {
      const dto = overlayWorkspaceTree(codeQlClassWithoutSource());
      const graph = dto.practice_graphs[0];
      graph.nodes.push(
        {
          node_id: 'stories:Example:stored',
          name: 'stored customer',
          practice: 'stories',
          semantic_type: 'Example',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: null,
        },
        {
          node_id: 'stories:Step:then',
          name: 'Then the customer is stored',
          practice: 'stories',
          semantic_type: 'Step',
          keyword: 'Then',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: { file: '', start_line: 1, end_line: 1, text: 'then the customer is stored' },
        },
      );
      graph.relationships.push(
        { kind: 'owns', from_id: 'ce:Module:domain.customer', to_id: 'stories:Step:then' },
        { kind: 'owns', from_id: 'stories:Step:then', to_id: 'stories:Example:stored' },
        { kind: 'demonstrates', from_id: 'stories:Example:stored', to_id: 'ce:OoadClass:Customer' },
      );
      const loaded = KnowledgeGraph.fromDto(dto);
      const examplePane = render(
        <SelectedNodePane
          selectedNode={loaded.selectNode('stories:Example:stored').present().selected_node}
          selectedTree={loaded.selectNode('stories:Example:stored').present().selected_tree}
          selectedRule={null}
          sourceFile={null}
        />,
      );
      expect(examplePane.queryAllByTestId('child-node-report')).toHaveLength(0);
      expect(examplePane.getByTestId('source-excerpt').textContent).toContain('export class Customer');
      examplePane.unmount();
      const step = loaded.selectNode('stories:Step:then').present();
      const stepPane = render(
        <SelectedNodePane
          selectedNode={step.selected_node}
          selectedTree={step.selected_tree}
          selectedRule={null}
          sourceFile={step.source_file}
        />,
      );
      expect(stepPane.queryAllByTestId('child-node-report')).toHaveLength(0);
      expect(stepPane.getByTestId('source-excerpt').textContent).toContain('then the customer is stored');
      expect(stepPane.getByTestId('source-excerpt').textContent).toContain('export class Customer');
    });
  });
  scenario('a typed property and an operation open their classes', ({ given, when, then }) => {
    given('credentials is an AccountCredentials property and load returns Account', () => {});
    when('the Engineer expands and selects them', () => {});
    then('the property expands to AccountCredentials and the operation expands to Account', () => {
      const dto = overlayWorkspaceTree(codeQlClassWithoutSource());
      const graph = dto.practice_graphs[0];
      const customer = graph.nodes.find((node) => node.name === 'Customer');
      if (customer?.source?.text) {
        customer.source = {
          ...customer.source,
          text: customer.source.text.replace(
            'load(id: string): Customer',
            'load(id: string): Account',
          ),
        };
      }
      graph.nodes.push(
        {
          node_id: 'ce:Property:credentials',
          name: 'credentials',
          practice: 'clean_engineering',
          semantic_type: 'Property',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: {
            file: 'domain/customer/Customer.ts',
            start_line: 2,
            end_line: 2,
            text: 'credentials: AccountCredentials;',
          },
        },
        {
          node_id: 'ce:OoadClass:AccountCredentials',
          name: 'AccountCredentials',
          practice: 'clean_engineering',
          semantic_type: 'OoadClass',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: {
            file: 'domain/account/AccountCredentials.ts',
            start_line: 1,
            end_line: 1,
            text: 'export class AccountCredentials {}',
          },
        },
        {
          node_id: 'ce:OoadClass:Account',
          name: 'Account',
          practice: 'clean_engineering',
          semantic_type: 'OoadClass',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: {
            file: 'domain/account/Account.ts',
            start_line: 1,
            end_line: 1,
            text: 'export class Account {}',
          },
        },
      );
      graph.relationships.push(
        { kind: 'owns', from_id: 'ce:OoadClass:Customer', to_id: 'ce:Property:credentials' },
        { kind: 'owns', from_id: 'ce:Module:domain.customer', to_id: 'ce:OoadClass:AccountCredentials' },
        { kind: 'owns', from_id: 'ce:Module:domain.customer', to_id: 'ce:OoadClass:Account' },
      );
      const loaded = KnowledgeGraph.fromDto(dto);
      const presented = loaded.present();
      const { container } = render(
        <PracticeGraphTree roots={presented.listed_tree} selectedId={null} onSelect={() => undefined} />,
      );
      expandNonRuleTwists(container);
      const propertyRow = [...container.querySelectorAll('li')].find((item) =>
        item.querySelector(':scope > .tree-row .tree-name')?.textContent === 'credentials',
      );
      expect(
        [...(propertyRow?.querySelectorAll('.tree-name') ?? [])].map((item) => item.textContent),
      ).toContain('AccountCredentials');
      const loadRow = [...container.querySelectorAll('li')].find((item) =>
        item.querySelector(':scope > .tree-row .tree-name')?.textContent === 'load',
      );
      expect(
        [...(loadRow?.querySelectorAll('.tree-name') ?? [])].map((item) => item.textContent),
      ).toContain('Account');
      const property = loaded.selectNode('ce:Property:credentials').present();
      const pane = render(
        <SelectedNodePane
          selectedNode={property.selected_node}
          selectedTree={property.selected_tree}
          selectedRule={null}
          sourceFile={property.source_file}
        />,
      );
      expect(pane.getByTestId('source-excerpt').textContent).toContain('1. credentials');
      expect(pane.queryAllByTestId('child-node-report')).toHaveLength(0);
      const classes = property.selected_tree ? classBodiesIn(property.selected_tree) : [];
      const layout = displayedCallSource(
        property.selected_tree?.source?.text ?? '',
        property.selected_tree ? callBodiesIn(property.selected_tree) : new Map(),
        1,
        [],
        classes,
      );
      expect(layout.text).toContain('AccountCredentials');
      expect(layout.folds.some((fold) => fold.kind === 'class')).toBe(true);
    });
  });
  scenario('hiding rules hides them in the panel', ({ given, when, then }) => {
    given('a class panel that lists a rule', () => {});
    when('show rules is off', () => {});
    then('the panel keeps the source and omits the rule', () => {
      const tree = {
        node_id: 'ce:OoadClass:Customer',
        name: 'Customer',
        path: 'Customer',
        practice: 'clean_engineering',
        semantic_type: 'OoadClass',
        is_file: false,
        properties: {},
        rule_statuses: {},
        rules: [
          {
            slug: 'keep-operations-small-and-focused',
            tag: 'base',
            status: 'violating' as const,
            body: 'Keep operations small.',
            message: 'processEverything is too long',
            practice: 'clean_engineering',
            fidelity: 'code',
          },
        ],
        relationships: [],
        source: {
          file: 'Customer.ts',
          start_line: 1,
          end_line: 1,
          text: 'export class Customer {}',
        },
        origin: null,
        failed: 1,
        total: 1,
        children: [],
      };
      const shown = render(
        <SelectedNodePane
          selectedNode={null}
          selectedTree={tree}
          selectedRule={null}
          sourceFile={tree.source}
        />,
      );
      expect(shown.getByTestId('rule-report')).toBeTruthy();
      shown.unmount();
      const hidden = render(
        <SelectedNodePane
          selectedNode={null}
          selectedTree={tree}
          selectedRule={null}
          sourceFile={tree.source}
          showRules={false}
        />,
      );
      expect(hidden.queryByTestId('rule-report')).toBeNull();
      expect(hidden.getByTestId('source-excerpt').textContent).toContain('export class Customer');
    });
  });
  scenario('an operation panel numbers the calls it makes', ({ given, when, then }) => {
    given('confirmIdentity calls profileRequirements.missing, which calls addressBook.lookup', () => {});
    when('the Engineer selects confirmIdentity', () => {});
    then('the panel expands three numbered levels and leaves the types collapsed', () => {
      const dto = codeQlClassWithoutSource();
      const graph = dto.practice_graphs[0];
      const source = (text: string) => ({
        file: 'missing/Calls.ts',
        start_line: 1,
        end_line: 4,
        text,
      });
      graph.nodes.push(
        {
          node_id: 'ce:Operation:confirmIdentity',
          name: 'confirmIdentity',
          practice: 'clean_engineering',
          semantic_type: 'Operation',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: source('confirmIdentity(customer: Customer) {\n  profileRequirements.missing(customer);\n}'),
        },
        {
          node_id: 'ce:OoadClass:ProfileRequirements',
          name: 'ProfileRequirements',
          practice: 'clean_engineering',
          semantic_type: 'OoadClass',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: source('export class ProfileRequirements {\n  missing(person: Identity): Address { return stored; }\n}'),
        },
        {
          node_id: 'ce:Operation:missing',
          name: 'missing',
          practice: 'clean_engineering',
          semantic_type: 'Operation',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: source('missing(person: Identity): Address {\n  addressBook.lookup(person);\n}'),
        },
        {
          node_id: 'ce:OoadClass:AddressBook',
          name: 'AddressBook',
          practice: 'clean_engineering',
          semantic_type: 'OoadClass',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: source('export class AddressBook { lookup(person: Identity) { postal.verify(person); } }'),
        },
        {
          node_id: 'ce:Operation:lookup',
          name: 'lookup',
          practice: 'clean_engineering',
          semantic_type: 'Operation',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: source('lookup(person: Identity) {\n  postal.verify(person);\n}'),
        },
        {
          node_id: 'ce:OoadClass:Postal',
          name: 'Postal',
          practice: 'clean_engineering',
          semantic_type: 'OoadClass',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: source('export class Postal { verify(person: Identity) { region.code(person); } }'),
        },
        {
          node_id: 'ce:Operation:verify',
          name: 'verify',
          practice: 'clean_engineering',
          semantic_type: 'Operation',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: source('verify(person: Identity) {\n  region.code(person);\n}'),
        },
        {
          node_id: 'ce:OoadClass:Identity',
          name: 'Identity',
          practice: 'clean_engineering',
          semantic_type: 'OoadClass',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: source('export class Identity {}'),
        },
        {
          node_id: 'ce:OoadClass:Address',
          name: 'Address',
          practice: 'clean_engineering',
          semantic_type: 'OoadClass',
          properties: {},
          applicable_rules: [],
          violations: [],
          source: source('export class Address {}'),
        },
      );
      graph.relationships.push(
        { kind: 'owns', from_id: 'ce:OoadClass:Customer', to_id: 'ce:Operation:confirmIdentity' },
        { kind: 'owns', from_id: 'ce:OoadClass:ProfileRequirements', to_id: 'ce:Operation:missing' },
        { kind: 'owns', from_id: 'ce:OoadClass:AddressBook', to_id: 'ce:Operation:lookup' },
        { kind: 'owns', from_id: 'ce:OoadClass:Postal', to_id: 'ce:Operation:verify' },
      );
      const presented = KnowledgeGraph.fromDto(overlayWorkspaceTree(dto))
        .selectNode('ce:Operation:confirmIdentity')
        .present();
      const pane = render(
        <SelectedNodePane
          selectedNode={presented.selected_node}
          selectedTree={presented.selected_tree}
          selectedRule={null}
          sourceFile={presented.source_file}
        />,
      );
      const text = pane.getByTestId('selected-subtree').textContent ?? '';
      expect(text).toContain('1. confirmIdentity');
      expect(text).not.toContain('1.1 profileRequirements.missing');
      const tree = presented.selected_tree;
      const bodies = tree ? callBodiesIn(tree) : new Map();
      const layout = displayedCallSource(tree?.source?.text ?? '', bodies);
      const lines = layout.text.split('\n');
      expect(layout.text).toContain('addressBook.lookup(person)');
      expect(layout.text).toContain('region.code(person)');
      expect(layout.folds.some((fold) => lines[fold.start - 1]?.includes('verify'))).toBe(true);
      const open = [...pane.container.querySelectorAll('.source-snippet')].map((node) => ({
        open: node.getAttribute('data-open'),
        title: node.querySelector('h2')?.textContent ?? '',
      }));
      expect(open.find((entry) => entry.title.includes('1. confirmIdentity'))?.open).toBe('true');
      expect(pane.queryAllByTestId('child-node-report')).toHaveLength(0);
      expect(open.some((entry) => entry.title.includes('verify'))).toBe(false);
    });
  });
  scenario('the tree lists calls under an operation and a property', ({ given, when, then }) => {
    given('confirmIdentity calls missing and credentials reads token', () => {});
    when('the Engineer expands them in the tree', () => {});
    then('those calls are child nodes', () => {
      const blank = {
        path: '',
        practice: 'clean_engineering',
        is_file: false,
        properties: {},
        rule_statuses: {},
        rules: [],
        origin: null,
        failed: 0,
        total: 0,
        children: [],
      };
      const missing = {
        ...blank,
        node_id: 'missing',
        name: 'missing',
        semantic_type: 'Operation',
        relationships: [],
        source: { file: '', start_line: 1, end_line: 1, text: 'missing() {}' },
      };
      const token = {
        ...blank,
        node_id: 'token',
        name: 'token',
        semantic_type: 'Property',
        relationships: [],
        source: { file: '', start_line: 1, end_line: 1, text: 'token: string' },
      };
      const customerId = {
        ...blank,
        node_id: 'customerId',
        name: 'customerId',
        semantic_type: 'Property',
        relationships: [],
        source: { file: '', start_line: 1, end_line: 1, text: 'customerId: string;' },
      };
      const customer = {
        ...blank,
        node_id: 'Customer',
        name: 'Customer',
        semantic_type: 'OoadClass',
        relationships: [],
        source: null,
        children: [customerId],
      };
      const confirm = {
        ...blank,
        node_id: 'confirm',
        name: 'confirmIdentity',
        semantic_type: 'Operation',
        relationships: [
          {
            kind: 'invokes',
            targets: [
              {
                node_id: 'missing',
                name: 'missing',
                semantic_type: 'Operation',
                practice: 'clean_engineering',
              },
              {
                node_id: 'customerId',
                name: 'customerId',
                semantic_type: 'Property',
                practice: 'clean_engineering',
              },
              {
                node_id: 'when-create',
                name: 'When the User creates their Paradise account',
                semantic_type: 'Step',
                practice: 'stories',
              },
            ],
          },
        ],
        source: {
          file: '',
          start_line: 1,
          end_line: 3,
          text: 'profileRequirements.missing(customer);\naccount.customerId = id;',
        },
      };
      const credentials = {
        ...blank,
        node_id: 'credentials',
        name: 'credentials',
        semantic_type: 'Property',
        relationships: [
          {
            kind: 'invokes',
            targets: [
              {
                node_id: 'token',
                name: 'token',
                semantic_type: 'Property',
                practice: 'clean_engineering',
              },
            ],
          },
        ],
        source: { file: '', start_line: 1, end_line: 1, text: 'account.token' },
      };
      const { container } = render(
        <PracticeGraphTree
          roots={[customer, confirm, credentials]}
          nodes={[missing, token, customerId]}
          practices={['clean_engineering']}
          showRules={false}
          selectedId={null}
          onSelect={() => undefined}
        />,
      );
      for (const twist of container.querySelectorAll('[data-testid="tree-expand"]')) {
        if (twist.getAttribute('aria-expanded') === 'false') {
          fireEvent.click(twist);
        }
      }
      const classRow = [...container.querySelectorAll('li')].find(
        (item) => item.querySelector(':scope > .tree-row .tree-name')?.textContent === 'Customer',
      );
      const operationRow = [...container.querySelectorAll('li')].find(
        (item) => item.querySelector(':scope > .tree-row .tree-name')?.textContent === 'confirmIdentity',
      );
      expect(
        [...(classRow?.querySelectorAll('.tree-name') ?? [])].map((item) => item.textContent),
      ).toContain('customerId');
      expect(
        [...(operationRow?.querySelectorAll('.tree-name') ?? [])].map((item) => item.textContent),
      ).not.toContain('customerId');
      expect(
        [...(operationRow?.querySelectorAll('.tree-name') ?? [])].map((item) => item.textContent),
      ).not.toContain('When the User creates their Paradise account');
      const names = [...container.querySelectorAll('.tree-name')].map((item) => item.textContent);
      expect(names).toContain('profileRequirements.missing');
      expect(names).toContain('account.token');
      const pane = KnowledgeGraph.fromDto({
        id: '33333333-3333-4333-8333-333333333333',
        folder: 'workspace',
        practice_graphs: [
          {
            id: 'practice:ce',
            name: 'clean_engineering',
            nodes: [
              {
                node_id: 'Customer',
                name: 'Customer',
                practice: 'clean_engineering',
                semantic_type: 'OoadClass',
                properties: {},
                applicable_rules: [],
                violations: [],
                source: null,
              },
              {
                node_id: 'customerId',
                name: 'customerId',
                practice: 'clean_engineering',
                semantic_type: 'Property',
                properties: {},
                applicable_rules: [],
                violations: [],
                source: { file: '', start_line: 1, end_line: 1, text: 'customerId: string;' },
              },
              {
                node_id: 'confirm',
                name: 'confirmIdentity',
                practice: 'clean_engineering',
                semantic_type: 'Operation',
                properties: {},
                applicable_rules: [],
                violations: [],
                source: {
                  file: '',
                  start_line: 1,
                  end_line: 2,
                  text: 'account.customerId = id;',
                },
              },
            ],
            relationships: [
              { kind: 'owns', from_id: 'Customer', to_id: 'customerId' },
              { kind: 'owns', from_id: 'Customer', to_id: 'confirm' },
              { kind: 'invokes', from_id: 'confirm', to_id: 'customerId' },
            ],
          },
        ],
      });
      const selected = pane.selectNode('confirm').present().selected_tree;
      const selectedNames = [selected?.name, ...(selected?.children ?? []).map((child) => child.name)];
      expect(selectedNames).not.toContain('account.customerId');
    });
  });
});
