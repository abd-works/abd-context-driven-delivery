import { act, cleanup, render, screen, waitFor, within } from '@testing-library/react';
import userEvent, { type UserEvent } from '@testing-library/user-event';
import { useLayoutEffect, useRef } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from './App';
import { ExplorerTrees } from './graph/explorer-trees';
import { GraphView } from './graph/GraphView';
import type { ExplorerEntryData, NodeSourceData } from '@cdd/harness/graph/graph';
import { SourceView } from './source/SourceView';
import type { Monaco } from '@monaco-editor/react';
import { CallCatalog } from './source/call-expansion';
import type { SourceCallout } from './source/source-callouts';
import { FoldKeys, VS_CODE_FOLD_KEYS } from './source/source-folding';
import filterChoices from './filter-choices.json';

const foldMarks = vi.hoisted(() => ({
  names: [] as string[],
  scrollbar: undefined as { handleMouseWheel?: boolean; alwaysConsumeMouseWheel?: boolean } | undefined,
  wordWrap: undefined as string | undefined,
  scrollLeft: 0,
  // The fold actions run and commands triggered on the editor, in order.
  folding: [] as { command: string; args?: unknown }[],
  // The folding range providers and keybinding rules given to Monaco.
  providers: [] as { language: string; provider: { provideFoldingRanges: (model: { getLinesContent: () => string[] }) => unknown } }[],
  keybindings: [] as { keybinding: number; command: string }[],
  // The lines a closed fold hides, as Monaco keeps them while the page shows the file.
  hidden: [] as number[],
}));

// Monaco's own keys, as a chord of two parts and modifiers: the fake keeps each code as a plain number.
const fakeMonaco = vi.hoisted(() => ({
  KeyMod: { CtrlCmd: 2048, Shift: 1024, Alt: 512, WinCtrl: 256, chord: (first: number, second: number) => first * 65536 + second },
  KeyCode: { KeyK: 41, KeyJ: 40, KeyL: 42, KeyM: 43, Digit0: 21, Digit1: 22, Digit2: 23, Digit3: 24, Digit4: 25, Digit5: 26, Digit6: 27, Digit7: 28, BracketLeft: 92, BracketRight: 94, F9: 66, Slash: 90, Backslash: 93, Minus: 88, Equal: 86, Period: 89, Comma: 87, Semicolon: 85 },
  languages: { registerFoldingRangeProvider: (_language: string, _provider: unknown) => undefined as unknown },
  editor: { addKeybindingRules: (_rules: unknown[]) => undefined as unknown },
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
      wordWrap?: string;
      lineNumbers?: (line: number) => string;
    };
    onMount?: (editor: {
      getValue: () => string;
      setValue: (next: string) => void;
      getModel: () => { getLineCount: () => number; getLineMaxColumn: (line: number) => number };
      getDomNode: () => HTMLElement;
      getTargetAtClientPoint: () => null;
      createDecorationsCollection: (next: FakeMark[]) => {
        set: (items: FakeMark[]) => void;
        clear: () => void;
      };
      getAction: (id: string) => { run: () => Promise<void> };
      trigger: (source: string, handler: string, payload: unknown) => void;
      onDidContentSizeChange: (listener: (size: { contentHeight: number }) => void) => { dispose: () => void };
      getScrollLeft: () => number;
      setScrollLeft: (left: number) => void;
      onMouseDown: (listener: (event: { target: { element: Element | null; position: { lineNumber: number } | null } }) => void) => { dispose: () => void };
      changeViewZones: (
        change: (accessor: { addZone: (zone: FakeZone) => string; removeZone: (id: string) => void }) => void,
      ) => void;
    }, monaco: typeof fakeMonaco) => void;
  }) => {
    const text = value ?? defaultValue ?? '';
    const host = useRef<HTMLDivElement>(null);
    type Mark = FakeMark;
    // Each decorations collection the editor made keeps its own marks, as Monaco's do; every one paints.
    const collections = useRef<Mark[][]>([]);
    const marks = { get current(): Mark[] { return collections.current.flat(); } };
    const zones = useRef<Map<string, FakeZone>>(new Map());
    const presses = useRef<((event: { target: { element: Element | null; position: { lineNumber: number } | null } }) => void)[]>([]);
    foldMarks.scrollbar = options?.scrollbar;
    foldMarks.wordWrap = options?.wordWrap;
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
        const row = document.createElement('div');
        row.dataset.line = shown;
        for (const item of marks.current) {
          if (item.range.startLineNumber === lineNumber && item.options.isWholeLine && item.options.className) {
            row.className = item.options.className;
          }
        }
        for (const item of marks.current) {
          const className = item.options.glyphMarginClassName;
          if (item.range.startLineNumber === lineNumber && className) {
            const mark = document.createElement('span');
            mark.className = className;
            row.appendChild(mark);
          }
        }
        row.dataset.editorLine = String(lineNumber);
        row.append(line);
        for (const item of marks.current) {
          if (item.range.startLineNumber === lineNumber && item.options.after) {
            const label = document.createElement('span');
            label.className = item.options.after.inlineClassName ?? '';
            label.textContent = item.options.after.content;
            row.appendChild(label);
          }
        }
        editor.appendChild(row);
        for (const zone of zones.current.values()) {
          if (zone.afterLineNumber === lineNumber) {
            zone.domNode.style.height = `${shownHeightOf(zone, text)}px`;
            editor.appendChild(zone.domNode);
          }
        }
      });
    };
    const pressed = (event: MouseEvent) => {
      const element = event.target instanceof Element ? event.target : null;
      const row = element?.closest<HTMLElement>('[data-editor-line]');
      const position = row ? { lineNumber: Number(row.dataset.editorLine) } : null;
      presses.current.forEach((listener) => listener({ target: { element, position } }));
    };
    // Monaco calls onMount once, with one editor; the fake calls it again only when its text changes.
    const mounting = useRef(onMount);
    mounting.current = onMount;
    useLayoutEffect(() => {
      mounting.current?.({
        getValue: () => text,
        setValue: () => undefined,
        getModel: () => ({ getLineCount: () => text.split('\n').length, getLineMaxColumn: (line) => (text.split('\n')[line - 1] ?? '').length + 1 }),
        getDomNode: () => host.current ?? document.body,
        getTargetAtClientPoint: () => null,
        createDecorationsCollection: (next) => {
          const index = collections.current.push(next) - 1;
          paint();
          return {
            set: (items) => {
              collections.current[index] = items;
              paint();
            },
            clear: () => {
              collections.current[index] = [];
              paint();
            },
          };
        },
        onMouseDown: (listener) => {
          presses.current.push(listener);
          return { dispose: () => (presses.current = presses.current.filter((held) => held !== listener)) };
        },
        changeViewZones: (change) => {
          change({
            addZone: (zone) => {
              const id = `zone-${zones.current.size + 1}-${zone.afterLineNumber}`;
              zones.current.set(id, zone);
              return id;
            },
            removeZone: (id) => zones.current.delete(id),
          });
          paint();
        },
        getAction: (id) => ({ run: async () => void foldMarks.folding.push({ command: id }) }),
        trigger: (_source, handler, payload) => void foldMarks.folding.push({ command: handler, args: payload }),
        onDidContentSizeChange: () => ({ dispose: () => undefined }),
        // A line as wide as any scroll asks, so the editor scrolls as far as it is told, never left of its start.
        getScrollLeft: () => foldMarks.scrollLeft,
        setScrollLeft: (left) => {
          foldMarks.scrollLeft = Math.max(0, left);
        },
      }, fakeMonaco);
    }, [text]);
    return <div ref={host} data-testid="source-editor" onMouseDown={(event) => pressed(event.nativeEvent)} />;
  },
}));

