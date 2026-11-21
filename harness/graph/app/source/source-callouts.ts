import type { editor as monaco } from 'monaco-editor';
import { useEffect, useState } from 'react';

// What opens in place under a line: a section another file holds, which a markdown link names (a story map's story opens
// its scenarios, a scenario's domain term its class in the markdown model), or a call or class the line's code reaches,
// or a story test's step invokes or observes, in this file or another. A link to a file or a heading that is not there
// is missing: it opens only its text, which says what is not there. link is the target a markdown link writes.
export type SourceCallout = {
  id: string;
  kind: 'section' | 'call' | 'class' | 'example' | 'missing';
  line: number;
  title: string;
  link?: string;
  path: string;
  startLine: number;
  endLine: number;
  text: string;
};

// The callouts a callout's own lines hold, a call inside an operation opened in place; none for a section.
export type CalloutsWithin = (callout: SourceCallout, stack: string[]) => SourceCallout[];

const CALLOUT_MARK = 'callout-mark';
const CALLOUT_LABEL = 'callout-label';
const CALLOUT_INNER_MARK = 'callout-inner-mark';
export const LINE_HEIGHT = 20;
const LINE_END = Number.MAX_SAFE_INTEGER;

type CalloutEditor = Pick<monaco.IStandaloneCodeEditor, 'createDecorationsCollection' | 'onMouseDown' | 'changeViewZones' | 'getModel' | 'getDomNode'>;

// The callout each open section shows, so a right-click over one finds it.
const calloutOfSection = new WeakMap<Element, SourceCallout>();

// The callouts of the open file. While a line's callouts are closed, a mark beside it and a label after it name what
// they open; a press on either opens them under the line and hides the label, and a press on the mark closes them and
// brings the label back. An open callout shows only its lines, shaded once, its file and lines in its tooltip; a line
// inside it that holds callouts of its own carries a mark that opens them inside it, one shade deeper. Each opens in a
// view zone, which adds no line to the file, so comments, rules and folds stay on the file's own lines. The callouts on
// the lines expand names open as well, as the page asks. With goTo, right-clicking an open callout offers Go to file,
// which opens what it shows in its own file.
export function useCallouts(editor: CalloutEditor | null, callouts: SourceCallout[], within: CalloutsWithin, editorLineOf: (fileLine: number) => number, expand: number[] = [], goTo?: GoToFile): void {
  const [open, setOpen] = useState<string[]>([]);
  const expandedKeys = expand.filter((line) => callouts.some((callout) => callout.line === line)).map(lineKey).join(' ');
  useEffect(() => {
    if (expandedKeys) setOpen((current) => [...new Set([...current, ...expandedKeys.split(' ')])]);
  }, [expandedKeys]);
  const toggle = (key: string) => setOpen((current) => (current.includes(key) ? current.filter((held) => held !== key) : [...current, key]));
  const lines = [...new Set(callouts.map((callout) => callout.line))];
  useEffect(() => {
    if (!editor || !callouts.length) return;
    const marks = editor.createDecorationsCollection(lines.map((line) => markOf(callouts.filter((each) => each.line === line), editorLineOf(line), open.includes(lineKey(line)))));
    return () => marks.clear();
  }, [editor, callouts, open, editorLineOf]);
  useEffect(() => {
    if (!editor || !callouts.length) return;
    const pressing = editor.onMouseDown((event) => {
      const pressed = event.target.element instanceof Element ? event.target.element : null;
      const line = event.target.position?.lineNumber;
      if (!line || !pressed?.closest(`.${CALLOUT_MARK}, .${CALLOUT_LABEL}`)) return;
      const fileLine = lines.find((each) => editorLineOf(each) === line);
      if (fileLine !== undefined) toggle(lineKey(fileLine));
    });
    return () => pressing.dispose();
  }, [editor, callouts, editorLineOf]);
  useEffect(() => {
    if (!editor) return;
    const zones: string[] = [];
    editor.changeViewZones((accessor) => {
      for (const line of lines.filter((each) => open.includes(lineKey(each)))) {
        const shown = calloutsBlock(callouts.filter((each) => each.line === line), lineKey(line), { open, toggle, within, goTo }, []);
        const afterLineNumber = editorLineOf(line);
        zones.push(accessor.addZone({ afterLineNumber, afterColumn: lastCharacterOf(editor, afterLineNumber), heightInPx: shown.rows * LINE_HEIGHT, domNode: shown.node }));
      }
    });
    return () => editor.changeViewZones((accessor) => zones.forEach((zone) => accessor.removeZone(zone)));
  }, [editor, callouts, open, within, editorLineOf, goTo]);
  useGoToMenu(editor, goTo);
  useLinkPresses(editor, callouts, editorLineOf, goTo);
}

