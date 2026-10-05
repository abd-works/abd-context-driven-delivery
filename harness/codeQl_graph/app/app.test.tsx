import { act, cleanup, render, screen, waitFor, within } from '@testing-library/react';
import userEvent, { type UserEvent } from '@testing-library/user-event';
import { useLayoutEffect, useRef } from 'react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { App } from './App';
import { GraphView } from './graph/GraphView';
import { SourceView } from './source/SourceView';

const foldMarks = vi.hoisted(() => ({
  names: [] as string[],
  scrollbar: undefined as { handleMouseWheel?: boolean; alwaysConsumeMouseWheel?: boolean } | undefined,
}));

vi.mock('@monaco-editor/react', () => ({
  default: ({
    value,
    defaultValue,
    options,
    onMount,
  }: {
    value?: string;
    defaultValue?: string;
    options?: {
      scrollbar?: { handleMouseWheel?: boolean; alwaysConsumeMouseWheel?: boolean };
      lineNumbers?: (line: number) => string;
    };
    onMount?: (editor: {
      getValue: () => string;
      setValue: (next: string) => void;
      getModel: () => { getLineCount: () => number };
      getDomNode: () => HTMLElement;
      getTargetAtClientPoint: () => null;
      createDecorationsCollection: (next: { range: { startLineNumber: number }; options: { glyphMarginClassName?: string } }[]) => {
        set: (items: { range: { startLineNumber: number }; options: { glyphMarginClassName?: string } }[]) => void;
        clear: () => void;
      };
      setHiddenAreas: (ranges: { startLineNumber: number; endLineNumber: number }[]) => void;
    }) => void;
  }) => {
    const text = value ?? defaultValue ?? '';
    const host = useRef<HTMLDivElement>(null);
    const marks = useRef<{ range: { startLineNumber: number }; options: { glyphMarginClassName?: string } }[]>([]);
    const hidden = useRef<{ startLineNumber: number; endLineNumber: number }[]>([]);
    foldMarks.scrollbar = options?.scrollbar;
    const paint = () => {
      const editor = host.current;
      if (!editor) {
        return;
      }
      foldMarks.names = marks.current.flatMap((item) => (item.options.glyphMarginClassName ? [item.options.glyphMarginClassName] : []));
      editor.replaceChildren();
      text.split('\n').forEach((line, index) => {
        const lineNumber = index + 1;
        const shown = options?.lineNumbers?.(lineNumber) || String(lineNumber);
        const covered = hidden.current.some((range) => lineNumber >= range.startLineNumber && lineNumber <= range.endLineNumber);
        if (covered) {
          return;
        }
        const row = document.createElement('div');
        row.dataset.line = shown;
        for (const item of marks.current) {
          const className = item.options.glyphMarginClassName;
          if (item.range.startLineNumber === lineNumber && className) {
            const mark = document.createElement('span');
            mark.className = className;
            row.appendChild(mark);
          }
        }
        row.append(line);
        editor.appendChild(row);
      });
    };
    useLayoutEffect(() => {
      onMount?.({
        getValue: () => text,
        setValue: () => undefined,
        getModel: () => ({ getLineCount: () => text.split('\n').length }),
        getDomNode: () => host.current ?? document.body,
        getTargetAtClientPoint: () => null,
        createDecorationsCollection: (next) => {
          marks.current = next;
          paint();
          return {
            set: (items) => {
              marks.current = items;
              paint();
            },
            clear: () => {
              marks.current = [];
              paint();
            },
          };
        },
        setHiddenAreas: (ranges) => {
          hidden.current = ranges;
          paint();
        },
      });
    }, [onMount, text]);
    return <div ref={host} data-testid="source-editor" />;
  },
}));