type FakeZone = { afterLineNumber: number; afterColumn?: number; heightInPx?: number; domNode: HTMLElement };

// The height Monaco lays a view zone out at: none while the position just after it is hidden by a closed fold. A zone
// after a line's end is followed by the next line, so a fold closed under that line hides it; a zone after a column
// before the end is followed by the rest of its own line.
function shownHeightOf(zone: FakeZone, text: string): number {
  const lastColumn = (text.split('\n')[zone.afterLineNumber - 1] ?? '').length + 1;
  const followingLine = (zone.afterColumn ?? lastColumn) >= lastColumn ? zone.afterLineNumber + 1 : zone.afterLineNumber;
  return foldMarks.hidden.includes(followingLine) ? 0 : (zone.heightInPx ?? 0);
}

type FakeMark = {
  range: { startLineNumber: number };
  options: { glyphMarginClassName?: string; className?: string; isWholeLine?: boolean; after?: { content: string; inlineClassName?: string } };
};

const folder = 'C:\\dev\\example';
const overlayFolder = 'C:\\dev\\patterns\\lern_domain_driven';
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
                {
                  type: 'rules',
                  name: 'rules',
                  node_id: 'op-1:rules',
                  children: [
                    {
                      type: 'Rule',
                      name: 'limit-operation-parameters',
                      node_id: 'op-1:rules:limit-operation-parameters',
                      status: 'passing',
                      children: [],
                    },
                  ],
                },
              ],
            },
            {
              type: 'Operation',
              name: 'failure',
              node_id: 'op-failure',
              children: [
                {
                  type: 'rules',
                  name: 'rules',
                  node_id: 'op-failure:rules',
                  children: [
                    {
                      type: 'Rule',
                      name: 'limit-operation-parameters',
                      node_id: 'op-failure:rules:limit-operation-parameters',
                      status: 'violating',
                      violations: [
                        {
                          rule: 'limit-operation-parameters',
                          message: "Operation 'failure' takes 4 parameters (maximum 2).",
                          location: 'register.ts',
                          line: 1,
                          end_line: 2,
                        },
                      ],
                      children: [],
                    },
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

// Each fixture practice's node types, relationships, and rules are the ones Python's filter answers were recorded for.
const held = filterChoices.practices;
const inventory = {
  clean_engineering: { node_counts: { Module: 1, OoadClass: 2, Operation: 3 }, edge_count: 3, ...held.clean_engineering, tree: engineeringTree },
  ddd: { node_counts: { Aggregate: 2, EntityRoot: 2, Repository: 1, ValueObject: 2 }, edge_count: 4, ...held.ddd, tree: domainTree },
  stories: { node_counts: { Epic: 1 }, edge_count: 1, ...held.stories, tree: storiesTree },
};

const calls: { operation: string; body: Record<string, unknown> }[] = [];
let shownViolations = false;
let activeOverlays: string[] = [];
let reported = currentStaleness();

function inventoryBundle() {
  const practices =
    shownViolations
      ? {
          ...inventory,
          clean_engineering: { ...inventory.clean_engineering, tree: violationTree(engineeringTree) },
        }
      : inventory;
  return {
    practices,
    overlays: activeOverlays,
    available_overlays: ['lern_domain_driven'],
  };
}

beforeEach(() => {
  calls.length = 0;
  shownViolations = false;
  activeOverlays = [];
  reported = currentStaleness();
  foldMarks.names = [];
  foldMarks.scrollbar = undefined;
  foldMarks.folding = [];
  foldMarks.hidden = [];
  fakeMonaco.languages.registerFoldingRangeProvider = (language, provider) => foldMarks.providers.push({ language, provider: provider as (typeof foldMarks.providers)[number]['provider'] });
  fakeMonaco.editor.addKeybindingRules = (rules) => foldMarks.keybindings.push(...(rules as { keybinding: number; command: string }[]));
  window.localStorage.clear();
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      const operation = operationOf(url, init);
      const body = init?.body ? (JSON.parse(String(init.body)) as Record<string, unknown>) : {};
      calls.push({ operation, body });
      const payload = answer(operation, body);
      const serialized = JSON.stringify(payload);
      return {
        ok: true,
        text: async () => serialized,
        json: async () => payload,
      };
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

it('should read the entries a closed entry left out when it is opened', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await expand(user, 'clean_engineering');
  await expand(user, 'account');
  expect(calls.filter((call) => call.operation === 'explorer_branch').map((call) => call.body.node_id)).toEqual(['module-1']);
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

const rowOf = (editor: HTMLElement, text: string) =>
  Array.from(editor.querySelectorAll<HTMLElement>('[data-line]')).find((row) => row.textContent?.includes(text));

function press(target: Element | null | undefined): void {
  if (!target) throw new Error('nothing to press');
  act(() => void target.dispatchEvent(new MouseEvent('mousedown', { bubbles: true })));
}

async function openRegister(user: UserEvent): Promise<HTMLElement> {
  await openFolder(user);
  await expand(user, 'clean_engineering');
  await expand(user, 'account');
  await expand(user, 'AccountCredentials');
  await user.click(screen.getByText('register'));
  return screen.findByTestId('source-editor');
}

it('should label each call and class the code reaches, their lines closed', async () => {
  const user = userEvent.setup();
  const editor = await openRegister(user);
  await waitFor(() => expect(rowOf(editor, 'credentials.save()')?.querySelector('.callout-label')?.textContent).toBe(' ▸ Credentials.save'));
  expect(rowOf(editor, 'const account: AccountToken')?.querySelector('.callout-label')?.textContent).toBe(' ▸ AccountToken');
  expect(editor.querySelector('.callout-section')).toBeNull();
  expect(editor.textContent).not.toContain('only-in-class-body');
  expect(foldMarks.scrollbar).toMatchObject({ handleMouseWheel: false, alwaysConsumeMouseWheel: false });
});

it('should open a call in place with its label hidden, shaded once, and bring the label back when closed', async () => {
  const user = userEvent.setup();
  const editor = await openRegister(user);
  await waitFor(() => expect(rowOf(editor, 'credentials.save()')?.querySelector('.callout-mark')).toBeTruthy());
  press(rowOf(editor, 'credentials.save()')?.querySelector('.callout-mark'));
  await waitFor(() => expect(editor.querySelectorAll('.callout-section')).toHaveLength(1));
  const lines = Array.from(editor.querySelectorAll('.callout-section .callout-text')).map((row) => row.textContent);
  expect([lines, rowOf(editor, 'credentials.save()')?.querySelector('.callout-label')]).toEqual([['save() {', '  this.notify();', '}'], null]);
  press(rowOf(editor, 'credentials.save()')?.querySelector('.callout-mark'));
  await waitFor(() => expect(editor.querySelector('.callout-section')).toBeNull());
  expect(rowOf(editor, 'credentials.save()')?.querySelector('.callout-label')).toBeTruthy();
});

it('should open a call inside an open call, one shade deeper', async () => {
  const user = userEvent.setup();
  const editor = await openRegister(user);
  await waitFor(() => expect(rowOf(editor, 'credentials.save()')?.querySelector('.callout-mark')).toBeTruthy());
  press(rowOf(editor, 'credentials.save()')?.querySelector('.callout-mark'));
  await waitFor(() => expect(editor.querySelector('.callout-inner-mark')).toBeTruthy());
  press(editor.querySelector('.callout-inner-mark'));
  await waitFor(() => expect(editor.querySelector('.callout-section .callout-section')?.textContent).toBe('notify() {  sent();}'));
});

it('should open a call inside a method whose own block is still folded at its full height', async () => {
  const text = 'class AppServer:\n    def restart(self) -> bool:\n        if not self.stop():\n            return False\n        return True\n\n    def stop(self) -> bool:\n        return True';
  const member = (node_id: string, name: string, owner: string, start_line: number, end_line: number): NodeSourceData => ({ node_id, name, owner, type: owner ? 'Operation' : 'OoadClass', file: 'app.py', start_line, end_line, text: text.split('\n').slice(start_line - 1, end_line).join('\n'), members: [] });
  const appServer = { ...member('app-server', 'AppServer', '', 1, 8), members: [member('app-server', 'AppServer', '', 1, 8), member('restart', 'restart', 'AppServer', 2, 5), member('stop', 'stop', 'AppServer', 7, 8)] };
  foldMarks.hidden = [4];
  render(<SourceView source={appServer} violation={null} rules={[]} activeRule="" language="python" />);
  const editor = await screen.findByTestId('source-editor');
  await waitFor(() => expect(rowOf(editor, 'if not self.stop()')?.querySelector('.callout-mark')).toBeTruthy());
  press(rowOf(editor, 'if not self.stop()')?.querySelector('.callout-mark'));
  await waitFor(() => expect(editor.querySelector('.callout-section')?.textContent).toContain('def stop(self) -> bool:'));
  expect(editor.querySelector<HTMLElement>('.callout-block')?.style.height).toBe('40px');
});

it('should never open a class a comment or a docstring names', async () => {
  const app = { node_id: 'class-app', name: 'App', type: 'OoadClass', owner: '', text: 'class App:\n    pass', file: 'app.py', start_line: 1, end_line: 2, members: [] };
  const story = { ...longLine, node_id: 'story', file: 'explore.story.shared.py', text: '"""Explore Graph In Files App."""\n# App opens here\napp = App()', members: [app] };
  render(<SourceView source={story} violation={null} rules={[]} activeRule="" />);
  const editor = await screen.findByTestId('source-editor');
  await waitFor(() => expect(rowOf(editor, 'app = App()')?.querySelector('.callout-label')).toBeTruthy());
  expect([rowOf(editor, 'Explore Graph')?.querySelector('.callout-label'), rowOf(editor, '# App opens')?.querySelector('.callout-label')]).toEqual([null, null]);
});

it('should show the source code without the marks the graph puts after its calls', () => {
  const marked = { node_id: 'save', name: 'save', type: 'Operation', owner: 'Credentials', text: 'save() {\n  stored(); /* call:stored */\n}', file: 'credentials.ts', start_line: 1, end_line: 3, members: [] };
  const [callout] = new CallCatalog([marked]).calloutsIn({ file: '', startLine: 1, text: 'credentials.save();', language: 'typescript' });
  expect(callout.text).toBe('save() {\n  stored();\n}');
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
        owner: '',
        members: [],
      }}
      violation={null}
      rules={[]}
      activeRule=""
    />,
  );
  const editor = await screen.findByTestId('source-editor');
  expect(rowOf(editor, 'loads the customer')?.dataset.line).toBe('93');
  expect(editor.textContent).not.toContain("then('the result");
});

const longLine = {
  node_id: 'order',
  name: 'Order',
  type: 'OoadClass',
  file: 'order.py',
  text: `class Order:
    def place(self, cart: Cart) -> Order:
        raise EmptyCartError(cart.id, "${'a cart needs one item to be placed '.repeat(6)}")`,
  start_line: 1,
  end_line: 3,
  owner: '',
  members: [] as NodeSourceData[],
};

function turnWheel(editor: HTMLElement, wheel: WheelEventInit): WheelEvent {
  const event = new WheelEvent('wheel', { bubbles: true, cancelable: true, ...wheel });
  editor.dispatchEvent(event);
  return event;
}

it('should scroll a long line sideways when the wheel turns with shift held', async () => {
  foldMarks.scrollLeft = 0;
  render(<SourceView source={longLine} violation={null} rules={[]} activeRule="" />);
  const editor = await screen.findByTestId('source-editor');
  const wheel = turnWheel(editor, { deltaY: 120, shiftKey: true });
  expect([foldMarks.scrollLeft, wheel.defaultPrevented]).toEqual([120, true]);
});

it('should scroll a long line sideways when the Person swipes sideways', async () => {
  foldMarks.scrollLeft = 0;
  render(<SourceView source={longLine} violation={null} rules={[]} activeRule="" />);
  const editor = await screen.findByTestId('source-editor');
  turnWheel(editor, { deltaX: 80, deltaY: 4 });
  expect(foldMarks.scrollLeft).toBe(80);
});

it('should leave the wheel without shift to the page', async () => {
  foldMarks.scrollLeft = 0;
  render(<SourceView source={longLine} violation={null} rules={[]} activeRule="" />);
  const editor = await screen.findByTestId('source-editor');
  const wheel = turnWheel(editor, { deltaY: 120 });
  expect([foldMarks.scrollLeft, wheel.defaultPrevented]).toEqual([0, false]);
});

it('should leave long lines unwrapped until the page asks to wrap them', async () => {
  render(<SourceView source={longLine} violation={null} rules={[]} activeRule="" />);
  await screen.findByTestId('source-editor');
  expect(foldMarks.wordWrap).toBe('off');
});

it('should wrap long lines when the page asks', async () => {
  render(<SourceView source={longLine} violation={null} rules={[]} activeRule="" wordWrap />);
  await screen.findByTestId('source-editor');
  expect(foldMarks.wordWrap).toBe('on');
});

const storyMap = {
  node_id: '.context/story-map.md',
  name: 'story-map.md',
  type: 'File',
  file: '.context/story-map.md',
  text: '# Story Map\n\n(E) Manage Tickets\n    (S) Person --> [Delete Ticket](../story_tests/remove_tickets_story.test.md#story-delete-ticket)',
  start_line: 1,
  end_line: 4,
  owner: '',
  members: [],
};
const deleteTicketScenarios: SourceCallout = {
  id: 'story_tests/remove_tickets_story.test.md:3',
  kind: 'section',
  line: 4,
  title: 'Delete Ticket',
  path: 'story_tests/remove_tickets_story.test.md',
  startLine: 3,
  endLine: 9,
  text: '## Story: Delete Ticket\n\n#### Scenario: a ticket is deleted\n\n*Given* a ticket on the board\n*When* the Person deletes it\n*Then* the board no longer shows it',
};

it('should mark and label a line whose link opens another file, its section closed', async () => {
  render(<SourceView source={storyMap} violation={null} rules={[]} activeRule="" language="markdown" keepGlyphMargin callouts={[deleteTicketScenarios]} />);
  const editor = await screen.findByTestId('source-editor');
  await waitFor(() => expect(editor.querySelector('[data-line="4"] .callout-mark')).toBeTruthy());
  expect([editor.querySelector('[data-line="4"] .callout-label')?.textContent, editor.querySelector('.callout-section')]).toEqual([' ▸ Delete Ticket', null]);
});

it('should open the linked section under its line in place of its label, naming its file only in its tooltip', async () => {
  render(<SourceView source={storyMap} violation={null} rules={[]} activeRule="" language="markdown" keepGlyphMargin callouts={[deleteTicketScenarios]} />);
  const editor = await screen.findByTestId('source-editor');
  await waitFor(() => expect(editor.querySelector('.callout-mark')).toBeTruthy());
  press(editor.querySelector('[data-line="4"] .callout-label'));
  await waitFor(() => expect(editor.querySelector('.callout-section')).toBeTruthy());
  const section = editor.querySelector<HTMLElement>('.callout-section');
  const lines = Array.from(section?.querySelectorAll('.callout-text') ?? []).map((row) => row.textContent);
  expect([lines, section?.title, editor.querySelector('.callout-label')]).toEqual([deleteTicketScenarios.text.split('\n'), 'Delete Ticket: story_tests/remove_tickets_story.test.md lines 3 to 9', null]);
});

it('should close the linked section and bring its label back when its mark is pressed again', async () => {
  render(<SourceView source={storyMap} violation={null} rules={[]} activeRule="" language="markdown" keepGlyphMargin callouts={[deleteTicketScenarios]} />);
  const editor = await screen.findByTestId('source-editor');
  await waitFor(() => expect(editor.querySelector('.callout-mark')).toBeTruthy());
  press(editor.querySelector('[data-line="4"] .callout-mark'));
  await waitFor(() => expect(editor.querySelector('.callout-section')).toBeTruthy());
  press(editor.querySelector('[data-line="4"] .callout-mark'));
  await waitFor(() => expect(editor.querySelector('.callout-section')).toBeNull());
  expect(editor.querySelector('[data-line="4"] .callout-label')).toBeTruthy();
});

function markedLines(editor: HTMLElement): string[] {
  return Array.from(editor.querySelectorAll<HTMLElement>('[data-line].selected-lines')).map((row) => row.dataset.line ?? '');
}

it('should mark the lines of the node the page asks to show', async () => {
  render(<SourceView source={longLine} violation={null} rules={[]} activeRule="" openAround={[{ start: 2, end: 3 }]} />);
  const editor = await screen.findByTestId('source-editor');
  await waitFor(() => expect(markedLines(editor)).toEqual(['2', '3']));
});

it('should mark no lines for a node that covers the whole file', async () => {
  render(<SourceView source={longLine} violation={null} rules={[]} activeRule="" openAround={[{ start: 1, end: 3 }]} />);
  const editor = await screen.findByTestId('source-editor');
  await screen.findAllByText(/class Order/);
  expect(markedLines(editor)).toEqual([]);
});

it("should fold everything with Monaco's Fold All, then unfold every fold around the lines asked to show", async () => {
  render(<SourceView source={longLine} violation={null} rules={[]} activeRule="" openAround={[{ start: 2, end: 3 }]} />);
  await screen.findByTestId('source-editor');
  await waitFor(() =>
    expect(foldMarks.folding).toEqual([{ command: 'editor.foldAll' }, { command: 'editor.unfold', args: { selectionLines: [1], direction: 'up', levels: 100 } }]),
  );
});

it('should leave the folds as the person left them when no lines are asked to show', async () => {
  render(<SourceView source={longLine} violation={null} rules={[]} activeRule="" />);
  await screen.findByTestId('source-editor');
  expect(foldMarks.folding).toEqual([]);
});

it('should fold markdown by its headings, a heading in a code block being none', async () => {
  render(<SourceView source={storyMap} violation={null} rules={[]} activeRule="" language="markdown" />);
  await screen.findByTestId('source-editor');
  const markdown = foldMarks.providers.find((each) => each.language === 'markdown');
  const lines = ['# A', '', '## B', 'text', '', '## C', '```', '# not', '```', 'x'];
  expect(markdown?.provider.provideFoldingRanges({ getLinesContent: () => lines })).toEqual([
    { start: 1, end: 10 },
    { start: 3, end: 4 },
    { start: 6, end: 10 },
  ]);
});

const monacoApi = fakeMonaco as unknown as Monaco;
const chordOf = (first: number, second: number) => fakeMonaco.KeyMod.chord(fakeMonaco.KeyMod.CtrlCmd | first, fakeMonaco.KeyMod.CtrlCmd | second);

it("should bind VS Code's fold chords when no keybindings file says otherwise", () => {
  foldMarks.keybindings = [];
  FoldKeys.VS_CODE.bindIn(monacoApi);
  expect(foldMarks.keybindings).toContainEqual({ keybinding: chordOf(fakeMonaco.KeyCode.KeyK, fakeMonaco.KeyCode.Digit0), command: 'editor.foldAll' });
});

it('should bind the key a keybindings file gives a fold command in place of VS Code', () => {
  foldMarks.keybindings = [];
  const keys = FoldKeys.from('[{ "key": "ctrl+m ctrl+m", "command": "editor.toggleFold" }]').bindIn(monacoApi);
  const toggles = foldMarks.keybindings.filter((rule) => rule.command === 'editor.toggleFold');
  expect([keys.problem, toggles]).toEqual(['', [{ keybinding: chordOf(fakeMonaco.KeyCode.KeyM, fakeMonaco.KeyCode.KeyM), command: 'editor.toggleFold' }]]);
});

it("should keep VS Code's keys and say why when a keybindings file is no list of fold commands", () => {
  const keys = [FoldKeys.from('{ "editor.foldAll": "ctrl+m" }'), FoldKeys.from('[{ "key": "ctrl+m", "command": "workbench.action.quit" }]'), FoldKeys.from('[{')];
  expect(keys.map((each) => [each.keys === VS_CODE_FOLD_KEYS, each.problem.length > 0])).toEqual([
    [true, true],
    [true, true],
    [true, true],
  ]);
});

it('should bind a key with shift, and a function key, as a keybindings file writes them', () => {
  foldMarks.keybindings = [];
  FoldKeys.from('[{ "key": "f9", "command": "editor.toggleFold" }]').bindIn(monacoApi);
  expect(foldMarks.keybindings).toEqual(expect.arrayContaining([
    { keybinding: fakeMonaco.KeyMod.CtrlCmd | fakeMonaco.KeyMod.Shift | fakeMonaco.KeyCode.BracketLeft, command: 'editor.fold' },
    { keybinding: fakeMonaco.KeyCode.F9, command: 'editor.toggleFold' },
  ]));
});

it("should keep VS Code's keys and say why when a keybindings file names a key Monaco has none for", () => {
  const keys = FoldKeys.from('[{ "key": "hyper+q", "command": "editor.foldAll" }]').bindIn(monacoApi);
  expect([keys.keys, keys.problem]).toEqual([VS_CODE_FOLD_KEYS, 'no key Monaco knows in {"key":"hyper+q","command":"editor.foldAll"}']);
});

it("should open the calls of a step in place", async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await expand(user, 'stories');
  await expand(user, 'Onboard');
  await expand(user, 'Create Account');
  await expand(user, 'Create account');
  await user.click(screen.getByText('when the User creates their account'));
  const editor = await screen.findByTestId('source-editor');
  await waitFor(() => expect(rowOf(editor, 'accountCredentials.register()')?.querySelector('.callout-label')?.textContent).toBe(' ▸ AccountCredentials.register'));
});

it('should select every node, connector, and rule for the practice', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.selectOptions(screen.getByTestId('filter-practice'), ['clean_engineering']);
  await waitFor(() => expect(chosen('filter-node')).toEqual(['Module', 'OoadClass', 'Operation']));
  expect(options('filter-node')).toEqual(['Module', 'OoadClass', 'Operation']);
  expect(chosen('filter-connector')).toEqual(['contains', 'owns', 'invokes']);
  expect(options('filter-connector')).toEqual(['contains', 'owns', 'invokes']);
  // conforms-to-schema is the framework's rule, so every node type has it beside its practice's own rules.
  expect(chosen('filter-rule')).toEqual([
    'clean_engineering.Module.conforms-to-schema',
    'clean_engineering.Module.module-rule',
    'clean_engineering.OoadClass.class-rule',
    'clean_engineering.OoadClass.conforms-to-schema',
    'clean_engineering.Operation.conforms-to-schema',
    'clean_engineering.Operation.limit-operation-parameters',
  ]);
});

it('should keep the first practice filters when another practice is added', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.selectOptions(screen.getByTestId('filter-practice'), ['clean_engineering']);
  await waitFor(() => expect(chosen('filter-node')).toContain('OoadClass'));
  pickOnly('filter-node', ['Module']);
  await waitFor(() => expect(chosen('filter-connector')).toEqual(['contains']));
  await user.selectOptions(screen.getByTestId('filter-practice'), ['clean_engineering', 'stories']);
  // The practices are offered in the order the approach walks them, stories first.
  await waitFor(() => expect(chosen('filter-practice')).toEqual(['stories', 'clean_engineering']));
  await waitFor(() => expect(chosen('filter-node')).toEqual(['Epic', 'Module']));
  expect(options('filter-node')).toEqual(['Epic', 'Module', 'OoadClass', 'Operation']);
  expect(chosen('filter-connector')).toEqual(['tells', 'contains']);
  expect(chosen('filter-rule')).toEqual([
    'clean_engineering.Module.conforms-to-schema',
    'clean_engineering.Module.module-rule',
    'stories.Epic.conforms-to-schema',
    'stories.Epic.verb-noun',
  ]);
  const asked = calls.filter((call) => call.operation === 'filter_choices').at(-1);
  expect(asked?.body).toMatchObject({ node_types: ['Module'], practices_before: ['clean_engineering'] });
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
  const filtered = calls.filter((call) => call.operation === 'explorer_trees').at(-1);
  expect(filtered?.body.filter).toMatchObject({ types: ['Operation'] });
});

it('should put the chosen folder on the page and show its classes', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  expect((screen.getByTestId('chosen-folder') as HTMLInputElement).value).toBe(folder);
  await expand(user, 'clean_engineering');
  await expand(user, 'account');
  expect(screen.getByText('AccountCredentials')).toBeTruthy();
  expect(calls.map((call) => call.operation).filter((operation) => operation !== 'progress')).toEqual([
    'choose_folder',
    'practice_names',
    'load_working_copy',
    'inventory',
    'filter_choices',
    'explorer_trees',
    'explorer_branch',
  ]);
});