// The callout whose link, as the line writes it, holds column: `[Cart](../domain-model.md#cart)` from its first bracket
// to its last; none for a callout that is no link's, or a link that names something not there.
export function linkCalloutAt(callouts: SourceCallout[], lineText: string, column: number): SourceCallout | undefined {
  return callouts.find((callout) => {
    if (!callout.link || callout.kind === 'missing') return false;
    const written = `[${callout.title}](${callout.link})`;
    const start = lineText.indexOf(written);
    return start >= 0 && start < column && column <= start + written.length + 1;
  });
}

// A press on a link with Ctrl or Cmd held follows it, as an editor follows a link: the file it names opens at the
// section its callout holds.
function useLinkPresses(editor: CalloutEditor | null, callouts: SourceCallout[], editorLineOf: (fileLine: number) => number, goTo?: GoToFile): void {
  useEffect(() => {
    if (!editor || !goTo || !callouts.some((callout) => callout.link)) return;
    const pressing = editor.onMouseDown((event) => {
      const at = event.target.position;
      if (!at || !(event.event.ctrlKey || event.event.metaKey)) return;
      const onLine = callouts.filter((callout) => editorLineOf(callout.line) === at.lineNumber);
      const followed = linkCalloutAt(onLine, editor.getModel()?.getLineContent(at.lineNumber) ?? '', at.column);
      if (!followed) return;
      event.event.preventDefault();
      // Once Monaco has finished with the press: opening the file takes this editor away.
      setTimeout(() => goTo(followed), 0);
    });
    return () => pressing.dispose();
  }, [editor, callouts, editorLineOf, goTo]);
}

const lineKey = (line: number): string => `L${line}`;

// Where a callout's lines are, as its tooltip says it; for a missing one, what is not there.
export const calloutPlace = (callout: SourceCallout): string => (callout.kind === 'missing' ? `${callout.title}: ${callout.text}` : `${callout.title}: ${callout.path} lines ${callout.startLine} to ${callout.endLine}`);

// The column of a line's last character, which a callout opens after. Monaco shows a zone only while the position just
// after it shows: after a line's end that is the next line, which a fold closed under the line hides, as a call's `if`
// block stays folded once the method around it unfolds; after its last character it is the line's own end.
function lastCharacterOf(editor: CalloutEditor, line: number): number | undefined {
  const lineEnd = editor.getModel()?.getLineMaxColumn(line) ?? 1;
  return lineEnd > 1 ? lineEnd - 1 : undefined;
}

function markOf(callouts: SourceCallout[], line: number, isOpen: boolean): monaco.IModelDeltaDecoration {
  const named = callouts.map((callout) => callout.title).join(', ');
  // The label sits after the line's last character: Monaco keeps a column past it at the line's end.
  return {
    range: { startLineNumber: line, startColumn: LINE_END, endLineNumber: line, endColumn: LINE_END },
    options: {
      glyphMarginClassName: `${CALLOUT_MARK}${isOpen ? ' callout-mark-open' : ''}`,
      glyphMarginHoverMessage: { value: callouts.map(calloutPlace).join('\n\n') },
      after: isOpen ? undefined : { content: ` ▸ ${named}`, inlineClassName: CALLOUT_LABEL },
    },
  };
}

// Opens what a callout shows in its own file, as Go to file on it asks.
export type GoToFile = (callout: SourceCallout) => void;

type Opening = { open: string[]; toggle: (key: string) => void; within: CalloutsWithin; goTo?: GoToFile };

