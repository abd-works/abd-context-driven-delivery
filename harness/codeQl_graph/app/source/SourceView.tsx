import Editor, { type OnMount } from '@monaco-editor/react';
import { useLayoutEffect, useMemo, useRef, useState } from 'react';
import { initialOpenFolds, inlineCallLayout, type FoldMember, type InlineFold } from './call-expansion';
import type { SourceText } from './SourceClient';

const LINE_HEIGHT = 20;

type SourceViewProps = {
  source: SourceText | null;
};

export function SourceView({ source }: SourceViewProps) {
  return (
    <div className="panel" data-testid="source-file">
      {source ? <SourceEditor source={source} /> : <p className="empty-state">Select a node</p>}
    </div>
  );
}

function SourceEditor({ source }: { source: SourceText }) {
  const members = source.members ?? [];
  const owner = members.find((member) => member.id === source.node_id)?.owner ?? '';
  const prepared = useMemo(
    () =>
      inlineCallLayout(source.text, members, owner, {
        openedClass: source.type === 'OoadClass' ? source.name : '',
        origin: source.start_line || 1,
      }),
    [source, members, owner],
  );
  const [openFor, setOpenFor] = useState(source.node_id);
  const [openFolds, setOpenFolds] = useState<string[]>(() => openBlockFolds(prepared.folds));
  if (openFor !== source.node_id) {
    setOpenFor(source.node_id);
    setOpenFolds(openBlockFolds(prepared.folds));
  }
  const editorRef = useRef<Parameters<OnMount>[0] | null>(null);
  const decorations = useRef<{ set: (next: object[]) => void; clear: () => void } | null>(null);
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
    applyCallFolds(editor, prepared.folds, openFolds, hideSource.current, decorations, prepared.depths);
  }, [prepared.text, prepared.folds, prepared.depths, openFolds]);

  const onMount: OnMount = (editor) => {
    editorRef.current = editor;
    applyCallFolds(editor, foldsRef.current, openFoldsRef.current, hideSource.current, decorations, depthsRef.current);
    const nodeEl = editor.getDomNode();
    nodeEl?.addEventListener(
      'mousedown',
      (event) => {
        const target = editor.getTargetAtClientPoint(event.clientX, event.clientY);
        const line = target?.position?.lineNumber;
        const markHit = event.target instanceof Element && event.target.closest('.call-fold, .class-fold, .block-fold') !== null;
        if (!line || (!markHit && target?.type !== 2)) {
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
  };

  return (
    <section className="knowledge-graph-panel source-snippet" data-open="true" data-file={source.file}>
      <p className="source-path">{source.file || source.name}</p>
      <div className="panel-source" data-testid="source-excerpt">
        <Editor
          height={Math.max(LINE_HEIGHT + 16, shownLineCount(prepared.text, prepared.folds, openFolds) * LINE_HEIGHT)}
          language={languageFor(source.file)}
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
            wordWrap: 'off',
            fontFamily: "'JetBrains Mono', ui-monospace, monospace",
            fontSize: 13,
            lineHeight: LINE_HEIGHT,
            glyphMargin: prepared.folds.length > 0,
            lineNumbers: (line: number) => prepared.lineNumbers[line - 1] ?? '',
            scrollbar: { handleMouseWheel: false, alwaysConsumeMouseWheel: false },
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

function openBlockFolds(folds: InlineFold[]): string[] {
  return folds.filter((fold) => initialOpenFolds([fold]).length > 0).map((fold) => foldKey(fold));
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

function shownLineCount(text: string, folds: InlineFold[], openFolds: string[]): number {
  const hidden = new Set<number>();
  for (const fold of hiddenRanges(folds, openFolds)) {
    for (let line = fold.start; line <= fold.end; line += 1) {
      hidden.add(line);
    }
  }
  return Math.max(1, text.split('\n').length - hidden.size);
}

function applyCallFolds(
  editor: Parameters<OnMount>[0],
  folds: InlineFold[],
  openFolds: string[],
  source: object,
  decorations: { current: { set: (next: object[]) => void; clear: () => void } | null },
  depths: number[] = [],
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
  ];
  const withOptions = editor as Parameters<OnMount>[0] & { updateOptions?(options: { glyphMargin: boolean }): void };
  withOptions.updateOptions?.({ glyphMargin: folds.length > 0 });
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