it('should show the backend traceback instead of loading forever', async () => {
  window.localStorage.setItem('cdd-graph-folder', folder);
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      const operation = operationOf(url, init);
      const body = init?.body ? (JSON.parse(String(init.body)) as Record<string, unknown>) : {};
      calls.push({ operation, body });
      if (operation === 'load_working_copy') {
        const payload = {
          error: 'No working copy for stories.',
          diagnosis:
            'I just encountered an error doing load_working_copy on C:\\repo. Please diagnose and fix.\n\nTraceback (most recent call last):\n  File "host.py", line 1, in handle\nQueryFailure: missing',
        };
        const serialized = JSON.stringify(payload);
        return { ok: false, text: async () => serialized, json: async () => payload };
      }
      const payload = answer(operation, body);
      const serialized = JSON.stringify(payload);
      return { ok: true, text: async () => serialized, json: async () => payload };
    }),
  );
  render(<App />);
  const error = await screen.findByTestId('scan-error');
  expect(error.textContent).toContain('I just encountered an error doing load_working_copy');
  expect(error.textContent).toContain('Please diagnose and fix');
  expect(error.textContent).toContain('Traceback (most recent call last)');
  expect(screen.getByRole('button', { name: 'Copy for AI' })).toBeTruthy();
  expect(screen.queryByTestId('extraction-progress')).toBeNull();
});

