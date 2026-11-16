import Editor, { type OnMount } from '@monaco-editor/react';
import type { editor as monaco } from 'monaco-editor';
import { useLayoutEffect, useMemo, useRef, useState } from 'react';
import { initialOpenFolds, inlineCallLayout, type FoldMember, type InlineFold } from './call-expansion';
import type { NodeSourceData } from '@cdd/harness/graph/graph';
import { buildViolationCorrectPrompt, type ViolationFocus } from './violation-prompt';
import { reasonOf } from '../graph/graph-failures';
import { failures } from '../graph/graph-page';
import './source.css';

const LINE_HEIGHT = 20;

type Decoration = monaco.IModelDeltaDecoration;
type Decorations = { current: monaco.IEditorDecorationsCollection | null };

export type SourceRule = {
  name: string;
  status?: string;
  messages: string[];
};

export type SourceEditorInstance = Parameters<OnMount>[0];

// A fold a page names on the source's own lines, such as a class or operation the session's graph places in a whole
// file.
export type SourceFold = { start: number; end: number; kind: 'class' | 'block' };

// Lines of the source a page wants shown, such as the nodes a person selected in the graph: every fold holding one of
// them starts open, and every other fold starts closed.
export type SourceLines = { start: number; end: number };

// What a page showing a whole file adds to the view: the folds its graph names, whether every fold starts open so the
// file reads whole until a person folds it, the language the file is in, and the editor itself once it is made, so the
// page can add its own gutter marks (each with the class SOURCE_MARK, which the fold toggle leaves alone) and menu
// actions, such as the Files app's comments; and whether long lines wrap, or scroll sideways (shift+wheel or a sideways
// swipe, since the page, not the editor, scrolls up and down).
export type SourceHostProps = {
  folds?: SourceFold[];
  unfolded?: boolean;
  openAround?: SourceLines[];
  language?: string;
  keepGlyphMargin?: boolean;
  wordWrap?: boolean;
  onEditor?: (editor: SourceEditorInstance) => void;
};

export const SOURCE_MARK = 'source-mark';

const NO_FOLDS: SourceFold[] = [];
const NO_LINES: SourceLines[] = [];

type SourceViewProps = SourceHostProps & {
  source: NodeSourceData | null;
  // Why there is no source to show for a selected node; empty while no node is selected.
  note?: string;
  violation: ViolationFocus | null;
  rules: SourceRule[];
  activeRule: string;
  onSelectRule?: (name: string) => void;
};

export function SourceView({ source, note = '', violation, rules = [], activeRule = '', onSelectRule = () => undefined, ...host }: SourceViewProps) {
  return (
    <div className="panel" data-testid="source-file">
      {source ? (
        <SourceEditor source={source} violation={violation} rules={rules} activeRule={activeRule} onSelectRule={onSelectRule} {...host} />
      ) : (
        <p className="empty-state">{note || 'Select a node'}</p>
      )}
    </div>
  );
}

