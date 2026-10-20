import Editor, { type OnMount } from '@monaco-editor/react';
import { useLayoutEffect, useMemo, useRef, useState } from 'react';
import { initialOpenFolds, inlineCallLayout, type FoldMember, type InlineFold } from './call-expansion';
import type { SourceText } from './SourceClient';
import { buildViolationCorrectPrompt, type ViolationFocus } from './violation-prompt';

const LINE_HEIGHT = 20;

export type SourceRule = {
  name: string;
  status?: string;
  messages: string[];
};

type SourceViewProps = {
  source: SourceText | null;
  violation: ViolationFocus | null;
  rules: SourceRule[];
  activeRule: string;
  onSelectRule?: (name: string) => void;
};

export function SourceView({ source, violation, rules = [], activeRule = '', onSelectRule = () => undefined }: SourceViewProps) {
  return (
    <div className="panel" data-testid="source-file">
      {source ? (
        <SourceEditor source={source} violation={violation} rules={rules} activeRule={activeRule} onSelectRule={onSelectRule} />
      ) : (
        <p className="empty-state">Select a node</p>
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
}: {
  source: SourceText;
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
  const owner = members.find((member) => member.id === source.node_id)?.owner ?? '';
  const prepared = useMemo(
    () =>
      inlineCallLayout(text, members, owner, {
        openedClass: source.type === 'OoadClass' ? source.name : '',
        origin: source.start_line || 1,
      }),
    [source, text, members, owner],
  );
  const [openFor, setOpenFor] = useState(source.node_id);
  const [openFolds, setOpenFolds] = useState<string[]>(() => openBlockFolds(prepared.folds, source.type));
  if (openFor !== source.node_id) {
    setOpenFor(source.node_id);
    setOpenFolds(openBlockFolds(prepared.folds, source.type));
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
    applyCallFolds(
      editor,
      prepared.folds,
      openFolds,
      hideSource.current,
      decorations,
      prepared.depths,
      violationLineDecorations(prepared.lineNumbers, markStart, markEnd, Boolean(violation)),
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
    );
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
    await navigator.clipboard.writeText(prompt);
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
          height={sourceHeight(prepared.text)}
          language={languageFor(file)}
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
): { range: { startLineNumber: number; startColumn: number; endLineNumber: number; endColumn: number }; options: { isWholeLine: boolean; className: string } }[] {
  if (!active || startLine < 1) {
    return [];
  }
  const last = endLine >= startLine ? endLine : startLine;
  const rows: { range: { startLineNumber: number; startColumn: number; endLineNumber: number; endColumn: number }; options: { isWholeLine: boolean; className: string } }[] = [];
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
  decorations: { current: { set: (next: object[]) => void; clear: () => void } | null },
  depths: number[] = [],
  violationMarks: { range: { startLineNumber: number; startColumn: number; endLineNumber: number; endColumn: number }; options: { isWholeLine?: boolean; className?: string; glyphMarginClassName?: string } }[] = [],
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
