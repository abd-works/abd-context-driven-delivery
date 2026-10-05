import { act, cleanup, render, screen, waitFor, within } from '@testing-library/react';
import userEvent, { type UserEvent } from '@testing-library/user-event';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { App } from './App';

const foldMarks = vi.hoisted(() => ({ names: [] as string[] }));

vi.mock('@monaco-editor/react', () => ({
  default: ({
    value,
    onMount,
  }: {
    value: string;
    onMount?: (editor: {
      getValue: () => string;
      setValue: (next: string) => void;
      getModel: () => { getLineCount: () => number };
      getDomNode: () => HTMLElement;
      getTargetAtClientPoint: () => null;
      createDecorationsCollection: (next: { options: { glyphMarginClassName?: string } }[]) => {
        set: (items: { options: { glyphMarginClassName?: string } }[]) => void;
        clear: () => void;
      };
      setHiddenAreas: () => void;
    }) => void;
  }) => {
    const record = (items: { options: { glyphMarginClassName?: string } }[]) => {
      foldMarks.names = items.flatMap((item) => (item.options.glyphMarginClassName ? [item.options.glyphMarginClassName] : []));
    };
    onMount?.({
      getValue: () => value,
      setValue: () => undefined,
      getModel: () => ({ getLineCount: () => value.split('\n').length }),
      getDomNode: () => document.body,
      getTargetAtClientPoint: () => null,
      createDecorationsCollection: (next) => {
        record(next);
        return { set: record, clear: () => undefined };
      },
      setHiddenAreas: () => undefined,
    });
    return <pre data-testid="source-editor">{value}</pre>;
  },
}));

const folder = 'C:\\dev\\example';
const registerText = 'register(input: Credentials) {\n  if (input) {\n    credentials.save();\n  }\n  credentials.notify();\n}';
const engineeringTree = {
  type: 'Practice',
  name: 'clean_engineering',
  node_id: 'practice',
  children: [
    {
      type: 'Module',
      name: 'account',
      node_id: 'module-1',
      children: [
        {
          type: 'OoadClass',
          name: 'AccountCredentials',
          node_id: 'class-1',
          children: [
            {
              type: 'Operation',
              name: 'register',
              node_id: 'op-1',
              children: [
                {
                  type: 'invokes',
                  name: 'invokes',
                  node_id: 'invokes-1',
                  children: [
                    { type: 'Operation', name: 'save', node_id: 'save', children: [] },
                    { type: 'Operation', name: 'notify', node_id: 'notify', children: [] },
                  ],
                },
              ],
            },
          ],
        },
        { type: 'OoadClass', name: 'Unused', node_id: 'class-2', children: [] },
      ],
    },
  ],
};
const domainTree = {
  type: 'Practice',
  name: 'ddd',
  node_id: 'ddd',
  children: [
    {
      type: 'BoundedContext',
      name: 'bounded context',
      node_id: 'bc',
      children: [
        {
          type: 'Aggregate',
          name: 'account-credentials',
          node_id: 'aggregate-account',
          children: [
            {
              type: 'EntityRoot',
              name: 'AccountCredentials',
              node_id: 'entity-account',
              children: [
                {
                  type: 'associates',
                  name: 'associates',
                  node_id: 'associates-account',
                  children: [
                    {
                      type: 'EntityRoot',
                      name: 'Customer',
                      node_id: 'entity-customer',
                      children: [
                        {
                          type: 'belongsTo',
                          name: 'belongsTo',
                          node_id: 'belongs-customer-entity',
                          children: [{ type: 'Aggregate', name: 'customer', node_id: 'aggregate-customer', children: [] }],
                        },
                      ],
                    },
                  ],
                },
              ],
            },
          ],
        },
        {
          type: 'Aggregate',
          name: 'customer',
          node_id: 'aggregate-customer',
          children: [
            { type: 'EntityRoot', name: 'Customer', node_id: 'entity-customer', children: [] },
            { type: 'Repository', name: 'CustomerRepository', node_id: 'repo-customer', children: [] },
            { type: 'ValueObject', name: 'Address', node_id: 'vo-address', children: [] },
            { type: 'ValueObject', name: 'Identity', node_id: 'vo-identity', children: [] },
          ],
        },
      ],
    },
  ],
};
const storiesTree = {
  type: 'Practice',
  name: 'stories',
  node_id: 'stories',
  children: [{ type: 'Epic', name: 'Onboard', node_id: 'epic-1', children: [] }],
};