function SourceEditor({
  source,
  violation,
  rules,
  activeRule,
  onSelectRule,
  folds = NO_FOLDS,
  unfolded = false,
  openAround = NO_LINES,
  language = '',
  keepGlyphMargin = false,
  wordWrap = false,
  onEditor,
}: SourceHostProps & {
  source: NodeSourceData;
  violation: ViolationFocus | null;
  rules: SourceRule[];
  activeRule: string;
  onSelectRule?: (name: string) => void;
}) {
  const file = source.file ?? '';
  const text = source.text ?? '';
  const markStart = violation?.startLine ?? source.start_line;
  const markEnd = violation?.endLine ?? source.end_line;
  const members = source.members ?? [];
  const owner = members.find((member) => member.node_id === source.node_id)?.owner ?? '';
  const prepared = useMemo(
    () =>
      withNamedFolds(
        inlineCallLayout(text, members, owner, {
          openedClass: source.type === 'OoadClass' ? source.name : '',
          origin: source.start_line || 1,
        }),
        folds,
      ),
    [source, text, members, owner, folds],
  );
  const initialOpen = () =>
    openAround.length ? foldsAround(prepared.folds, openAround) : unfolded ? prepared.folds.map(foldKey) : openBlockFolds(prepared.folds, source.type);
  // The folds start again whenever the source or the lines to show change, such as a node selected in the graph.
  const openKey = `${source.node_id}|${openAround.map((lines) => `${lines.start}-${lines.end}`).join(',')}|${prepared.folds.length}`;
  const [openFor, setOpenFor] = useState(openKey);
  const [openFolds, setOpenFolds] = useState<string[]>(initialOpen);
  if (openFor !== openKey) {
    setOpenFor(openKey);
    setOpenFolds(initialOpen());
  }
  // Wrapped lines take more than one line's height, so a wrapping editor is as tall as the editor says its content is.
  const [contentHeight, setContentHeight] = useState(0);
  const glyphs = useRef(keepGlyphMargin);
  glyphs.current = keepGlyphMargin;
  const editorRef = useRef<Parameters<OnMount>[0] | null>(null);
  const decorations = useRef<monaco.IEditorDecorationsCollection | null>(null);
  const hideSource = useRef({ id: 'call-folds' });
  const foldsRef = useRef(prepared.folds);
  const depthsRef = useRef(prepared.depths);
  const openFoldsRef = useRef(openFolds);
  foldsRef.current = prepared.folds;
  depthsRef.current = prepared.depths;
  openFoldsRef.current = openFolds;

  useLayoutEffect(() => {
    const editor = editorRef.current;
    if (!editor) {
      return;
    }
    if (editor.getValue() !== prepared.text) {
      editor.setValue(prepared.text);
    }
    applyCallFolds(
      editor,
      prepared.folds,
      openFolds,
      hideSource.current,
      decorations,
      prepared.depths,
      violationLineDecorations(prepared.lineNumbers, markStart, markEnd, Boolean(violation)),
      glyphs.current,
    );
  }, [prepared.text, prepared.folds, prepared.depths, openFolds, prepared.lineNumbers, markStart, markEnd, violation]);

  const onMount: OnMount = (editor) => {
    editorRef.current = editor;
    applyCallFolds(
      editor,
      foldsRef.current,
      openFoldsRef.current,
      hideSource.current,
      decorations,
      depthsRef.current,
      violationLineDecorations(prepared.lineNumbers, markStart, markEnd, Boolean(violation)),
      glyphs.current,
    );
    const nodeEl = editor.getDomNode();
    editor.onDidContentSizeChange((size) => setContentHeight(size.contentHeight));
    nodeEl?.addEventListener('wheel', (event) => scrollSideways(editor, event), { passive: false });
    nodeEl?.addEventListener(
      'mousedown',
      (event) => {
        const target = editor.getTargetAtClientPoint(event.clientX, event.clientY);
        const line = target?.position?.lineNumber;
        const markHit = event.target instanceof Element && event.target.closest('.call-fold, .class-fold, .block-fold') !== null;
        const pageMark = event.target instanceof Element && event.target.closest(`.${SOURCE_MARK}`) !== null;
        if (!line || pageMark || (!markHit && target?.type !== 2)) {
          return;
        }
        const fold = foldsRef.current.find((entry) => entry.glyph === line);
        if (!fold) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        const key = foldKey(fold);
        setOpenFolds((current) => (current.includes(key) ? current.filter((item) => item !== key) : [...current, key]));
      },
      true,
    );
    onEditor?.(editor);
  };

  async function copyCorrectPrompt() {
    if (!violation) {
      return;
    }
    const prompt = buildViolationCorrectPrompt({
      rule: violation.rule,
      message: violation.message,
      nodeName: source.name,
      nodeType: source.type,
      file: file,
      startLine: violation?.startLine ?? source.start_line,
      endLine: violation?.endLine ?? source.end_line,
      excerpt: text,
    });
    try {
      await navigator.clipboard.writeText(prompt);
    } catch (cause) {
      failures.fail(`The prompt was not copied: ${reasonOf(cause)}`, `Copy the correction prompt for ${violation.rule} in the Graph app`);
    }
  }

  return (
    <section className="knowledge-graph-panel source-snippet" data-open="true" data-file={file}>
      {rules.length > 0 ? (
        <div className="source-rules" data-testid="source-rules">
          {rules.map((rule) => (
            <button
              key={rule.name}
              type="button"
              className={['source-rule', rule.status ?? '', rule.name === activeRule ? 'is-active' : ''].filter(Boolean).join(' ')}
              title={rule.messages.join('\n') || undefined}
              onClick={() => onSelectRule?.(rule.name)}
            >
              {rule.name}
            </button>
          ))}
        </div>
      ) : null}
      {violation ? (
        <div className="violation-banner" data-testid="violation-banner">
          <div className="violation-banner-copy">
            <p className="violation-rule">{violation.rule}</p>
            <p className="violation-message">{violation.message}</p>
          </div>
          <button type="button" className="copy-prompt" data-testid="violation-correct" onClick={() => void copyCorrectPrompt()}>
            Correct
          </button>
        </div>
      ) : null}
      <p className="source-path">{file || source.name}</p>
      <div className="panel-source" data-testid="source-excerpt">
        <Editor
          height={wordWrap && contentHeight ? contentHeight + 16 : sourceHeight(prepared.text)}
          language={language || languageFor(file)}
          theme={document.documentElement.dataset.theme === 'engineering' ? 'vs-dark' : 'vs'}
          defaultValue={prepared.text}
          onMount={onMount}
          options={{
            readOnly: true,
            domReadOnly: true,
            folding: false,
            showFoldingControls: 'never',
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            wordWrap: wordWrap ? 'on' : 'off',
            fontFamily: "'JetBrains Mono', ui-monospace, monospace",
            fontSize: 13,
            lineHeight: LINE_HEIGHT,
            glyphMargin: keepGlyphMargin || prepared.folds.length > 0,
            lineNumbers: (line: number) => prepared.lineNumbers[line - 1] ?? '',
            scrollbar: { handleMouseWheel: false, alwaysConsumeMouseWheel: false, horizontal: 'auto', horizontalScrollbarSize: 10 },
          }}
        />
      </div>
    </section>
  );
}

