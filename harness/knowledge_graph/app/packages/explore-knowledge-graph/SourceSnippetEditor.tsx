import { useEffect, useState } from 'react';
import Editor, { type OnMount } from '@monaco-editor/react';
import type { SourceRangeDto } from './knowledge-graph';

const LINE_HEIGHT = 20;
const MAX_HEIGHT = 520;

const SNIPPET_OPTIONS = {
  readOnly: true,
  domReadOnly: true,
  folding: true,
  showFoldingControls: 'always' as const,
  foldingStrategy: 'indentation' as const,
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
}: {
  source: SourceRangeDto;
  label: string;
  typeLabel: string;
  excerpt?: boolean;
  open?: boolean;
  onToggle?: () => void;
  toggleTestId?: string;
  toggleLabel?: string;
}) {
  const theme = useExplorerMonacoTheme();
  const value = source.text || '';
  const startLine = source.start_line || 1;
  const [height, setHeight] = useState(() => editorHeight(value));
  useEffect(() => {
    setHeight(editorHeight(value));
  }, [value]);
  const fitHeight: OnMount = (editor) => {
    const fit = () => {
      const next = fittedHeight(editor.getContentHeight());
      setHeight((current) => (current === next ? current : next));
    };
    fit();
    editor.onDidContentSizeChange(fit);
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
          {open ? '▼' : '▶'}
        </button>
        <h2>
          {label} <span className="source-type">({typeLabel})</span>
        </h2>
      </div>
      {open ? (
        <Editor
          height={height}
          language={languageFor(source.file)}
          value={value}
          theme={theme}
          onMount={fitHeight}
          loading={<pre className="source-loading">{value}</pre>}
          options={{
            ...SNIPPET_OPTIONS,
            lineNumbers: (line) => String(startLine + line - 1),
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

function editorHeight(value: string): number {
  const lines = Math.max(value.split('\n').length, 1);
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