it('should list rules as practice, node, then rule', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  expect(options('filter-rule')).toEqual([
    'clean_engineering.Module.conforms-to-schema',
    'clean_engineering.Module.module-rule',
    'clean_engineering.OoadClass.class-rule',
    'clean_engineering.OoadClass.conforms-to-schema',
    'clean_engineering.Operation.conforms-to-schema',
    'clean_engineering.Operation.limit-operation-parameters',
    'ddd.Aggregate.conforms-to-schema',
    'ddd.BoundedContext.conforms-to-schema',
    'ddd.EntityRoot.conforms-to-schema',
    'ddd.Repository.conforms-to-schema',
    'ddd.ValueObject.conforms-to-schema',
    'stories.Epic.conforms-to-schema',
    'stories.Epic.verb-noun',
  ]);
});

it('should force a reload from the top right of the page', async () => {
  const user = userEvent.setup();
  window.localStorage.setItem('cdd-graph-folder', folder);
  render(<App />);
  await screen.findByRole('button', { name: 'Expand clean_engineering' });
  calls.length = 0;
  await user.click(screen.getByRole('button', { name: 'Force reload' }));
  await waitFor(() =>
    expect(calls.some((call) => call.operation === 'load_working_copy' && call.body.force === true)).toBe(true),
  );
});

