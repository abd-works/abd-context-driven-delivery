import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { PracticeGraphTree } from '../../../packages/explore-knowledge-graph/PracticeGraphTree';
import { compositionByClass } from '../../../packages/explore-knowledge-graph/knowledge-graph/workspace-overlay';
import type { ListedTreeNode } from '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';
import { expandNonRuleTwists } from '../helpers/story-graphs';

function node(
  id: string,
  name: string,
  semanticType: string,
  children: ListedTreeNode[] = [],
  text = '',
): ListedTreeNode {
  return {
    node_id: id,
    name,
    path: name,
    practice: semanticType === 'Aggregate' || semanticType === 'Entity' || semanticType === 'EntityRoot' ? 'ddd' : 'clean_engineering',
    semantic_type: semanticType,
    is_file: false,
    properties: {},
    rule_statuses: {},
    rules: [],
    relationships: [],
    source: text ? { file: 'Customer.ts', start_line: 1, end_line: 1, text } : null,
    origin: null,
    failed: 0,
    total: 0,
    children,
  };
}

function directNames(container: HTMLElement, title: string): string[] {
  const row = [...container.querySelectorAll('li')].find(
    (item) => item.querySelector(':scope > .tree-row .tree-name')?.textContent === title,
  );
  return [...(row?.querySelectorAll(':scope > ul > li > .tree-row .tree-name') ?? [])].map(
    (item) => item.textContent ?? '',
  );
}

describe('composition from the class model', () => {
  it('reads composition targets from a class section', () => {
    const composed = compositionByClass(`
### **Customer** <<Aggregate Root>> <<Entity>>
+ << composition >> identity: Identity
+ << association >> accountCredentials: AccountCredentials
+ << composition >> address: Address
`);
    expect(composed.get('Customer')).toEqual(['Identity', 'Address']);
  });
});

describe('same-module types nest under the member', () => {
  it('hides a class the folder root composes and keeps associations in the list', () => {
    const identity = node('class:Identity', 'Identity', 'OoadClass');
    const account = node('class:Account', 'Account', 'OoadClass');
    const audit = node('class:Audit', 'Audit', 'OoadClass');
    const customer = node('class:Customer', 'Customer', 'OoadClass', [
      node('prop:identity', 'identity', 'Property', [], 'public identity: Identity'),
      node('op:load', 'load', 'Operation', [], 'load(): Account {'),
      node('op:save', '_save', 'Operation', [], 'private _save(): Audit {'),
    ]);
    customer.relationships = [
      {
        kind: 'composition',
        targets: [
          {
            node_id: identity.node_id,
            name: 'Identity',
            semantic_type: 'OoadClass',
            practice: 'clean_engineering',
          },
        ],
      },
    ];
    const module = node('module:customer', 'customer', 'Module', [customer, identity, account, audit]);
    const view = render(<PracticeGraphTree roots={[module]} selectedId={null} onSelect={() => undefined} />);
    expandNonRuleTwists(view.container);
    expect(directNames(view.container, 'customer')).toEqual(['Customer', 'Account', 'Audit']);
    expect(directNames(view.container, 'identity')).toContain('Identity');
    expect(directNames(view.container, 'load')).toContain('Account');
  });

  it('keeps a type that lives in another module in that module', () => {
    const invoice = node('class:Invoice', 'Invoice', 'OoadClass');
    const customer = node('class:Customer', 'Customer', 'OoadClass', [
      node('prop:bill', 'bill', 'Property', [], 'bill: Invoice'),
    ]);
    const customerModule = node('module:customer', 'customer', 'Module', [customer]);
    const billing = node('module:billing', 'billing', 'Module', [invoice]);
    const view = render(
      <PracticeGraphTree roots={[customerModule, billing]} selectedId={null} onSelect={() => undefined} />,
    );
    expandNonRuleTwists(view.container);
    expect(directNames(view.container, 'billing')).toContain('Invoice');
    expect(directNames(view.container, 'customer')).toEqual(['Customer']);
  });

  it('nests an entity under the aggregate member that uses it', () => {
    const address = node('entity:Address', 'Address', 'Entity');
    const root = node('entity:Customer', 'Customer', 'EntityRoot', [
      node('prop:address', 'address', 'Property', [], 'address: Address'),
    ]);
    const aggregate = node('agg:Customer', 'Onboarding', 'Aggregate', [root, address]);
    const view = render(<PracticeGraphTree roots={[aggregate]} selectedId={null} onSelect={() => undefined} />);
    expandNonRuleTwists(view.container);
    expect(directNames(view.container, 'Onboarding')).toEqual(['Customer', 'Address']);
    expect(directNames(view.container, 'address')).toContain('Address');
  });
});
