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
  const openFoldsRef = useRef(openFolds);
  foldsRef.current = prepared.folds;
  openFoldsRef.current = openFolds;

  useLayoutEffect(() => {
    const editor = editorRef.current;
    if (!editor) {
      return;
    }
    if (editor.getValue() !== prepared.text) {
      editor.setValue(prepared.text);
    }
    applyCallFolds(editor, prepared.folds, openFolds, hideSource.current, decorations);
  }, [prepared.text, prepared.folds, openFolds]);

  const onMount: OnMount = (editor) => {
    editorRef.current = editor;
    applyCallFolds(editor, foldsRef.current, openFoldsRef.current, hideSource.current, decorations);
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
          height={Math.max(LINE_HEIGHT + 16, prepared.text.split('\n').length * LINE_HEIGHT)}
          language={languageFor(source.file)}
          theme={document.documentElement.dataset.theme === 'engineering' ? 'vs-dark' : 'vs'}
          value={prepared.text}
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

function applyCallFolds(
  editor: Parameters<OnMount>[0],
  folds: InlineFold[],
  openFolds: string[],
  source: object,
  decorations: { current: { set: (next: object[]) => void; clear: () => void } | null },
) {
  const open = new Set(openFolds);
  const ranges = hiddenRanges(folds, openFolds).map((fold) => ({
    startLineNumber: fold.start,
    startColumn: 1,
    endLineNumber: fold.end,
    endColumn: 1000,
  }));
  const next = folds.map((fold) => ({
    range: { startLineNumber: fold.glyph, startColumn: 1, endLineNumber: fold.glyph, endColumn: 1 },
    options: { glyphMarginClassName: glyphClass(fold.kind, open.has(foldKey(fold))) },
  }));
  if (decorations.current) {
    decorations.current.set(next);
  } else {
    decorations.current = editor.createDecorationsCollection(next);
  }
  const hidden = editor as Parameters<OnMount>[0] & { setHiddenAreas(ranges: object[], source?: object): void };
  hidden.setHiddenAreas(ranges, source);
}

export type { FoldMember };