it('should reload the last folder when the app opens', async () => {
  window.localStorage.setItem('cdd-graph-folder', folder);
  render(<App />);
  await screen.findByRole('button', { name: 'Expand clean_engineering' });
  expect((screen.getByTestId('chosen-folder') as HTMLInputElement).value).toBe(folder);
  expect(calls.some((call) => call.operation === 'load_working_copy' && call.body.folder === folder)).toBe(true);
});

it('should load the session path a link names in place of the last folder', async () => {
  window.localStorage.setItem('cdd-graph-folder', 'C:/last/folder');
  window.history.replaceState(null, '', `/?folder=${encodeURIComponent(folder)}`);
  try {
    render(<App />);
    await screen.findByRole('button', { name: 'Expand clean_engineering' });
    expect(calls.some((call) => call.operation === 'load_working_copy' && call.body.folder === folder)).toBe(true);
  } finally {
    window.history.replaceState(null, '', '/');
  }
});

it('should start with the source pane asking for a node', () => {
  render(<App />);
  expect(screen.getByText('Select a node')).toBeTruthy();
});

it('should offer built-in overlay names from the catalog', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  expect(screen.getByTestId('overlay-catalog')).toBeTruthy();
  expect(screen.getByTestId('overlay-add-lern_domain_driven')).toBeTruthy();
});

it('should offer an overlay folder picker between practice and node filters', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  expect(screen.getByTestId('overlay-add')).toBeTruthy();
  expect(screen.getByText(/No active overlay/i)).toBeTruthy();
});