// The open callouts of one line, one after another, each shaded once; a line inside one whose code holds callouts of its
// own carries a mark, and those callouts open below that line, inside it. Answers the block and how many rows it takes.
function calloutsBlock(callouts: SourceCallout[], key: string, opening: Opening, stack: string[]): { node: HTMLElement; rows: number } {
  const block = document.createElement('div');
  block.className = 'callout-block';
  let rows = 0;
  callouts.forEach((callout, index) => {
    const shown = calloutSection(callout, `${key}>${index}`, opening, [...stack, callout.id]);
    block.append(shown.node);
    rows += shown.rows;
  });
  return { node: block, rows };
}

function calloutSection(callout: SourceCallout, key: string, opening: Opening, stack: string[]): { node: HTMLElement; rows: number } {
  const section = document.createElement('div');
  section.className = `callout-section callout-${callout.kind}`;
  section.title = calloutPlace(callout);
  calloutOfSection.set(section, callout);
  const inner = opening.within(callout, stack);
  let rows = 0;
  callout.text.split('\n').forEach((text, index) => {
    const fileLine = callout.startLine + index;
    const here = inner.filter((each) => each.line === fileLine);
    section.append(calloutRow(text, here.length ? `${key}:${fileLine}` : '', here, opening));
    rows += 1;
    if (!here.length || !opening.open.includes(`${key}:${fileLine}`)) return;
    const nested = calloutsBlock(here, `${key}:${fileLine}`, opening, stack);
    section.append(nested.node);
    rows += nested.rows;
  });
  return { node: section, rows };
}

const CALLOUT_MENU = 'callout-menu';

// A right-click over an open callout shows Go to file for the innermost one under the pointer. The editor's text layer
// lies over the callouts, so the click reaches the editor, not the callout: the editor's own node hears it first, before
// Monaco's menu does, and finds the callout beneath the pointer.
function useGoToMenu(editor: CalloutEditor | null, goTo: GoToFile | undefined): void {
  useEffect(() => {
    const root = editor?.getDomNode();
    if (!root || !goTo) return;
    const onContextMenu = (event: MouseEvent) => {
      const under = document.elementsFromPoint(event.clientX, event.clientY).find((element) => calloutOfSection.has(element));
      const callout = under ? calloutOfSection.get(under) : undefined;
      if (!callout || callout.kind === 'missing') return;
      event.preventDefault();
      event.stopPropagation();
      showGoToMenu(event.clientX, event.clientY, () => goTo(callout));
    };
    root.addEventListener('contextmenu', onContextMenu, true);
    return () => root.removeEventListener('contextmenu', onContextMenu, true);
  }, [editor, goTo]);
}

// The menu a right-click on a callout opens where the pointer is: Go to file, which closes it, as a press anywhere else
// or Escape does.
function showGoToMenu(x: number, y: number, goTo: () => void): void {
  const backdrop = document.createElement('div');
  backdrop.className = `${CALLOUT_MENU}-backdrop`;
  const menu = document.createElement('div');
  menu.className = CALLOUT_MENU;
  menu.setAttribute('role', 'menu');
  menu.style.left = `${x}px`;
  menu.style.top = `${y}px`;
  const item = document.createElement('button');
  item.type = 'button';
  item.setAttribute('role', 'menuitem');
  item.textContent = 'Go to file';
  const close = () => {
    backdrop.remove();
    menu.remove();
    document.removeEventListener('keydown', onKey);
  };
  const onKey = (event: KeyboardEvent) => {
    if (event.key === 'Escape') close();
  };
  item.addEventListener('click', () => {
    close();
    goTo();
  });
  backdrop.addEventListener('mousedown', close);
  backdrop.addEventListener('contextmenu', (event) => {
    event.preventDefault();
    close();
  });
  document.addEventListener('keydown', onKey);
  menu.append(item);
  document.body.append(backdrop, menu);
}

function calloutRow(text: string, key: string, inner: SourceCallout[], opening: Opening): HTMLElement {
  const row = document.createElement('div');
  row.className = 'callout-text';
  if (key) {
    const mark = document.createElement('button');
    mark.type = 'button';
    mark.className = `${CALLOUT_INNER_MARK}${opening.open.includes(key) ? ' callout-mark-open' : ''}`;
    mark.title = inner.map((callout) => callout.title).join(', ');
    mark.addEventListener('mousedown', (event) => {
      event.preventDefault();
      event.stopPropagation();
      opening.toggle(key);
    });
    row.append(mark);
  }
  row.append(text);
  return row;
}
