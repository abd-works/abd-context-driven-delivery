import Editor, { type Monaco, type OnMount } from '@monaco-editor/react';
import type { editor as monaco } from 'monaco-editor';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { CallCatalog, type FoldMember } from './call-expansion';
import { useCallouts, type CalloutsWithin, type SourceCallout } from './source-callouts';
import { foldMarkdownHeadings, useOpenAround, type SourceLines } from './source-folding';
import type { NodeSourceData } from '@cdd/harness/graph/graph';
import { buildViolationCorrectPrompt } from './violation-prompt';
import type { ViolationFocus } from '../graph/graph-selection';
import { reasonOf } from '../graph/graph-failures';
import { failures } from '../graph/graph-page';
import './source.css';

const LINE_HEIGHT = 20;
// The room the editor keeps above and below its lines.
const SOURCE_PADDING = 16;

type Decoration = monaco.IModelDeltaDecoration;

export type SourceRule = {
  name: string;
  status?: string;
  messages: string[];
};

export type SourceEditorInstance = Parameters<OnMount>[0];

// What a page showing a whole file adds to the view: the lines to open, such as the nodes selected in the graph, around
// which every other fold closes; the language the file is in; whether calls and classes the code names open in place,
// which a story test's page turns off, since its callouts are its steps' own; the callouts it opens in place itself;
// whether long lines wrap, or scroll sideways (shift+wheel or a sideways swipe, since the page, not the editor, scrolls
// up and down); and the editor and its Monaco once made, so the page can add its own gutter marks (each with the class
// SOURCE_MARK) and menu actions, such as the Files app's comments, and bind its shortcuts. The file folds as Monaco folds
// its language, by its classes, functions and blocks, and markdown by its headings. The callouts expandCallouts names open
// as the page asks, such as a node selected in the graph through a connector.
export type SourceHostProps = {
  openAround?: SourceLines[];
  language?: string;
  keepGlyphMargin?: boolean;
  wordWrap?: boolean;
  callouts?: SourceCallout[];
  expandCallouts?: string[];
  opensCalls?: boolean;
  onEditor?: (editor: SourceEditorInstance, monacoApi: Monaco) => void;
};

export const SOURCE_MARK = 'source-mark';

const NO_LINES: SourceLines[] = [];
const NO_CALLOUTS: SourceCallout[] = [];
const NO_IDS: string[] = [];
const NO_MEMBERS: NodeSourceData[] = [];
// A text in no language Monaco reads as code holds no calls.
const PROSE_LANGUAGES = new Set(['markdown', 'plaintext']);

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

type SourceEditorProps = SourceHostProps & {
  source: NodeSourceData;
  violation: ViolationFocus | null;
  rules: SourceRule[];
  activeRule: string;
  onSelectRule?: (name: string) => void;
};

function SourceEditor({ source, violation, rules, activeRule, onSelectRule, openAround = NO_LINES, language = '', keepGlyphMargin = false, wordWrap = false, callouts = NO_CALLOUTS, expandCallouts = NO_IDS, opensCalls = true, onEditor }: SourceEditorProps) {
  const file = source.file ?? '';
  const text = source.text ?? '';
  const origin = source.start_line || 1;
  const shownLanguage = language || languageFor(file);
  const [editor, setEditor] = useState<SourceEditorInstance | null>(null);
  const [contentHeight, setContentHeight] = useState(0);
  const { shown, within } = useSourceCallouts(source, shownLanguage, callouts, opensCalls);
  const editorLineOf = useCallback((fileLine: number) => fileLine - origin + 1, [origin]);
  useCallouts(editor, shown, within, editorLineOf, expandCallouts);
  useOpenAround(editor, openAround, text);
  useLineMarks(editor, origin, text, violation, openAround);
  const onMount: OnMount = (made, monacoApi) => {
    foldMarkdownHeadings(monacoApi);
    made.onDidContentSizeChange((size) => setContentHeight(size.contentHeight));
    made.getDomNode()?.addEventListener('wheel', (event) => scrollSideways(made, event), { passive: false });
    setEditor(made);
    onEditor?.(made, monacoApi);
  };
  return (
    <section className="knowledge-graph-panel source-snippet" data-open="true" data-file={file}>
      <SourceRulesView rules={rules} activeRule={activeRule} onSelectRule={onSelectRule} />
      {violation ? <ViolationBannerView violation={violation} source={source} /> : null}
      <p className="source-path">{file || source.name}</p>
      <div className="panel-source" data-testid="source-excerpt">
        <Editor
          height={contentHeight ? contentHeight + SOURCE_PADDING : sourceHeight(text)}
          language={shownLanguage}
          theme={document.documentElement.dataset.theme === 'engineering' ? 'vs-dark' : 'vs'}
          value={text}
          onMount={onMount}
          options={{
            readOnly: true,
            domReadOnly: true,
            folding: true,
            foldingStrategy: 'auto',
            showFoldingControls: 'mouseover',
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            wordWrap: wordWrap ? 'on' : 'off',
            fontFamily: "'JetBrains Mono', ui-monospace, monospace",
            fontSize: 13,
            lineHeight: LINE_HEIGHT,
            glyphMargin: keepGlyphMargin || shown.length > 0,
            lineNumbers: (line: number) => String(origin + line - 1),
            scrollbar: { handleMouseWheel: false, alwaysConsumeMouseWheel: false, horizontal: 'auto', horizontalScrollbarSize: 10 },
          }}
        />
      </div>
    </section>
  );
}