it('should apply overlays through the api when a folder is chosen', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.click(screen.getByTestId('overlay-add'));
  await waitFor(() =>
    expect(calls.some((call) => call.operation === 'overlay_of')).toBe(true),
  );
  await waitFor(() =>
    expect(
      calls.some(
        (call) => call.operation === 'set_overlays' && (call.body.overlays as string[]).includes(overlayFolder),
      ),
    ).toBe(true),
  );
  expect(screen.getByTestId('overlay-list').textContent).toMatch(/Lern domain driven|lern_domain_driven/i);
});

it('should take an overlay applied from its folder out of the catalog', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.click(screen.getByTestId('overlay-add'));
  await waitFor(() => expect(screen.getByTestId('overlay-remove-lern_domain_driven')).toBeTruthy());
  expect(screen.queryByTestId('overlay-add-lern_domain_driven')).toBeNull();
});

it('should take an overlay applied by its name out of the catalog', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.click(screen.getByTestId('overlay-add-lern_domain_driven'));
  await waitFor(() => expect(activeOverlays).toEqual(['lern_domain_driven']));
  await waitFor(() => expect(screen.queryByTestId('overlay-add-lern_domain_driven')).toBeNull());
});

it('should remove an overlay when its remove control is clicked', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.click(screen.getByTestId('overlay-add'));
  await waitFor(() => expect(activeOverlays).toContain(overlayFolder));
  await user.click(screen.getByTestId('overlay-remove-lern_domain_driven'));
  await waitFor(() =>
    expect(calls.some((call) => call.operation === 'set_overlays' && (call.body.overlays as string[]).length === 0)).toBe(
      true,
    ),
  );
});

it('should send violations when the switch is turned on', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.click(screen.getByRole('button', { name: 'Violations' }));
  await waitFor(() =>
    expect(calls.some((call) => call.operation === 'explorer_trees' && (call.body.filter as { violations: boolean }).violations)).toBe(true),
  );
});

it('should show a passing rule and a violating rule under the operation', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await expand(user, 'clean_engineering');
  await expand(user, 'account');
  await expand(user, 'AccountCredentials');
  await expand(user, 'register');
  await user.click(screen.getAllByTestId('tree-expand-rules')[0]);
  const passing = document.querySelector('.rule-status.passing');
  expect(passing?.textContent).toContain('limit-operation-parameters');
  await expand(user, 'failure');
  const rules = screen.getAllByTestId('tree-expand-rules');
  await user.click(rules[rules.length - 1]);
  const violating = document.querySelector('.rule-status.violating');
  expect(violating?.textContent).toContain('limit-operation-parameters');
});

it('should keep the violation attached when violations are filtered', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await user.click(screen.getByRole('button', { name: 'Violations' }));
  await expand(user, 'clean_engineering');
  await expand(user, 'account');
  await expand(user, 'AccountCredentials');
  expect(screen.queryByRole('button', { name: 'Expand register' })).toBeNull();
  await expand(user, 'failure');
  await user.click(screen.getByTestId('tree-expand-rules'));
  expect(document.querySelector('.rule-status.violating')?.textContent).toContain('limit-operation-parameters');
  expect(document.querySelector('.rule-status.passing')).toBeNull();
});

it('should expose the violation message when hovering a violating rule', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await expand(user, 'clean_engineering');
  await expand(user, 'account');
  await expand(user, 'AccountCredentials');
  await expand(user, 'failure');
  await user.click(screen.getByTestId('tree-expand-rules'));
  expect(screen.getByTestId('tree-violation-rule').getAttribute('title')).toBe(
    "Operation 'failure' takes 4 parameters (maximum 2).",
  );
});

it('should show the violation banner, highlight the source, and say Fix this one was not sent with no chat to send it to', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  await expand(user, 'clean_engineering');
  await expand(user, 'account');
  await expand(user, 'AccountCredentials');
  await expand(user, 'failure');
  await user.click(screen.getByTestId('tree-expand-rules'));
  await user.click(screen.getByTestId('tree-violation-rule'));
  const banner = await screen.findByTestId('violation-banner');
  expect(banner.textContent).toContain('limit-operation-parameters');
  expect(banner.textContent).toContain('takes 4 parameters (maximum 2)');
  expect(calls.some((call) => call.operation === 'source' && call.body.node_id === 'op-failure')).toBe(true);
  const listed = await screen.findByTestId('source-rules');
  expect(listed.textContent).toContain('limit-operation-parameters');
  const editor = await screen.findByTestId('source-editor');
  await waitFor(() => expect(editor.querySelector('.violation-highlight')).toBeTruthy());
  await user.click(screen.getByTestId('violation-fix-one'));
  expect((await screen.findByTestId('violation-fix-one-outcome')).textContent).toBe('Not sent');
});

// Fix this one hands the page the broken place to fix, which Python writes the words of, and shows on the banner what the
// page answered.
it('should hand Fix this one the rule, the place, its node, and its lines, and show that it was sent', async () => {
  const one = vi.fn().mockResolvedValue({ isSent: true, words: 'Sent to chat' });
  const user = userEvent.setup();
  const place = { message: "Operation 'failure' takes 4 parameters (maximum 2).", startLine: 2, endLine: 3 };
  render(<SourceView source={longLine} violation={{ rule: 'limit-operation-parameters', places: [place] }} rules={[]} activeRule="" fixes={{ one }} />);
  await user.click(screen.getByTestId('violation-fix-one'));
  expect(one).toHaveBeenCalledWith({ rule: 'limit-operation-parameters', place, nodeId: longLine.node_id, startLine: 2, endLine: 3 });
  const outcome = await screen.findByTestId('violation-fix-one-outcome');
  expect(outcome.textContent).toBe('Sent to chat');
  expect(outcome.className).toContain('is-sent');
});

it('should show that Fix this one was not sent when the page answers so', async () => {
  const user = userEvent.setup();
  const violation = { rule: 'limit-operation-parameters', places: [{ message: 'Too many parameters.', startLine: 2, endLine: 3 }] };
  render(<SourceView source={longLine} violation={violation} rules={[]} activeRule="" fixes={{ one: async () => ({ isSent: false, words: 'Not sent' }) }} />);
  await user.click(screen.getByTestId('violation-fix-one'));
  const outcome = await screen.findByTestId('violation-fix-one-outcome');
  expect(outcome.textContent).toBe('Not sent');
  expect(outcome.className).toContain('is-failed');
});

describe('a broken rule at two places, on a page that fixes a whole rule', () => {
  const violation = { rule: 'limit-operation-parameters', places: [{ message: 'First.', startLine: 1, endLine: 1 }, { message: 'Second.', startLine: 2, endLine: 3 }] };

  it('should offer Fix this one on each place', () => {
    render(<SourceView source={longLine} violation={violation} rules={[]} activeRule="" fixes={{ one: vi.fn(), rule: vi.fn() }} />);
    expect(screen.getAllByTestId('violation-fix-one')).toHaveLength(2);
  });

  it('should hand Fix this one the place it was pressed on', async () => {
    const one = vi.fn().mockResolvedValue({ isSent: true, words: 'Sent to chat' });
    const user = userEvent.setup();
    render(<SourceView source={longLine} violation={violation} rules={[]} activeRule="" fixes={{ one, rule: vi.fn() }} />);
    await user.click(screen.getAllByTestId('violation-fix-one')[1]!);
    expect(one).toHaveBeenCalledWith(expect.objectContaining({ place: violation.places[1], startLine: 2, endLine: 3 }));
  });

  it('should hand Fix rule the rule', async () => {
    const rule = vi.fn().mockResolvedValue({ isSent: true, words: 'Sent to chat' });
    const user = userEvent.setup();
    render(<SourceView source={longLine} violation={violation} rules={[]} activeRule="" fixes={{ one: vi.fn(), rule }} />);
    await user.click(screen.getByTestId('violation-fix-rule'));
    expect(rule).toHaveBeenCalledWith('limit-operation-parameters');
  });
});

