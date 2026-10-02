import { useEffect, useMemo, useRef, useState } from 'react';
import Editor, { type OnMount } from '@monaco-editor/react';
import {
  displayedCallSource,
  visibleLineCount,
  type CallBody,
  type CallFold,
  type ClassBody,
} from './call-expansion';
import type { SourceRangeDto } from './knowledge-graph';

const GLYPH_MARGIN = 2;
const EMPTY_CLASSES: ClassBody[] = [];
const EMPTY_CALLS: CallBody[] = [];
const LINE_HEIGHT = 20;
const MAX_HEIGHT = 520;

const SNIPPET_OPTIONS = {
  readOnly: true,
  domReadOnly: true,
  folding: false,
  showFoldingControls: 'never' as const,
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
  automaticLayout: true,
  wordWrap: 'off' as const,
  fontFamily: "'JetBrains Mono', ui-monospace, monospace",
  fontSize: 13,
  lineHeight: LINE_HEIGHT,
  renderLineHighlight: 'line' as const,
  scrollbar: {
    alwaysConsumeMouseWheel: false,
    vertical: 'auto' as const,
  },
  overviewRulerBorder: false,
  hideCursorInOverviewRuler: true,
  contextmenu: false,
  glyphMargin: false,
  padding: { top: 8, bottom: 8 },
};

export function SourceSnippetEditor({
  source,
  label,
  typeLabel,
  excerpt = true,
  open = true,
  onToggle,
  toggleTestId = 'toggle-source',
  toggleLabel,
  mark = 'chevron',
  calls,
  classes,
  anchored,
  listClasses = false,
}: {
  source: SourceRangeDto;
  label: string;
  typeLabel: string;
  excerpt?: boolean;
  open?: boolean;
  onToggle?: () => void;
  toggleTestId?: string;
  toggleLabel?: string;
  mark?: 'chevron' | 'class';
  calls?: Map<string, CallBody>;
  classes?: ClassBody[];
  anchored?: CallBody[];
  listClasses?: boolean;
}) {
  const theme = useExplorerMonacoTheme();
  const value = source.text || '';
  const valueRef = useRef(value);
  valueRef.current = value;
  const startLine = source.start_line || 1;
  const noCalls = useRef(new Map<string, CallBody>());
  const catalog = calls ?? noCalls.current;
  const known = classes ?? EMPTY_CLASSES;
  const rooted = anchored ?? EMPTY_CALLS;
  const layout = useMemo(
    () => displayedCallSource(value, catalog, 1, [], known, rooted, listClasses),
    [value, catalog, known, rooted, listClasses],
  );
  const closedFolds = useRef(new Set<number>());
  const [opened, setOpened] = useState<{ text: string; lines: Set<number> }>({
    text: value,
    lines: new Set(),
  });
  const openFolds = opened.text === value ? opened.lines : closedFolds.current;
  const lineMap = useRef<string[]>(layout.lineNumbers);
  const foldsRef = useRef(layout.folds);
  lineMap.current = layout.lineNumbers;
  foldsRef.current = layout.folds;
  const editorRef = useRef<Parameters<OnMount>[0] | null>(null);
  const hideSource = useRef({ id: 'call-folds' });
  const decorations = useRef<{ clear: () => void } | null>(null);
  const [mounted, setMounted] = useState(false);
  const [height, setHeight] = useState(() => editorHeight(visibleLineCount(layout, openFolds)));
  useEffect(() => {
    setHeight(editorHeight(visibleLineCount(layout, openFolds)));
  }, [layout, openFolds]);
  useEffect(() => {
    const editor = editorRef.current;
    if (!editor) {
      return;
    }
    if (editor.getValue() !== layout.text) {
      editor.setValue(layout.text);
    }
    editor.updateOptions({
      glyphMargin: layout.folds.length > 0,
      lineNumbers: (line) => {
        const mapped = lineMap.current[line - 1];
        return mapped ? String(startLine + Number(mapped) - 1) : '';
      },
    });
    applyCallFolds(editor, layout.folds, openFolds, hideSource.current, decorations);
  }, [layout, startLine, openFolds, mounted]);
  const fitHeight: OnMount = (editor) => {
    editorRef.current = editor;
    setMounted(true);
    const fit = () => {
      const next = fittedHeight(editor.getContentHeight());
      setHeight((current) => (current === next ? current : next));
    };
    fit();
    editor.onDidContentSizeChange(fit);
    const node = editor.getDomNode();
    node?.addEventListener(
      'mousedown',
      (event) => {
        const target = editor.getTargetAtClientPoint(event.clientX, event.clientY);
        const line = target?.position?.lineNumber ?? target?.range?.startLineNumber;
        const markHit =
          event.target instanceof Element &&
          event.target.closest(
            '.codicon-folding-collapsed, .codicon-folding-expanded, .call-fold, .class-fold',
          ) !== null;
        if (!line || !target || (target.type !== GLYPH_MARGIN && !markHit)) {
          return;
        }
        const fold = foldsRef.current.find((entry) => entry.start === line);
        if (!fold) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        setOpened((current) => {
          const base = current.text === valueRef.current ? current.lines : closedFolds.current;
          const next = new Set(base);
          if (next.has(fold.start)) {
            next.delete(fold.start);
          } else {
            next.add(fold.start);
          }
          applyCallFolds(editor, foldsRef.current, next, hideSource.current, decorations);
          return { text: valueRef.current, lines: next };
        });
      },
      true,
    );
  };
  return (
    <div
      className="source-snippet"
      data-testid={excerpt ? 'source-excerpt' : 'nested-source'}
      data-open={open ? 'true' : 'false'}
    >
      <div className="source-snippet-bar">
        <button
          type="button"
          className="source-toggle"
          data-testid={toggleTestId}
          aria-expanded={open}
          aria-label={toggleLabel ?? (open ? 'Collapse' : 'Expand')}
          onClick={onToggle}
        >
          {mark === 'class' ? <ClassMark open={open} /> : open ? '▼' : '▶'}
        </button>
        <h2>
          {label} <span className="source-type">({typeLabel})</span>
        </h2>
      </div>
      {open ? (
        <Editor
          height={height}
          language={languageFor(source.file)}
          value={layout.text}
          theme={theme}
          onMount={fitHeight}
          loading={<pre className="source-loading">{layout.text}</pre>}
          options={{
            ...SNIPPET_OPTIONS,
            glyphMargin: layout.folds.length > 0,
            lineNumbers: (line) => {
              const mapped = lineMap.current[line - 1];
              return mapped ? String(startLine + Number(mapped) - 1) : '';
            },
          }}
        />
      ) : null}
    </div>
  );
}

