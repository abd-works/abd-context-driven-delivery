import { describe, expect, it } from 'vitest';
import { callBodiesIn, displayedCallSource, type CallBody } from '../../../packages/explore-knowledge-graph/call-expansion';
import { KnowledgeGraph } from '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';
import { propertyExcerpt } from '../../../packages/explore-knowledge-graph/knowledge-graph/workspace-overlay';
import { definitionsInFile } from '../../../packages/explore-knowledge-graph/knowledge-graph/workspace';
import type { ListedTreeNode } from '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';

function body(member: string, text: string, id = member): CallBody {
  return { id, member, label: member, text };
}

describe('call expansion', () => {
  const bodies = new Map<string, CallBody>([
    ['persistCustomer', body('persistCustomer', 'persistCustomer(accountCredentials) {\n  this.storeCustomerId(created);\n}')],
    ['storeCustomerId', body('storeCustomerId', 'storeCustomerId(created) {\n  return created.id;\n}')],
    ['token', body('token', 'token: string')],
  ]);

  it('lists each operation on the line, collapsed, before its body', () => {
    const source = 'await this.persistCustomer(account); this.storeCustomerId(created);';
    const layout = displayedCallSource(source, bodies);
    const lines = layout.text.split('\n');
    const persistAt = lines.findIndex((line) => line.trim().startsWith('persistCustomer('));
    const storeAt = lines.findIndex((line) => line.trim().startsWith('storeCustomerId('));
    expect(persistAt).toBeGreaterThan(0);
    expect(storeAt).toBeGreaterThan(persistAt);
    expect(layout.folds.find((fold) => fold.start === 1)?.kind).toBe('call');
    expect(layout.folds.find((fold) => fold.start === persistAt + 1)?.kind).toBe('call');
    expect(layout.lineNumbers[0]).toBe('1');
    expect(layout.lineNumbers[1]).toBe('');
  });

  it('lists parameter and return types after the operations', () => {
    const persist = body(
      'persistCustomer',
      'persistCustomer(account: AccountCredentials): Customer {\n  return account;\n}',
    );
    persist.types = [
      { id: 'creds', name: 'AccountCredentials', text: 'export class AccountCredentials {\n  email: string;\n}' },
      { id: 'customer', name: 'Customer', text: 'export class Customer {\n  id: string;\n}' },
    ];
    const layout = displayedCallSource('this.persistCustomer(account);', new Map([['persistCustomer', persist]]));
    const lines = layout.text.split('\n');
    const operationAt = lines.findIndex((line) => line.includes('persistCustomer(account:'));
    const credentialsAt = lines.findIndex((line) => line.trim() === 'AccountCredentials');
    const customerAt = lines.findIndex((line) => line.trim() === 'Customer');
    expect(operationAt).toBeGreaterThan(0);
    expect(credentialsAt).toBeGreaterThan(operationAt);
    expect(customerAt).toBeGreaterThan(credentialsAt);
    expect(layout.folds.find((fold) => fold.start === credentialsAt + 1)?.kind).toBe('class');
    expect(layout.text).toContain('export class Customer');
  });

  it('keeps the indent of the lines that follow a call', () => {
    const source = [
      '  async create() {',
      '    const created = await this.persistCustomer(accountCredentials);',
      '    return created;',
      '  }',
    ].join('\n');
    const layout = displayedCallSource(source, bodies);
    const lines = layout.text.split('\n');
    const start = lines.findIndex((line) => line.includes('const created')) + 1;
    const fold = layout.folds.find((entry) => entry.start === start);
    expect(lines[fold?.end ?? 0]).toBe('    return created;');
    expect(lines.at(-1)).toBe('  }');
  });

  it('stops at five levels', () => {
    const deep = new Map<string, CallBody>([
      ['missing', body('missing', 'missing(person) {\n  addressBook.lookup(person);\n}')],
      ['lookup', body('lookup', 'lookup(person) {\n  postal.verify(person);\n}')],
      ['verify', body('verify', 'verify(person) {\n  region.code(person);\n}')],
      ['code', body('code', 'code(person) {\n  atlas.find(person);\n}')],
      ['find', body('find', 'find(person) {\n  store.read(person);\n}')],
    ]);
    const layout = displayedCallSource('profileRequirements.missing(customer);', deep);
    const lines = layout.text.split('\n');
    expect(layout.text).toContain('atlas.find(person)');
    expect(layout.text).not.toContain('store.read');
    expect(layout.folds.some((fold) => lines[fold.start - 1]?.includes('.find'))).toBe(false);
  });

  it('keeps a simple property off the call list', () => {
    const node = {
      node_id: 'create',
      name: 'create',
      semantic_type: 'Operation',
      source: { text: 'account.token' },
      children: [
        {
          node_id: 'token',
          name: 'account.token',
          semantic_type: 'Property',
          source: { text: 'token: string' },
          children: [],
        },
        {
          node_id: 'load',
          name: 'repository.load',
          semantic_type: 'Operation',
          source: { text: 'load(id: string): Account { return id; }' },
          children: [
            {
              node_id: 'account',
              name: 'Account',
              semantic_type: 'OoadClass',
              source: { text: 'export class Account {}' },
              children: [],
            },
          ],
        },
      ],
    } as ListedTreeNode;
    const found = callBodiesIn(node);
    expect([...found.keys()]).toEqual(['load']);
    expect(found.get('load')?.types?.map((type) => type.name)).toEqual(['Account']);
  });

  it('anchors invoked operations then lists classes on a prose line', () => {
    const layout = displayedCallSource(
      'then the customer is stored',
      new Map(),
      1,
      [],
      [{ id: 'customer', name: 'Customer', text: 'export class Customer {\n  id: string;\n}' }],
      [body('create', 'create(credentials) {\n  return credentials;\n}', 'ce:Operation:create')],
      true,
    );
    const lines = layout.text.split('\n');
    const createAt = lines.findIndex((line) => line.trim().startsWith('create('));
    const classAt = lines.findIndex((line) => line.trim() === 'Customer');
    expect(lines[0]).toBe('then the customer is stored');
    expect(createAt).toBeGreaterThan(0);
    expect(classAt).toBeGreaterThan(createAt);
    expect(layout.text).toContain('export class Customer');
    expect(layout.folds.find((fold) => fold.start === 1)?.kind).toBe('call');
    expect(layout.folds.find((fold) => fold.start === classAt + 1)?.kind).toBe('class');
  });

  it('uses the property line and expands its type the way an operation expands a call', () => {
    const excerpt = propertyExcerpt('email', {
      file: 'domain/customer/Customer.ts',
      start_line: 23,
      end_line: 36,
      text: [
        'export class Identity {',
        '  constructor(',
        '    public email: string,',
        '    public name = \'\',',
        '  ) {}',
        '}',
      ].join('\n'),
    });
    expect(excerpt.text.trim()).toBe('public email: string,');
    expect(excerpt.start_line).toBe(25);
    const layout = displayedCallSource(
      excerpt.text,
      new Map(),
      1,
      [],
      [{ id: 'string-skip', name: 'string', text: 'export class string {}' }],
    );
    expect(layout.text.split('\n')[0]).toContain('public email: string');
    const fields = definitionsInFile({
      relativePath: 'domain/customer/Customer.ts',
      text: [
        'export class Customer {',
        '  public identity: Identity;',
        '  constructor(',
        '    public accountCredentials: AccountCredentials,',
        '  ) {',
        '    this.identity = new Identity(accountCredentials.email);',
        '  }',
        '}',
      ].join('\n'),
    }).filter((entry) => entry.semantic_type === 'Property');
    expect(fields.map((entry) => entry.name).sort()).toEqual(['accountCredentials', 'identity']);
    expect(fields.find((entry) => entry.name === 'accountCredentials')?.source.text).toContain(
      'public accountCredentials: AccountCredentials',
    );
  });

  it('folds this.callee from source even without an invoke edge', () => {
    const graph = KnowledgeGraph.fromDto({
      id: '11111111-1111-1111-1111-111111111111',
      folder: '',
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
              properties: {},
              applicable_rules: [],
              violations: [],
              source: { file: 'Customer.ts', start_line: 1, end_line: 20, text: 'export class Customer {}' },
            },
            {
              node_id: 'ce:Operation:persistCustomer',
              name: 'persistCustomer',
              practice: 'clean_engineering',
              semantic_type: 'Operation',
              properties: {},
              applicable_rules: [],
              violations: [],
              source: {
                file: 'Customer.ts',
                start_line: 10,
                end_line: 14,
                text: 'persistCustomer() {\n  const email = this.validateToken();\n  return this.persistNewCustomer(email);\n}',
              },
            },
            {
              node_id: 'ce:Operation:validateToken',
              name: 'validateToken',
              practice: 'clean_engineering',
              semantic_type: 'Operation',
              properties: {},
              applicable_rules: [],
              violations: [],
              source: {
                file: 'Customer.ts',
                start_line: 15,
                end_line: 16,
                text: 'validateToken() {\n  return true;\n}',
              },
            },
            {
              node_id: 'ce:Operation:persistNewCustomer',
              name: 'persistNewCustomer',
              practice: 'clean_engineering',
              semantic_type: 'Operation',
              properties: {},
              applicable_rules: [],
              violations: [],
              source: {
                file: 'Customer.ts',
                start_line: 17,
                end_line: 18,
                text: 'persistNewCustomer(email) {\n  return email;\n}',
              },
            },
          ],
          relationships: [
            { kind: 'owns', from_id: 'ce:OoadClass:Customer', to_id: 'ce:Operation:persistCustomer' },
            { kind: 'owns', from_id: 'ce:OoadClass:Customer', to_id: 'ce:Operation:validateToken' },
            { kind: 'owns', from_id: 'ce:OoadClass:Customer', to_id: 'ce:Operation:persistNewCustomer' },
          ],
        },
      ],
    });
    const pane = graph.selectNode('ce:Operation:persistCustomer').presentSelection();
    const tree = pane.selected_tree;
    const bodies = tree ? callBodiesIn(tree) : new Map();
    const layout = displayedCallSource(tree?.source?.text ?? '', bodies);
    expect([...bodies.keys()].sort()).toEqual(['persistNewCustomer', 'validateToken']);
    expect(layout.folds.length).toBeGreaterThan(0);
    expect(layout.text).toContain('validateToken() {');
    expect(layout.text).toContain('persistNewCustomer(email) {');
  });
});