// The callouts the source shows: the page's own, then, while the code may open calls, each call and class its code
// reaches among the graph's members; and the callouts inside an open one, the calls its own code reaches.
function useSourceCallouts(source: NodeSourceData, language: string, callouts: SourceCallout[], opensCalls: boolean): { shown: SourceCallout[]; within: CalloutsWithin } {
  const members = (source.members ?? NO_MEMBERS) as FoldMember[];
  const owner = members.find((member) => member.node_id === source.node_id)?.owner ?? '';
  const catalog = useMemo(() => new CallCatalog(members, owner), [members, owner]);
  const isCode = !PROSE_LANGUAGES.has(language);
  const shown = useMemo(() => {
    const own = opensCalls && isCode ? catalog.calloutsIn(source.text ?? '', source.start_line || 1, language, [source.node_id], source.file) : [];
    return [...callouts, ...own];
  }, [catalog, callouts, opensCalls, isCode, source, language]);
  const within = useCallback<CalloutsWithin>((callout, stack) => (callout.kind === 'section' ? [] : catalog.calloutsIn(callout.text, callout.startLine, languageFor(callout.path), stack, callout.path)), [catalog]);
  return { shown, within };
}

// The lines of the broken rule chosen and of the nodes the page asked to show, marked whole.
function useLineMarks(editor: SourceEditorInstance | null, origin: number, text: string, violation: ViolationFocus | null, openAround: SourceLines[]): void {
  useEffect(() => {
    if (!editor) return;
    const lastLine = origin + text.split('\n').length - 1;
    const violationLines = violation ? [{ start: violation.startLine ?? origin, end: violation.endLine ?? violation.startLine ?? lastLine }] : [];
    const selected = openAround.filter((lines) => lines.start > origin || lines.end < lastLine);
    const marks = editor.createDecorationsCollection([...linesMarked(violationLines, origin, 'violation-highlight'), ...linesMarked(selected, origin, 'selected-lines')]);
    return () => marks.clear();
  }, [editor, origin, text, violation, openAround]);
}

// Each editor line of each span, marked whole.
function linesMarked(spans: SourceLines[], origin: number, className: string): Decoration[] {
  const lines = spans.filter((span) => span.start >= 1).flatMap((span) => Array.from({ length: Math.max(span.start, span.end) - span.start + 1 }, (_, index) => span.start + index - origin + 1));
  return lines.map((line) => ({ range: { startLineNumber: line, startColumn: 1, endLineNumber: line, endColumn: 1 }, options: { isWholeLine: true, className } }));
}

function SourceRulesView({ rules, activeRule, onSelectRule }: { rules: SourceRule[]; activeRule: string; onSelectRule?: (name: string) => void }) {
  if (!rules.length) return null;
  return (
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
  );
}

function ViolationBannerView({ violation, source }: { violation: ViolationFocus; source: NodeSourceData }) {
  async function copyCorrectPrompt() {
    const prompt = buildViolationCorrectPrompt({
      rule: violation.rule,
      message: violation.message,
      nodeName: source.name,
      nodeType: source.type,
      file: source.file ?? '',
      startLine: violation.startLine ?? source.start_line,
      endLine: violation.endLine ?? source.end_line,
      excerpt: source.text ?? '',
    });
    try {
      await navigator.clipboard.writeText(prompt);
    } catch (cause) {
      failures.fail(`The prompt was not copied: ${reasonOf(cause)}`, `Copy the correction prompt for ${violation.rule} in the Graph app`);
    }
  }
  return (
    <div className="violation-banner" data-testid="violation-banner">
      <div className="violation-banner-copy">
        <p className="violation-rule">{violation.rule}</p>
        <p className="violation-message">{violation.message}</p>
      </div>
      <button type="button" className="copy-prompt" data-testid="violation-correct" onClick={() => void copyCorrectPrompt()}>
        Correct
      </button>
    </div>
  );
}

function languageFor(file: string): string {
  if (file.endsWith('.py')) return 'python';
  if (file.endsWith('.md')) return 'markdown';
  return 'typescript';
}

// The editor leaves the wheel to the page, so the page scrolls up and down through a file as tall as it is; a sideways
// swipe, or the wheel with shift held, scrolls the editor's long lines instead, and only while they have further to go.
function scrollSideways(editor: SourceEditorInstance, event: WheelEvent): void {
  const sideways = event.shiftKey ? event.deltaY || event.deltaX : Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : 0;
  if (!sideways) return;
  const before = editor.getScrollLeft();
  editor.setScrollLeft(before + sideways);
  if (editor.getScrollLeft() !== before) event.preventDefault();
}

function sourceHeight(text: string): number {
  return Math.max(1, text.split('\n').length) * LINE_HEIGHT + SOURCE_PADDING;
}

