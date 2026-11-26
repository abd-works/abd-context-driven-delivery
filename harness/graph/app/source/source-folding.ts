import type { Monaco } from '@monaco-editor/react';
import type { editor as monaco } from 'monaco-editor';
import { useEffect } from 'react';

// Lines of the source a page wants shown, such as the nodes a person selected in the graph: every fold holding one of
// them opens, and every other fold closes.
export type SourceLines = { start: number; end: number };

// One shortcut, as VS Code's and Cursor's keybindings.json write it: `{ "key": "ctrl+k ctrl+0", "command": "editor.foldAll" }`.
export type FoldKey = { key: string; command: string };

type FoldEditor = Pick<monaco.IStandaloneCodeEditor, 'getAction' | 'trigger'>;

const HEADING = /^(#{1,6})\s/;
const FENCE = /^\s*(```|~~~)/;
// The folds a selected node opens up from: every fold around its first line, however deep.
const EVERY_LEVEL = 100;

// Where each markdown heading's section runs: from its heading to the line before the next heading of its level or
// above, a heading in a code block being no heading.
function headingRanges(lines: string[]): SourceLines[] {
  const open: { level: number; start: number }[] = [];
  const ranges: SourceLines[] = [];
  const close = (level: number, end: number) => {
    while (open.length && open[open.length - 1].level >= level) {
      const held = open.pop()!;
      if (end > held.start) ranges.push({ start: held.start, end });
    }
  };
  let fenced = false;
  lines.forEach((line, index) => {
    fenced = FENCE.test(line) ? !fenced : fenced;
    const level = fenced ? 0 : (HEADING.exec(line)?.[1].length ?? 0);
    if (!level) return;
    close(level, lastWritten(lines, index));
    open.push({ level, start: index + 1 });
  });
  close(1, lastWritten(lines, lines.length));
  return ranges.sort((left, right) => left.start - right.start);
}

// The last line before index that is not blank, so a section folds without the blank lines before the next heading.
function lastWritten(lines: string[], index: number): number {
  let line = index;
  while (line > 0 && !lines[line - 1].trim()) line -= 1;
  return line;
}

const folded = new WeakSet<object>();

// Markdown folds by its headings, as an IDE folds it: Monaco folds code by its own reading of the language, and
// markdown by nothing but region markers, so each Monaco a page loads is given this one provider, once.
export function foldMarkdownHeadings(monacoApi: Monaco): void {
  if (folded.has(monacoApi)) return;
  folded.add(monacoApi);
  monacoApi.languages.registerFoldingRangeProvider('markdown', {
    provideFoldingRanges: (model: monaco.ITextModel) => headingRanges(model.getLinesContent()),
  });
}

// A decorator line, such as a Python story test's `@s.given("a ticket on the board")` above its step's function.
const DECORATOR_LINE = /^\s*@/;

// The lines, from 1, whose folds open for the lines asked to show: each node's first line, and, when that line is a
// decorator, the first line of what it decorates, so a step or an operation written under its decorators shows its
// own body, not only the folds around it.
export function linesToUnfold(text: string, openAround: SourceLines[]): number[] {
  const lines = text.split(/\r?\n/);
  const unfold = openAround.flatMap(({ start, end }) => {
    const decorated = lines.slice(start - 1, end).findIndex((line) => !DECORATOR_LINE.test(line));
    return decorated > 0 ? [start, start + decorated] : [start];
  });
  return [...new Set(unfold)];
}

// The folds around the lines asked to show open, each node's own fold with them (linesToUnfold), and every other fold
// closes, as Monaco's own Fold All and Unfold with its levels up do; with no lines asked, the folds stay as the person
// left them.
export function useOpenAround(editor: FoldEditor | null, openAround: SourceLines[], text: string): void {
  const key = openAround.map((lines) => `${lines.start}-${lines.end}`).join(',');
  useEffect(() => {
    if (!editor || !openAround.length) return;
    void (async () => {
      await editor.getAction('editor.foldAll')?.run();
      editor.trigger('source-view', 'editor.unfold', { selectionLines: linesToUnfold(text, openAround).map((line) => line - 1), direction: 'up', levels: EVERY_LEVEL });
    })();
  }, [editor, key, text]);
}

// VS Code's fold shortcuts, which Monaco binds too: what a page binds when no keybindings file says otherwise.
export const VS_CODE_FOLD_KEYS: FoldKey[] = [
  { key: 'ctrl+k ctrl+0', command: 'editor.foldAll' },
  { key: 'ctrl+k ctrl+j', command: 'editor.unfoldAll' },
  { key: 'ctrl+k ctrl+[', command: 'editor.foldRecursively' },
  { key: 'ctrl+k ctrl+]', command: 'editor.unfoldRecursively' },
  { key: 'ctrl+k ctrl+l', command: 'editor.toggleFold' },
  { key: 'ctrl+shift+[', command: 'editor.fold' },
  { key: 'ctrl+shift+]', command: 'editor.unfold' },
  ...[1, 2, 3, 4, 5, 6, 7].map((level) => ({ key: `ctrl+k ctrl+${level}`, command: `editor.foldLevel${level}` })),
];

// The commands a keybindings file may bind: Monaco's fold actions.
const FOLD_COMMANDS = new Set([...VS_CODE_FOLD_KEYS.map((each) => each.command), 'editor.foldAllExcept', 'editor.unfoldAllExcept', 'editor.toggleFoldRecursively', 'editor.foldAllBlockComments']);

// The fold shortcuts a page binds: VS Code's, each replaced by the key a keybindings file gives its command. A file that
// is not a list of keys and fold commands, or names a key Monaco has no code for, keeps VS Code's and says why.
export class FoldKeys {
  private constructor(
    readonly keys: FoldKey[],
    readonly problem: string,
  ) {}

  static readonly VS_CODE = new FoldKeys(VS_CODE_FOLD_KEYS, '');

  static from(json: string): FoldKeys {
    try {
      const given: unknown = JSON.parse(json);
      if (!Array.isArray(given)) return FoldKeys.fromFailure('it is not a list of { "key", "command" }');
      const wrong = given.find((each) => typeof each?.key !== 'string' || !FOLD_COMMANDS.has(each?.command));
      if (wrong !== undefined) return FoldKeys.fromFailure(`${JSON.stringify(wrong)} binds no fold command (${[...FOLD_COMMANDS].join(', ')})`);
      const chosen = given as FoldKey[];
      return new FoldKeys([...VS_CODE_FOLD_KEYS.filter((each) => !chosen.some((held) => held.command === each.command)), ...chosen], '');
    } catch (failure) {
      return FoldKeys.fromFailure(failure instanceof Error ? failure.message : String(failure));
    }
  }

  static fromFailure(why: string): FoldKeys {
    return new FoldKeys(VS_CODE_FOLD_KEYS, why);
  }

  // Binds each key in the Monaco the page loaded, for every editor in it. A key Monaco has no code for is refused.
  bindIn(monacoApi: Monaco): FoldKeys {
    const rules = this.keys.map((each) => ({ keybinding: keybindingOf(monacoApi, each.key), command: each.command }));
    const unknown = rules.find((rule) => rule.keybinding === 0);
    if (unknown) return FoldKeys.fromFailure(`no key Monaco knows in ${JSON.stringify(this.keys[rules.indexOf(unknown)])}`).bindIn(monacoApi);
    monacoApi.editor.addKeybindingRules(rules);
    return this;
  }
}

// The keybinding Monaco reads for a key such as `ctrl+k ctrl+0`: each chord part its modifiers and its key; 0 when a
// key is none Monaco has.
function keybindingOf(monacoApi: Monaco, key: string): number {
  const parts = key.trim().toLowerCase().split(/\s+/).map((part) => chordPartOf(monacoApi, part));
  if (!parts.length || parts.length > 2 || parts.includes(0)) return 0;
  return parts.length === 2 ? monacoApi.KeyMod.chord(parts[0], parts[1]) : parts[0];
}

function chordPartOf(monacoApi: Monaco, part: string): number {
  const names = part.split('+');
  const code = keyCodeOf(monacoApi, names.pop() ?? '');
  const mods = { ctrl: monacoApi.KeyMod.CtrlCmd, cmd: monacoApi.KeyMod.CtrlCmd, shift: monacoApi.KeyMod.Shift, alt: monacoApi.KeyMod.Alt, meta: monacoApi.KeyMod.WinCtrl, win: monacoApi.KeyMod.WinCtrl };
  const known = names.every((name) => name in mods);
  return code && known ? names.reduce((sum, name) => sum | mods[name as keyof typeof mods], code) : 0;
}

function keyCodeOf(monacoApi: Monaco, name: string): number {
  const codes = monacoApi.KeyCode;
  const punctuation: Record<string, number> = { '[': codes.BracketLeft, ']': codes.BracketRight, '/': codes.Slash, '\\': codes.Backslash, '-': codes.Minus, '=': codes.Equal, '.': codes.Period, ',': codes.Comma, ';': codes.Semicolon };
  if (name in punctuation) return punctuation[name];
  const written = /^[a-z]$/.test(name) ? `Key${name.toUpperCase()}` : /^\d$/.test(name) ? `Digit${name}` : /^f\d{1,2}$/.test(name) ? name.toUpperCase() : '';
  return (written && (codes as unknown as Record<string, number>)[written]) || 0;
}