const folder = 'C:\\dev\\example';
const registerText = 'register(input: Credentials) {\n  const account: AccountToken = input;\n  if (input) {\n    credentials.save();\n  }\n  credentials.notify();\n}';
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
            { type: 'EntityRoot', name: 'AccountCredentials', node_id: 'entity-account', children: [] },
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
const storyText = [
  "shareStory('Create Account', () => {",
  "  scenario('Create account', ({ when, then }) => {",
  "    when('the User creates their account', async () => {",
  '      accountCredentials.register();',
  '    });',
  "    then('the account is unconfirmed', () => {",
  '      expect(accountCredentials.verified).toBe(false);',
  '    });',
  '  });',
  '});',
].join('\n');
const scenarioText = [
  "scenario('Create account', ({ when, then }) => {",
  "  when('the User creates their account', async () => {",
  '    accountCredentials.register();',
  '  });',
  "  then('the account is unconfirmed', () => {",
  '    expect(accountCredentials.verified).toBe(false);',
  '  });',
  '});',
].join('\n');
const stepText = [
  "when('the User creates their account', async () => {",
  '  accountCredentials.register();',
  '  if (input) {',
  '    accountCredentials.notify();',
  '  }',
  '});',
].join('\n');
const storiesTree = {
  type: 'Practice',
  name: 'stories',
  node_id: 'stories',
  children: [
    {
      type: 'Epic',
      name: 'Onboard',
      node_id: 'epic-1',
      children: [
        {
          type: 'Story',
          name: 'Create Account',
          node_id: 'story-1',
          children: [
            {
              type: 'Scenario',
              name: 'Create account',
              node_id: 'scenario-1',
              children: [{ type: 'Step', name: 'when the User creates their account', node_id: 'step-1', children: [] }],
            },
          ],
        },
      ],
    },
  ],
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
  foldMarks.scrollbar = undefined;
  window.localStorage.clear();
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
  await waitFor(() => expect(editor.querySelector('.call-fold')).toBeTruthy());
  const line = (text: string) =>
    Array.from(editor.querySelectorAll<HTMLElement>('[data-line]')).find((row) => row.textContent?.includes(text));
  expect(line('credentials.save()')?.querySelector('.call-fold')).toBeTruthy();
  expect(line('credentials.notify()')?.querySelector('.call-fold')).toBeTruthy();
  expect(line('const account: AccountToken = input;')?.querySelector('.class-fold')).toBeTruthy();
  expect(line('if (input)')?.querySelector('.block-fold')).toBeTruthy();
  expect(editor.textContent).not.toContain('only-in-class-body');
  expect(foldMarks.scrollbar).toEqual({ handleMouseWheel: false, alwaysConsumeMouseWheel: false });
});

it('should number a step from its line in the file', async () => {
  render(
    <SourceView
      source={{
        node_id: 'when-load',
        name: 'when My Paradise loads the customer',
        type: 'Step',
        file: 'create_customer.story.shared.ts',
        text: "    when('My Paradise loads the customer', async () => {\n      customer = await ctx.customerRepository.load(accountCredentials);\n    });",
        start_line: 93,
        end_line: 95,
        members: [],
      }}
    />,
  );
  const editor = await screen.findByTestId('source-editor');
  const when = Array.from(editor.querySelectorAll<HTMLElement>('[data-line]')).find((row) =>
    row.textContent?.includes('loads the customer'),
  );
  expect(when?.dataset.line).toBe('93');
  expect(editor.textContent).not.toContain("then('the result");
});