function languageFor(file: string): string {
  if (file.endsWith('.py')) {
    return 'python';
  }
  if (file.endsWith('.tsx') || file.endsWith('.jsx')) {
    return 'typescript';
  }
  return 'typescript';
}

const STORY_SOURCE_TYPES = new Set([
  'Scenario',
  'Story',
  'Background',
  'Step',
  'Given',
  'When',
  'Then',
  'Example',
]);

function openBlockFolds(folds: InlineFold[], nodeType?: string): string[] {
  if (nodeType && STORY_SOURCE_TYPES.has(nodeType)) {
    return folds.filter((fold) => fold.kind === 'block').map((fold) => foldKey(fold));
  }
  return folds.filter((fold) => initialOpenFolds([fold]).length > 0).map((fold) => foldKey(fold));
}

// The page's folds join the layout's own, one fold to a line: a fold the layout already starts on that line stays.
function withNamedFolds<Layout extends { folds: InlineFold[] }>(layout: Layout, folds: SourceFold[]): Layout {
  const named = folds.map(namedFold).filter((fold) => fold.end > fold.glyph && !layout.folds.some((held) => held.glyph === fold.glyph));
  return named.length ? { ...layout, folds: [...layout.folds, ...named] } : layout;
}

function namedFold(fold: SourceFold): InlineFold {
  return { glyph: fold.start, start: fold.start + 1, end: fold.end, kind: fold.kind };
}

// The folds that hold one of the lines asked for, a class around a selected operation too.
export function foldsAround(folds: InlineFold[], around: SourceLines[]): string[] {
  return folds.filter((fold) => around.some((lines) => fold.glyph <= lines.start && fold.end >= lines.end)).map(foldKey);
}

function foldKey(fold: InlineFold): string {
  return `${fold.kind}:${fold.start}:${fold.end}`;
}

function hiddenRanges(folds: InlineFold[], openFolds: string[]): InlineFold[] {
  const open = new Set(openFolds);
  return folds
    .filter((fold) => !open.has(foldKey(fold)) && fold.end >= fold.start)
    .filter(
      (fold) =>
        !folds.some(
          (other) => other !== fold && other.start <= fold.start && other.end >= fold.end && !open.has(foldKey(other)),
        ),
    );
}

function glyphClass(kind: InlineFold['kind'], open: boolean): string {
  if (kind === 'class') {
    return `class-fold${open ? ' class-fold-open' : ''}`;
  }
  if (kind === 'block') {
    return `block-fold${open ? ' block-fold-open' : ''}`;
  }
  return `call-fold${open ? ' call-fold-open' : ''}`;
}

function editorHasViewModel(editor: Parameters<OnMount>[0]): boolean {
  return Boolean(
    (editor as unknown as { _modelData?: { viewModel?: { getLineCount?: () => number } } })._modelData?.viewModel
      ?.getLineCount,
  );
}