const inventory = {
  clean_engineering: {
    node_counts: { Module: 1, OoadClass: 2, Operation: 3 },
    edge_count: 3,
    node_types: ['Module', 'OoadClass', 'Operation'],
    edge_types: ['contains', 'owns', 'invokes'],
    rules: ['module-rule', 'class-rule', 'limit-operation-parameters'],
    tree: engineeringTree,
  },
  ddd: {
    node_counts: { Aggregate: 2, EntityRoot: 2, Repository: 1, ValueObject: 2 },
    edge_count: 4,
    node_types: ['BoundedContext', 'Aggregate', 'EntityRoot', 'Repository', 'ValueObject'],
    edge_types: ['owns', 'associates', 'belongsTo'],
    rules: [],
    tree: domainTree,
  },
  stories: {
    node_counts: { Epic: 1 },
    edge_count: 1,
    node_types: ['Epic'],
    edge_types: ['tells'],
    rules: ['verb-noun'],
    tree: storiesTree,
  },
};

const calls: { operation: string; body: Record<string, unknown> }[] = [];

beforeEach(() => {
  calls.length = 0;
  foldMarks.names = [];
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      const operation = String(url).replace('/api/', '');
      const body = init?.body ? (JSON.parse(String(init.body)) as Record<string, unknown>) : {};
      calls.push({ operation, body });
      return { ok: true, json: async () => ({ ok: true, result: answer(operation, body) }) };
    }),
  );
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it('should leave every practice collapsed until it is opened', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  expect(screen.queryByText('account')).toBeNull();
  await expand(user, 'clean_engineering');
  expect(screen.getByText('account')).toBeTruthy();
  expect(screen.queryByText('AccountCredentials')).toBeNull();
});

it('should show the customer aggregate with its entity, repository, and value objects', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await expand(user, 'ddd');
  await expand(user, 'bounded context');
  await expand(user, 'customer');
  const aggregate = document.querySelector('[data-node-id="aggregate-customer"]');
  expect(aggregate).toBeTruthy();
  expect(within(aggregate as HTMLElement).getByText('Customer')).toBeTruthy();
  expect(within(aggregate as HTMLElement).getByText('CustomerRepository')).toBeTruthy();
  expect(within(aggregate as HTMLElement).getByText('Address')).toBeTruthy();
  expect(within(aggregate as HTMLElement).getByText('Identity')).toBeTruthy();
});

it('should list every invoke under an operation', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await expand(user, 'clean_engineering');
  await expand(user, 'account');
  await expand(user, 'AccountCredentials');
  await expand(user, 'register');
  const invokes = document.querySelector('[data-node-id="invokes-1"]');
  await expand(user, 'invokes');
  expect(invokes).toBeTruthy();
  expect(within(invokes as HTMLElement).getByText('save')).toBeTruthy();
  expect(within(invokes as HTMLElement).getByText('notify')).toBeTruthy();
});

it('should fold calls, classes, and blocks in the source', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await expand(user, 'clean_engineering');
  await expand(user, 'account');
  await expand(user, 'AccountCredentials');
  await user.click(screen.getByText('register'));
  const editor = await screen.findByTestId('source-editor');
  expect(editor.textContent).toContain('stored();');
  expect(editor.textContent).toContain('sent();');
  expect(foldMarks.names.some((name) => name.includes('call-fold'))).toBe(true);
  expect(foldMarks.names.some((name) => name.includes('class-fold'))).toBe(true);
  expect(foldMarks.names.some((name) => name.includes('block-fold'))).toBe(true);
});

it('should select every node, connector, and rule for the practice', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.selectOptions(screen.getByTestId('filter-practice'), ['clean_engineering']);
  await waitFor(() => expect(chosen('filter-node')).toEqual(['Module', 'OoadClass', 'Operation']));
  expect(options('filter-node')).toEqual(['Module', 'OoadClass', 'Operation']);
  expect(chosen('filter-connector')).toEqual(['contains', 'owns', 'invokes']);
  expect(options('filter-connector')).toEqual(['contains', 'owns', 'invokes']);
  expect(chosen('filter-rule')).toEqual(['module-rule', 'class-rule', 'limit-operation-parameters']);
});