it('should fold a story, a scenario, and a step the way a class folds', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await expand(user, 'stories');
  await expand(user, 'Onboard');
  await expand(user, 'Create Account');
  await user.click(screen.getByText('Create Account'));
  const editor = await screen.findByTestId('source-editor');
  const line = (text: string) =>
    Array.from(editor.querySelectorAll<HTMLElement>('[data-line]')).find((row) => row.textContent?.includes(text));
  await waitFor(() => expect(line("scenario('Create account'")?.querySelector('.block-fold')).toBeTruthy());
  expect(editor.textContent).not.toContain('accountCredentials.register');

  await expand(user, 'Create Account');
  await user.click(screen.getByText('Create account'));
  await waitFor(() => expect(line("when('the User creates their account'")?.querySelector('.block-fold')).toBeTruthy());
  expect(editor.textContent).not.toContain('accountCredentials.register');

  await expand(user, 'Create account');
  await user.click(screen.getByText('when the User creates their account'));
  await waitFor(() => expect(line('accountCredentials.register()')?.querySelector('.call-fold')).toBeTruthy());
  expect(line('if (input)')?.querySelector('.block-fold')).toBeTruthy();
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

it('should reload the last folder when the app opens', async () => {
  window.localStorage.setItem('cdd-graph-folder', folder);
  render(<App />);
  await screen.findByRole('button', { name: 'Expand clean_engineering' });
  expect((screen.getByTestId('chosen-folder') as HTMLInputElement).value).toBe(folder);
  expect(calls.some((call) => call.operation === 'load_working_copy' && call.body.folder === folder)).toBe(true);
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

it('should show invokes, observes, and demonstrates on a step', async () => {
  const user = userEvent.setup();
  const step = {
    type: 'Step',
    name: 'when the User enters valid account credentials',
    node_id: 'step-valid',
    children: [
      {
        type: 'scopes',
        name: 'scopes',
        node_id: 'scopes-valid',
        children: [{ type: 'Example', name: 'hiddenExample', node_id: 'hidden', children: [] }],
      },
      {
        type: 'invokes',
        name: 'invokes',
        node_id: 'invokes-valid',
        children: [{ type: 'Operation', name: 'register', node_id: 'op-register', children: [] }],
      },
      {
        type: 'observes',
        name: 'observes',
        node_id: 'observes-valid',
        children: [
          {
            type: 'Example',
            name: 'unverifiedAccountCredentials',
            node_id: 'example-unverified',
            children: [
              {
                type: 'demonstrates',
                name: 'demonstrates',
                node_id: 'demonstrates-account',
                children: [{ type: 'OoadClass', name: 'AccountCredentials', node_id: 'class-account', children: [] }],
              },
            ],
          },
        ],
      },
    ],
  };
  render(<GraphView trees={[step]} loading={false} error="" selectedId="" onSelect={() => undefined} />);
  await user.click(screen.getByRole('button', { name: 'Expand when the User enters valid account credentials' }));
  expect(document.querySelector('[data-node-id="scopes-valid"]')).toBeNull();
  expect(document.querySelector('[data-node-id="invokes-valid"]')).toBeTruthy();
  expect(document.querySelector('[data-node-id="observes-valid"]')).toBeTruthy();
  await user.click(screen.getByRole('button', { name: 'Expand observes' }));
  await user.click(screen.getByRole('button', { name: 'Expand unverifiedAccountCredentials' }));
  expect(document.querySelector('[data-node-id="demonstrates-account"]')).toBeTruthy();
  await user.click(screen.getByRole('button', { name: 'Expand demonstrates' }));
  expect(document.querySelector('[data-node-id="class-account"]')).toBeTruthy();
});

it('should create the database for the chosen folder', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.click(screen.getByTestId('create-database'));
  expect((await screen.findByTestId('work-progress')).textContent).toContain('Created the database');
  const created = calls.findIndex((call) => call.operation === 'create_database');
  expect(created).toBeGreaterThan(-1);
  expect(calls[created + 1]?.operation).toBe('load_working_copy');
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
    const nodeId = String(body.node_id);
    const storySource =
      nodeId === 'story-1'
        ? { name: 'Create Account', type: 'Story', file: 'authenticate_user.story.shared.ts', text: storyText }
        : nodeId === 'scenario-1'
          ? { name: 'Create account', type: 'Scenario', file: 'authenticate_user.story.shared.ts', text: scenarioText }
          : nodeId === 'step-1'
            ? { name: 'when the User creates their account', type: 'Step', file: 'authenticate_user.story.shared.ts', text: stepText }
            : { name: 'register', type: 'Operation', file: 'register.ts', text: registerText };
    return {
      node_id: body.node_id,
      name: storySource.name,
      type: storySource.type,
      file: storySource.file,
      text: storySource.text,
      start_line: 1,
      end_line: storySource.text.split('\n').length,
      members: [
        { id: 'op-1', name: 'register', kind: 'Operation', owner: 'AccountCredentials', text: registerText, file: 'register.ts', start: 1, end: 4 },
        { id: 'save', name: 'save', kind: 'Operation', owner: 'Credentials', text: 'save() {\n  stored();\n}', file: 'credentials.ts', start: 1, end: 3 },
        { id: 'notify', name: 'notify', kind: 'Operation', owner: 'Credentials', text: 'notify() {\n  sent();\n}', file: 'credentials.ts', start: 5, end: 7 },
        { id: 'class-c', name: 'Credentials', kind: 'OoadClass', owner: '', text: 'class Credentials {\n  token: string;\n}', file: 'credentials.ts', start: 1, end: 3 },
        { id: 'class-token', name: 'AccountToken', kind: 'OoadClass', owner: '', text: 'class AccountToken {\n  value: string;\n}', file: 'token.ts', start: 1, end: 3 },
        {
          id: 'class-account',
          name: 'AccountCredentials',
          kind: 'OoadClass',
          owner: '',
          text: 'class AccountCredentials {\n  token: AccountToken;\n  only-in-class-body();\n}',
          file: 'account.ts',
          start: 1,
          end: 4,
        },
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