// The editor leaves the wheel to the page, so the page scrolls up and down through a file as tall as it is; a sideways
// swipe, or the wheel with shift held, scrolls the editor's long lines instead, and only while they have further to go.
function scrollSideways(editor: Parameters<OnMount>[0], event: WheelEvent): void {
  const sideways = event.shiftKey ? event.deltaY || event.deltaX : Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : 0;
  if (!sideways) {
    return;
  }
  const before = editor.getScrollLeft();
  editor.setScrollLeft(before + sideways);
  if (editor.getScrollLeft() !== before) {
    event.preventDefault();
  }
}

function sourceHeight(text: string): number {
  const lines = Math.max(1, text.split('\n').length);
  return lines * LINE_HEIGHT + 16;
}

function shownLineCount(text: string, folds: InlineFold[], openFolds: string[]): number {
  const hidden = new Set<number>();
  for (const fold of hiddenRanges(folds, openFolds)) {
    for (let line = fold.start; line <= fold.end; line += 1) {
      hidden.add(line);
    }
  }
  return Math.max(1, text.split('\n').length - hidden.size);
}

function violationLineDecorations(
  lineNumbers: string[],
  startLine: number,
  endLine: number,
  active: boolean,
): Decoration[] {
  if (!active || startLine < 1) {
    return [];
  }
  const last = endLine >= startLine ? endLine : startLine;
  const rows: Decoration[] = [];
  for (let index = 0; index < lineNumbers.length; index += 1) {
    const fileLine = Number.parseInt(lineNumbers[index] ?? '', 10);
    if (!Number.isFinite(fileLine) || fileLine < startLine || fileLine > last) {
      continue;
    }
    const editorLine = index + 1;
    rows.push({
      range: { startLineNumber: editorLine, startColumn: 1, endLineNumber: editorLine, endColumn: 1 },
      options: { isWholeLine: true, className: 'violation-highlight' },
    });
  }
  return rows;
}

function applyCallFolds(
  editor: Parameters<OnMount>[0],
  folds: InlineFold[],
  openFolds: string[],
  source: object,
  decorations: Decorations,
  depths: number[] = [],
  violationMarks: Decoration[] = [],
  keepGlyphMargin = false,
) {
  const open = new Set(openFolds);
  const ranges = hiddenRanges(folds, openFolds).map((fold) => ({
    startLineNumber: fold.start,
    startColumn: 1,
    endLineNumber: fold.end,
    endColumn: 1000,
  }));
  const next = [
    ...folds.map((fold) => ({
      range: { startLineNumber: fold.glyph, startColumn: 1, endLineNumber: fold.glyph, endColumn: 1 },
      options: { glyphMarginClassName: glyphClass(fold.kind, open.has(foldKey(fold))) },
    })),
    ...depths.flatMap((depth, index) => {
      if (depth <= 0) {
        return [];
      }
      const level = Math.min(depth, 5);
      return [
        {
          range: { startLineNumber: index + 1, startColumn: 1, endLineNumber: index + 1, endColumn: 1 },
          options: { isWholeLine: true, className: `call-nest call-nest-${level}` },
        },
      ];
    }),
    ...violationMarks,
  ];
  const withOptions = editor as Parameters<OnMount>[0] & { updateOptions?(options: { glyphMargin: boolean }): void };
  withOptions.updateOptions?.({ glyphMargin: keepGlyphMargin || folds.length > 0 });
  if (decorations.current) {
    decorations.current.set(next);
  } else {
    decorations.current = editor.createDecorationsCollection(next);
  }
  const hidden = editor as Parameters<OnMount>[0] & { setHiddenAreas(ranges: object[], source?: object): void };
  hidden.setHiddenAreas(ranges, source);
  if (!editorHasViewModel(editor)) {
    return;
  }
  const token = source as { generation?: number };
  token.generation = (token.generation ?? 0) + 1;
  const generation = token.generation;
  let frames = 0;
  const restore = () => {
    if (token.generation !== generation || frames >= 8) {
      return;
    }
    frames += 1;
    if (viewIsStillFullyExpanded(editor)) {
      decorations.current?.set(next);
      hidden.setHiddenAreas([], source);
      hidden.setHiddenAreas(ranges, source);
      requestAnimationFrame(restore);
    }
  };
  requestAnimationFrame(restore);
}

function viewIsStillFullyExpanded(editor: Parameters<OnMount>[0]): boolean {
  const modelLines = editor.getModel()?.getLineCount() ?? 0;
  const viewModel = (editor as unknown as { _modelData?: { viewModel?: { getLineCount?: () => number } } })._modelData
    ?.viewModel;
  const shown = viewModel?.getLineCount?.() ?? modelLines;
  return modelLines > 1 && shown >= modelLines;
}

export type { FoldMember };