it('should keep the first practice filters when another practice is added', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.selectOptions(screen.getByTestId('filter-practice'), ['clean_engineering']);
  await waitFor(() => expect(chosen('filter-node')).toContain('OoadClass'));
  pickOnly('filter-node', ['Module']);
  await waitFor(() => expect(chosen('filter-connector')).toEqual(['contains']));
  await user.selectOptions(screen.getByTestId('filter-practice'), ['clean_engineering', 'stories']);
  await waitFor(() => expect(chosen('filter-practice')).toEqual(['clean_engineering', 'stories']));
  expect(chosen('filter-node')).toEqual(['Module', 'Epic']);
  expect(options('filter-node')).toEqual(['Module', 'OoadClass', 'Operation', 'Epic']);
  expect(chosen('filter-connector')).toEqual(['contains', 'tells']);
  expect(chosen('filter-rule')).toEqual(['module-rule', 'verb-noun']);
});

it('should show a module without its children and a class with its module', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.selectOptions(screen.getByTestId('filter-practice'), ['clean_engineering']);
  await waitFor(() => expect(chosen('filter-node')).toContain('Module'));
  pickOnly('filter-node', ['Module']);
  await waitFor(() => expect(chosen('filter-connector')).toEqual(['contains']));
  await expand(user, 'clean_engineering');
  expect(screen.getByText('account')).toBeTruthy();
  expect(screen.queryByText('AccountCredentials')).toBeNull();
  pickOnly('filter-node', ['OoadClass']);
  await waitFor(() => expect(chosen('filter-connector')).toEqual(['owns']));
  await expand(user, 'clean_engineering');
  await expand(user, 'account');
  await expand(user, 'AccountCredentials');
  expect(screen.getByText('AccountCredentials')).toBeTruthy();
  expect(screen.queryByText('register')).toBeNull();
});

it('should keep the selected node type and drop the other class', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await expand(user, 'clean_engineering');
  await expand(user, 'account');
  expect(screen.getByText('Unused')).toBeTruthy();
  await user.selectOptions(screen.getByTestId('filter-node'), ['Operation']);
  await waitFor(() => expect(screen.queryByText('Unused')).toBeNull());
  await expand(user, 'clean_engineering');
  await expand(user, 'account');
  await expand(user, 'AccountCredentials');
  expect(screen.getByText('register')).toBeTruthy();
  const filtered = calls.filter((call) => call.operation === 'return_nodes').at(-1);
  expect(filtered?.body.filter).toMatchObject({ node_types: ['Operation'] });
});

it('should put the chosen folder on the page and show its classes', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  expect((screen.getByTestId('chosen-folder') as HTMLInputElement).value).toBe(folder);
  await expand(user, 'clean_engineering');
  await expand(user, 'account');
  expect(screen.getByText('AccountCredentials')).toBeTruthy();
  expect(calls.map((call) => call.operation)).toEqual(['choose_folder', 'load_working_copy', 'inventory']);
});

it('should start with the source pane asking for a node', () => {
  render(<App />);
  expect(screen.getByText('Select a node')).toBeTruthy();
});

it('should send violations when the switch is turned on', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.click(screen.getByRole('button', { name: 'Violations' }));
  await waitFor(() =>
    expect(calls.some((call) => call.operation === 'return_nodes' && (call.body.filter as { violations: boolean }).violations)).toBe(true),
  );
});

it('should create the database for the chosen folder', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.click(screen.getByTestId('create-database'));
  expect((await screen.findByTestId('work-progress')).textContent).toContain('Created the database');
  expect(calls.at(-1)?.operation).toBe('create_database');
});

it('should merge the working copy onto master', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.click(screen.getByTestId('refresh-master'));
  expect(await screen.findByTestId('work-progress')).toHaveProperty('textContent', 'Merged working copy onto master');
  expect(calls.some((call) => call.operation === 'reload_working_copy')).toBe(true);
});

it('should reload the working copy for the chosen folder', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.click(screen.getByTestId('reload-working-copy'));
  expect(await screen.findByTestId('work-progress')).toHaveProperty('textContent', 'Reloaded the working copy');
  expect(calls.filter((call) => call.operation === 'load_working_copy').length).toBeGreaterThan(1);
});

async function openFolder(user: UserEvent) {
  render(<App />);
  await user.click(screen.getByTestId('working-folder'));
  await screen.findByRole('button', { name: 'Expand clean_engineering' });
}