it('should show invokes, observes, and demonstrates on a step', async () => {
  const user = userEvent.setup();
  const step = {
    type: 'Step',
    name: 'when the User enters valid account credentials',
    node_id: 'step-valid',
    children: [
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
  render(<GraphView trees={new ExplorerTrees([step] as unknown as ExplorerEntryData[])} loading={false} error="" selectedId="" activeRule="" onSelect={() => undefined} onOpenBranch={async () => undefined} />);
  await user.click(screen.getByRole('button', { name: 'Expand when the User enters valid account credentials' }));
  expect(document.querySelector('[data-node-id="invokes-valid"]')).toBeTruthy();
  expect(document.querySelector('[data-node-id="observes-valid"]')).toBeTruthy();
  await user.click(screen.getByRole('button', { name: 'Expand observes' }));
  await user.click(screen.getByRole('button', { name: 'Expand unverifiedAccountCredentials' }));
  expect(document.querySelector('[data-node-id="demonstrates-account"]')).toBeTruthy();
  await user.click(screen.getByRole('button', { name: 'Expand demonstrates' }));
  expect(document.querySelector('[data-node-id="class-account"]')).toBeTruthy();
});

it('should show each load step while the graph is loading', async () => {
  let polled = 0;
  let release: (value: unknown) => void = () => undefined;
  const gate = new Promise((resolve) => {
    release = resolve;
  });
  window.localStorage.setItem('cdd-graph-folder', folder);
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      const operation = operationOf(url, init);
      const body = init?.body ? (JSON.parse(String(init.body)) as Record<string, unknown>) : {};
      calls.push({ operation, body });
      if (operation === 'load_working_copy') {
        await gate;
      }
      if (operation === 'progress') {
        const steps = ['Reading classes', 'Recording stories'];
        const payload = [{ tool: 'graph.load_working_copy', message: steps[Math.min(polled++, steps.length - 1)] }];
        const serialized = JSON.stringify(payload);
        return { ok: true, text: async () => serialized, json: async () => payload };
      }
      const payload = answer(operation, body);
      const serialized = JSON.stringify(payload);
      return { ok: true, text: async () => serialized, json: async () => payload };
    }),
  );
  render(<App />);
  const log = await screen.findByTestId('loading-log');
  expect(log.textContent).toContain('Reading classes');
  await waitFor(() => expect(log.textContent).toContain('Recording stories'));
  expect(screen.getByTestId('extraction-progress').textContent).toContain('Recording stories');
  release(undefined);
  await screen.findByRole('button', { name: 'Expand clean_engineering' });
});

async function openFolder(user: UserEvent) {
  render(<App />);
  await user.click(screen.getByTestId('working-folder'));
  await screen.findByRole('button', { name: 'Expand clean_engineering' });
}

// Opens an entry and waits for the branch the page reads for it.
async function expand(user: UserEvent, name: string) {
  const shut = screen.queryByRole('button', { name: `Expand ${name}` });
  if (shut) {
    await user.click(shut);
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });
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

// The operation a request names: the graph's tool, the explorer's folder dialog, or the progress of the running calls.
function operationOf(url: string, init?: RequestInit): string {
  const last = String(url).split('/').pop() ?? '';
  if (last === 'choose-folder' && init?.body && String(init.body).includes('overlay')) {
    return 'choose_folder';
  }
  return last.replace(/-/g, '_');
}

function answer(operation: string, body: Record<string, unknown>): unknown {
  if (operation === 'choose_folder') {
    return { folder: String(body.title).includes('overlay') ? overlayFolder : folder };
  }
  if (operation === 'overlay_of') {
    return { overlay: body.folder };
  }
  if (operation === 'inventory') {
    return inventoryBundle();
  }
  if (operation === 'practice_names') {
    return ['stories', 'ddd', 'ux', 'clean_engineering', 'bdd'];
  }
  if (operation === 'set_overlays') {
    activeOverlays = Array.isArray(body.overlays) ? (body.overlays as string[]) : [];
    return inventoryBundle();
  }
  if (operation === 'filter_choices') {
    return choicesFor((body.practices as string[]) ?? [], (body.node_types as string[]) ?? [], (body.practices_before as string[] | null | undefined) ?? null);
  }
  if (operation === 'explorer_trees') {
    const picked = body.filter as { practices?: string[]; types?: string[]; violations?: boolean };
    shownViolations = Boolean(picked.violations);
    return treesFor(picked.practices ?? [], picked.types ?? [], shownViolations).map(opened);
  }
  if (operation === 'explorer_branch') {
    const picked = body.filter as { practices?: string[]; types?: string[]; violations?: boolean };
    const trees = treesFor(picked.practices ?? [], picked.types ?? [], Boolean(picked.violations));
    const home = trees.flatMap((tree) => [...walked(tree)]).find((entry) => entry.node_id === body.node_id && entry.children.length > 0);
    return home ? opened(home) : null;
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
        { node_id: 'op-1', name: 'register', type: 'Operation', owner: 'AccountCredentials', text: registerText, file: 'register.ts', start_line: 1, end_line: 4 },
        { node_id: 'save', name: 'save', type: 'Operation', owner: 'Credentials', text: 'save() {\n  this.notify();\n}', file: 'credentials.ts', start_line: 1, end_line: 3 },
        { node_id: 'notify', name: 'notify', type: 'Operation', owner: 'Credentials', text: 'notify() {\n  sent();\n}', file: 'credentials.ts', start_line: 5, end_line: 7 },
        { node_id: 'class-c', name: 'Credentials', type: 'OoadClass', owner: '', text: 'class Credentials {\n  token: string;\n}', file: 'credentials.ts', start_line: 1, end_line: 3 },
        { node_id: 'class-token', name: 'AccountToken', type: 'OoadClass', owner: '', text: 'class AccountToken {\n  value: string;\n}', file: 'token.ts', start_line: 1, end_line: 3 },
        {
          node_id: 'class-account',
          name: 'AccountCredentials',
          type: 'OoadClass',
          owner: '',
          text: 'class AccountCredentials {\n  token: AccountToken;\n  only-in-class-body();\n}',
          file: 'account.ts',
          start_line: 1,
          end_line: 4,
        },
      ],
    };
  }
  if (operation === 'load_working_copy') {
    return { message: 'Reloaded the working copy' };
  }
  if (operation === 'progress') {
    return [];
  }
  if (operation === 'staleness') {
    return reported;
  }
  if (operation === 'serialize_graph_cache') {
    return 'Serialized the graph cache';
  }
  return 'ok';
}

function comparison(older: boolean, dates: Record<string, string>) {
  return { older, practice: 'stories', dates };
}