function useExplorerMonacoTheme(): 'kg-light' | 'kg-dark' {
  const [theme, setTheme] = useState<'kg-light' | 'kg-dark'>(() =>
    document.documentElement.dataset.theme === 'engineering'
      ? 'kg-dark'
      : 'kg-light',
  );
  useEffect(() => {
    const root = document.documentElement;
    const sync = () =>
      setTheme(root.dataset.theme === 'engineering' ? 'kg-dark' : 'kg-light');
    const observer = new MutationObserver(sync);
    observer.observe(root, { attributes: true, attributeFilter: ['data-theme'] });
    return () => observer.disconnect();
  }, []);
  return theme;
}

function applyCallFolds(
  editor: Parameters<OnMount>[0],
  folds: CallFold[],
  open: Set<number>,
  source: object,
  decorations: { current: { clear: () => void } | null },
) {
  const ranges = folds
    .filter((fold) => !open.has(fold.start) && fold.end > fold.start)
    .map((fold) => ({
      startLineNumber: fold.start + 1,
      startColumn: 1,
      endLineNumber: fold.end,
      endColumn: 1,
    }));
  (
    editor as Parameters<OnMount>[0] & {
      setHiddenAreas(ranges: object[], source?: object): void;
    }
  ).setHiddenAreas(ranges, source);
  decorations.current?.clear();
  decorations.current = editor.createDecorationsCollection(
    folds.map((fold) => ({
      range: {
        startLineNumber: fold.start,
        startColumn: 1,
        endLineNumber: fold.start,
        endColumn: 1,
      },
      options: {
        glyphMarginClassName: glyphClass(fold.kind, open.has(fold.start)),
        glyphMarginHoverMessage: {
          value: hoverLabel(fold.kind, open.has(fold.start)),
        },
      },
    })),
  );
}

function glyphClass(kind: CallFold['kind'], open: boolean): string {
  const icon = open ? 'codicon-folding-expanded' : 'codicon-folding-collapsed';
  if (kind === 'class') {
    return `codicon ${icon} class-fold${open ? ' class-fold-open' : ''}`;
  }
  return `codicon ${icon} call-fold${open ? ' call-fold-open' : ''}`;
}

function hoverLabel(kind: CallFold['kind'], open: boolean): string {
  const noun = kind === 'class' ? 'class' : 'call';
  return open ? `Collapse ${noun}` : `Expand ${noun}`;
}

function ClassMark({ open }: { open: boolean }) {
  return (
    <svg
      className="class-mark"
      viewBox="0 0 16 16"
      width="14"
      height="14"
      data-open={open ? 'true' : 'false'}
      aria-hidden="true"
    >
      <rect
        x="2.5"
        y="2.5"
        width="11"
        height="11"
        rx="0.5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <path d="M2.5 6.2h11" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

function editorHeight(lines: number): number {
  return fittedHeight(lines * LINE_HEIGHT + 16);
}

function fittedHeight(contentHeight: number): number {
  return Math.min(Math.max(Math.ceil(contentHeight), LINE_HEIGHT + 16), MAX_HEIGHT);
}

const LANGUAGE_BY_EXT: Record<string, string> = {
  py: 'python',
  ts: 'typescript',
  tsx: 'typescript',
  js: 'javascript',
  jsx: 'javascript',
  json: 'json',
  css: 'css',
  html: 'html',
  htm: 'html',
  md: 'markdown',
  ql: 'java',
  qll: 'java',
};

function languageFor(file: string): string {
  const name = file.replaceAll('\\', '/').split('/').pop() ?? '';
  const ext = name.includes('.') ? name.slice(name.lastIndexOf('.') + 1) : '';
  return LANGUAGE_BY_EXT[ext] ?? 'plaintext';
}