async function expand(user: UserEvent, name: string) {
  const closed = screen.queryByRole('button', { name: `Expand ${name}` });
  if (closed) {
    await user.click(closed);
  }
}

function pickOnly(testId: string, values: string[]) {
  const select = screen.getByTestId(testId) as HTMLSelectElement;
  act(() => {
    for (const option of Array.from(select.options)) {
      option.selected = values.includes(option.value);
    }
    select.dispatchEvent(new Event('change', { bubbles: true }));
  });
}

function options(testId: string): string[] {
  return Array.from((screen.getByTestId(testId) as HTMLSelectElement).options).map((option) => option.value);
}

function chosen(testId: string): string[] {
  return Array.from((screen.getByTestId(testId) as HTMLSelectElement).selectedOptions).map((option) => option.value);
}

function answer(operation: string, body: Record<string, unknown>): unknown {
  const filter = (body.filter ?? {}) as { practices?: string[]; node_types?: string[] };
  if (operation === 'choose_folder') {
    return folder;
  }
  if (operation === 'inventory') {
    return inventory;
  }
  if (operation === 'filter_choices') {
    return constrained(filter.node_types ?? []);
  }
  if (operation === 'return_nodes') {
    return rowsFor(filter.practices ?? [], filter.node_types ?? []);
  }
  if (operation === 'source') {
    return {
      node_id: body.node_id,
      name: 'register',
      type: 'Operation',
      file: 'register.ts',
      text: registerText,
      start_line: 1,
      end_line: 4,
      members: [
        { id: 'op-1', name: 'register', kind: 'Operation', owner: 'AccountCredentials', text: registerText, file: 'register.ts', start: 1, end: 4 },
        { id: 'save', name: 'save', kind: 'Operation', owner: 'Credentials', text: 'save() {\n  stored();\n}', file: 'credentials.ts', start: 1, end: 3 },
        { id: 'notify', name: 'notify', kind: 'Operation', owner: 'Credentials', text: 'notify() {\n  sent();\n}', file: 'credentials.ts', start: 5, end: 7 },
        { id: 'class-c', name: 'Credentials', kind: 'OoadClass', owner: '', text: 'class Credentials {\n  token: string;\n}', file: 'credentials.ts', start: 1, end: 3 },
      ],
    };
  }
  if (operation === 'create_database') {
    return 'Created the database';
  }
  if (operation === 'reload_working_copy') {
    return 'Merged working copy onto master';
  }
  if (operation === 'load_working_copy') {
    return 'Reloaded the working copy';
  }
  return 'ok';
}

function constrained(types: string[]) {
  if (types.length === 1 && types[0] === 'Module') {
    return { node_types: types, relationships: ['contains'], rules: ['module-rule'] };
  }
  if (types.length === 1 && types[0] === 'OoadClass') {
    return { node_types: types, relationships: ['owns'], rules: ['class-rule'] };
  }
  if (types.length === 1 && types[0] === 'Operation') {
    return { node_types: types, relationships: ['invokes'], rules: ['limit-operation-parameters'] };
  }
  return { node_types: types, relationships: ['contains', 'owns', 'invokes'], rules: ['module-rule', 'class-rule', 'limit-operation-parameters'] };
}

function rowsFor(practices: string[], types: string[]) {
  const trees = [];
  if (practices.length === 0 || practices.includes('clean_engineering')) {
    trees.push(engineeringTree);
  }
  if (practices.length === 0 || practices.includes('stories')) {
    trees.push(storiesTree);
  }
  const rows: { practice: string; type: string; name: string; node_id: string; ancestors: string[]; children: string[] }[] = [];
  const walk = (node: { type: string; name: string; node_id: string; children: typeof engineeringTree.children }, practice: string) => {
    const holder = node.type === node.name;
    if (!holder && node.type !== 'Practice' && (types.length === 0 || types.includes(node.type))) {
      rows.push({ practice, type: node.type, name: node.name, node_id: node.node_id, ancestors: [], children: [] });
    }
    for (const child of node.children) {
      walk(child, practice);
    }
  };
  if (trees.includes(engineeringTree)) {
    walk(engineeringTree, 'clean_engineering');
  }
  if (trees.includes(storiesTree)) {
    walk(storiesTree, 'stories');
  }
  return rows;
}