function currentStaleness() {
  return {
    master_stale: {
      older_than_worktree: comparison(false, { master: '2026-10-08T00:00:00+00:00', worktree: '2026-10-08T00:00:00+00:00' }),
      older_than_code: comparison(false, { master: '2026-10-08T00:00:00+00:00', code: '2026-10-08T00:00:00+00:00' }),
    },
    worktree_stale: {
      older_than_code: comparison(false, { worktree: '2026-10-08T00:00:00+00:00', code: '2026-10-08T00:00:00+00:00' }),
      older_than_master: comparison(false, { worktree: '2026-10-08T00:00:00+00:00', master: '2026-10-08T00:00:00+00:00' }),
    },
    graph_cache_stale: {
      older_than_worktree: comparison(false, { graph_cache: '2026-10-08T00:00:00+00:00', worktree: '2026-10-08T00:00:00+00:00' }),
      older_than_master: comparison(false, { graph_cache: '2026-10-08T00:00:00+00:00', master: '2026-10-08T00:00:00+00:00' }),
      older_than_code: comparison(false, { graph_cache: '2026-10-08T00:00:00+00:00', code: '2026-10-08T00:00:00+00:00' }),
    },
    dates: {
      graph_cache: '2026-10-08T00:00:00+00:00',
      practices: [{ practice: 'stories', master: '2026-10-08T00:00:00+00:00', worktree: '2026-10-08T00:00:00+00:00', code: '2026-10-08T00:00:00+00:00' }],
    },
  };
}

function staleMaster() {
  const report = currentStaleness();
  report.master_stale.older_than_code = comparison(true, { master: '2026-01-01T00:00:00+00:00', code: '2026-10-08T00:00:00+00:00' });
  report.worktree_stale.older_than_master = comparison(true, { worktree: '2026-01-01T00:00:00+00:00', master: '2026-10-08T00:00:00+00:00' });
  report.graph_cache_stale.older_than_worktree = comparison(true, {
    graph_cache: '2026-01-02T00:00:00+00:00',
    worktree: '2026-10-08T00:00:00+00:00',
  });
  return report;
}

// Graph.filter_choices as Python answers it, for the fixture graph's practices: filter_choices_record.py records
// Python's answer to each request in filter-choices.json, so these tests hold no copy of the rule. A request with no
// recorded answer fails, naming itself, until it is added there and recorded.
function choicesFor(practices: string[], nodeTypes: string[], before: string[] | null) {
  const request = { practices, node_types: nodeTypes, practices_before: before };
  const found = filterChoices.answers.find((entry) => JSON.stringify(entry.request) === JSON.stringify(request));
  if (!found) {
    throw new Error(`no answer Python recorded for graph.filter_choices ${JSON.stringify(request)}: add it to filter-choices.json and run filter_choices_record.py`);
  }
  return found.answer;
}

function violationTree(node: Entry): Entry | null {
  const children = node.children.map((child) => violationTree(child)).filter((child): child is Entry => Boolean(child));
  if (node.type === 'Rule') {
    return node.status === 'violating' ? { ...node, children } : null;
  }
  if (node.type === 'rules') {
    return children.length > 0 ? { ...node, children } : null;
  }
  return { ...node, children };
}

// An explorer tree item as the fixtures write it: an entry, a rules collection, or a rule with its status.
type Entry = { type: string; name: string; node_id: string; children: Entry[]; status?: string; children_left_out?: number };

// An entry as Python's explorer answers send it: the entries below it, each closed, keeping its rules and counting the
// entries it left out, which explorer_branch answers.
function opened(entry: Entry): Entry {
  return { ...entry, children: entry.children.map((child) => (child.type === 'rules' ? child : closed(child))), children_left_out: 0 };
}

function closed(entry: Entry): Entry {
  const rules = entry.children.filter((child) => child.type === 'rules');
  return { ...entry, children: rules, children_left_out: entry.children.length - rules.length };
}

function* walked(entry: Entry): Generator<Entry> {
  yield entry;
  for (const child of entry.children) yield* walked(child);
}

// Graph.explorer_trees as Python answers it: each named practice's tree, every practice's when none is named, keeping
// its root, the nodes the filter matches with their rules, and the nodes on the way to them.
function treesFor(practices: string[], types: string[], violations: boolean): Entry[] {
  const matched = new Set(rowsFor(practices, types, violations).map((row) => row.node_id));
  const loaded = inventoryBundle().practices as Record<string, { tree: Entry | null }>;
  const shown = practices.length ? practices : Object.keys(loaded);
  return shown.map((name) => loaded[name]?.tree && keptBy(loaded[name].tree!, matched)).filter((tree): tree is Entry => Boolean(tree));
}

function keptBy(node: Entry, matched: Set<string>): Entry | null {
  const rules = node.children.filter((child) => child.type === 'rules');
  const entries = node.children
    .filter((child) => child.type !== 'rules')
    .map((child) => keptBy(child, matched))
    .filter((child): child is Entry => child !== null);
  if (node.type === 'Practice' || matched.has(node.node_id)) {
    return { ...node, children: [...entries, ...rules] };
  }
  return entries.length > 0 ? { ...node, children: entries } : null;
}

function rowsFor(practices: string[], types: string[], violations = false) {
  const trees: Record<string, Entry> = { clean_engineering: engineeringTree, ddd: domainTree, stories: storiesTree };
  const rows: { practice: string; type: string; name: string; node_id: string; ancestors: string[]; children: string[] }[] = [];
  const walk = (node: Entry, practice: string) => {
    const holder = node.type === node.name;
    const violating = (node.children ?? []).some(
      (child) => child.name === 'rules' && (child.children ?? []).some((hit) => hit.status === 'violating'),
    );
    if (
      !holder &&
      node.type !== 'Practice' &&
      node.type !== 'rules' &&
      node.type !== 'Rule' &&
      (types.length === 0 || types.includes(node.type)) &&
      (!violations || violating)
    ) {
      rows.push({ practice, type: node.type, name: node.name, node_id: node.node_id, ancestors: [], children: [] });
    }
    for (const child of node.children) {
      walk(child, practice);
    }
  };
  for (const [practice, tree] of Object.entries(trees)) {
    if (practices.length === 0 || practices.includes(practice)) {
      walk(tree, practice);
    }
  }
  return rows;
}

// B10: a node whose source the graph cannot give, or a source read that fails, says so in the source pane.
function answeringSource(answerFor: () => { ok: boolean; payload: unknown }) {
  const answered = vi.mocked(fetch);
  const every = answered.getMockImplementation()!;
  answered.mockImplementation(async (url, init) => {
    if (operationOf(String(url), init) !== 'source') return every(url, init);
    const { ok, payload } = answerFor();
    const serialized = JSON.stringify(payload);
    return { ok, status: ok ? 200 : 500, text: async () => serialized, json: async () => payload } as Response;
  });
}

it('should say a node has no source the graph can show', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  answeringSource(() => ({ ok: true, payload: null }));
  await expand(user, 'clean_engineering');
  await expand(user, 'account');
  await user.click(screen.getByText('AccountCredentials'));
  expect(await screen.findByText('The graph holds no source for this node. Load the folder again if it should.')).toBeTruthy();
});

it('should say why reading a source failed', async () => {
  const user = userEvent.setup();
  await openFolder(user);
  answeringSource(() => ({ ok: false, payload: { error: 'graph.source is still running after 10 seconds' } }));
  await expand(user, 'clean_engineering');
  await expand(user, 'account');
  await user.click(screen.getByText('AccountCredentials'));
  expect(await screen.findByText(/The source did not open: .*still running after 10 seconds/)).toBeTruthy();
});
