import { describe, expect, it } from 'vitest';
import {
  arrangeListedClassChildren,
  KnowledgeGraph,
} from '../../packages/explore-knowledge-graph/knowledge-graph/graph';

describe('listed class children', () => {
  it('keeps relatives on the class and leftover properties under properties', () => {
    const arranged = arrangeListedClassChildren(
      { node_id: 'ce:OoadClass:AccountCredentials', practice: 'clean_engineering' },
      [
        listed('token', 'Property'),
        listed('email', 'Property'),
        listed('_repository', 'Property'),
        listed('verify', 'Operation'),
      ],
      new Set(['ce:Property:token']),
    );
    expect(arranged.map((node) => node.name)).toEqual(['token', 'verify', 'properties']);
    expect(arranged.find((node) => node.name === 'properties')?.children.map((node) => node.name).sort()).toEqual([
      '_repository',
      'email',
    ]);
  });

  it('keeps relatives and the properties group if listed children were already arranged', () => {
    const once = arrangeListedClassChildren(
      { node_id: 'ce:OoadClass:AccountCredentials', practice: 'clean_engineering' },
      [
        listed('token', 'Property'),
        listed('email', 'Property'),
        listed('_repository', 'Property'),
        listed('verify', 'Operation'),
      ],
      new Set(['ce:Property:token']),
    );
    const arranged = arrangeListedClassChildren(
      { node_id: 'ce:OoadClass:AccountCredentials', practice: 'clean_engineering' },
      once,
      new Set(['ce:Property:token']),
    );
    expect(arranged.map((node) => node.name)).toEqual(['token', 'verify', 'properties']);
    expect(arranged.find((node) => node.name === 'properties')?.children.map((node) => node.name).sort()).toEqual([
      '_repository',
      'email',
    ]);
  });

  it('puts a domain-typed field under properties unless CodeQL marked it relative', () => {
    const arranged = arrangeListedClassChildren(
      { node_id: 'ce:OoadClass:AccountCredentials', practice: 'clean_engineering' },
      [
        {
          ...listed('token', 'Property'),
          source: {
            file: 'src/account-credentials.ts',
            start_line: 53,
            end_line: 53,
            text: 'token: AccountToken | null = null',
          },
        },
        listed('email', 'Property'),
      ],
    );
    expect(arranged.map((node) => node.name)).toEqual(['token', 'properties']);
    expect(arranged.find((node) => node.name === 'properties')?.children.map((node) => node.name)).toEqual([
      'email',
    ]);
  });

  it('lists relatives, then operations, then properties', () => {
    const arranged = arrangeListedClassChildren(
      { node_id: 'ce:OoadClass:AccountCredentials', practice: 'clean_engineering' },
      [
        {
          ...listed('customer', 'Operation'),
          source: {
            file: 'src/account-credentials.ts',
            start_line: 106,
            end_line: 108,
            text: 'get customer(): Customer | null {\n    return this._customer;\n  }',
          },
        },
        listed('email', 'Property'),
        listed('_repository', 'Property'),
        listed('verify', 'Operation'),
      ],
    );
    expect(arranged.map((node) => node.name)).toEqual(['customer', 'verify', 'properties']);
    expect(arranged.find((node) => node.name === 'customer')?.semantic_type).toBe('Property');
    expect(arranged.find((node) => node.name === 'properties')?.children.map((node) => node.name).sort()).toEqual([
      '_repository',
      'email',
    ]);
  });

  it('presents relatives, then operations, then properties under the class', () => {
    const presented = KnowledgeGraph.fromDto({
      id: '11111111-1111-4111-8111-111111111111',
      folder: 'C:/tmp/kg',
      practice_graphs: [
        {
          id: 'practice:clean_engineering',
          name: 'clean_engineering',
          nodes: [
            node('ce:OoadClass:AccountCredentials', 'AccountCredentials', 'OoadClass', {
              file: 'src/account-credentials.ts',
              start_line: 29,
              end_line: 200,
              text: 'export class AccountCredentials {}',
            }),
            node('ce:Property:token', 'token', 'Property', {
              file: 'src/account-credentials.ts',
              start_line: 53,
              end_line: 53,
              text: 'token: AccountToken | null = null',
            }),
            node('ce:Operation:customer', 'customer', 'Operation', {
              file: 'src/account-credentials.ts',
              start_line: 106,
              end_line: 108,
              text: 'get customer(): Customer | null {\n    return this._customer;\n  }',
            }),
            node('ce:Property:email', 'email', 'Property', {
              file: 'src/account-credentials.ts',
              start_line: 66,
              end_line: 66,
              text: 'public email = \'\'',
            }),
            node('ce:Property:_repository', '_repository', 'Property', {
              file: 'src/account-credentials.ts',
              start_line: 62,
              end_line: 62,
              text: '_repository?: AccountCredentialsRepository',
            }),
            node('ce:Operation:verify', 'verify', 'Operation', {
              file: 'src/account-credentials.ts',
              start_line: 150,
              end_line: 160,
              text: 'verify(): void {}',
            }),
          ],
          relationships: [
            { kind: 'owns', from_id: 'ce:OoadClass:AccountCredentials', to_id: 'ce:Property:token' },
            { kind: 'owns', from_id: 'ce:OoadClass:AccountCredentials', to_id: 'ce:Operation:customer' },
            { kind: 'owns', from_id: 'ce:OoadClass:AccountCredentials', to_id: 'ce:Property:email' },
            { kind: 'owns', from_id: 'ce:OoadClass:AccountCredentials', to_id: 'ce:Property:_repository' },
            { kind: 'owns', from_id: 'ce:OoadClass:AccountCredentials', to_id: 'ce:Operation:verify' },
            { kind: 'relative', from_id: 'ce:OoadClass:AccountCredentials', to_id: 'ce:Property:token' },
          ],
        },
      ],
    }).present();
    const account = walk(presented.listed_tree).find((row) => row.name === 'AccountCredentials');
    expect(account?.children.map((child) => child.name)).toEqual([
      'customer',
      'token',
      'verify',
      'properties',
    ]);
    expect(account?.children.find((child) => child.name === 'properties')?.children.map((child) => child.name).sort()).toEqual([
      '_repository',
      'email',
    ]);
    expect(presented.listed_tree.map((row) => row.name)).toEqual(['clean_engineering']);
    expect(presented.listed_tree[0]?.semantic_type).toBe('Practice');
  });
});

function walk(nodes: { name: string; children?: any[] }[]): { name: string; children?: any[] }[] {
  return nodes.flatMap((node) => [node, ...walk(node.children ?? [])]);
}

function node(
  node_id: string,
  name: string,
  semantic_type: string,
  source: { file: string; start_line: number; end_line: number; text: string },
) {
  return {
    node_id,
    name,
    practice: 'clean_engineering',
    fidelity: 'code',
    semantic_type,
    properties: { folder: 'src' },
    applicable_rules: [],
    violations: [],
    source,
  };
}

function listed(name: string, semantic_type: 'Property' | 'Operation') {
  return {
    node_id: `ce:${semantic_type}:${name}`,
    name,
    path: name,
    practice: 'clean_engineering',
    semantic_type,
    is_file: false,
    properties: {},
    rule_statuses: {},
    rules: [],
    relationships: [],
    source: null,
    origin: null,
    children: [],
    failed: 0,
    total: 0,
  };
}
