import type { editor as monaco } from 'monaco-editor';
import { useEffect, useState } from 'react';

// A line of the file whose link names a heading in another file, and that heading's section, which opens in place under
// the line: a story map's story opens its scenarios, a scenario's domain term its class in the markdown model.
export type SourceCallout = { line: number; title: string; path: string; startLine: number; endLine: number; text: string };

export const CALLOUT_MARK = 'callout-mark';

type CalloutEditor = Pick<monaco.IStandaloneCodeEditor, 'createDecorationsCollection' | 'onMouseDown' | 'changeViewZones'>;

// The callouts of the open file: a mark beside each callout's line, which a press opens and closes, and under each open
// one its section, headed by the file and lines it comes from. A section opens in a view zone, which adds no line to
// the file, so comments, rules and selected lines stay on the file's own lines. Answers whether any callout is open,
// since an open section makes the editor taller than its file.
export function useCallouts(editor: CalloutEditor | null, callouts: SourceCallout[], lineNumbers: string[]): boolean {
  const [open, setOpen] = useState<number[]>([]);
  useEffect(() => {
    if (!editor || !callouts.length) return;
    const marks = editor.createDecorationsCollection(calloutMarks(callouts, lineNumbers, open));
    return () => marks.clear();
  }, [editor, callouts, lineNumbers, open]);
  useEffect(() => {
    if (!editor || !callouts.length) return;
    const pressing = editor.onMouseDown((event) => {
      const line = event.target.position?.lineNumber;
      if (!line || !(event.target.element instanceof Element) || !event.target.element.closest(`.${CALLOUT_MARK}`)) return;
      const fileLine = Number.parseInt(lineNumbers[line - 1] ?? '', 10);
      setOpen((current) => (current.includes(fileLine) ? current.filter((held) => held !== fileLine) : [...current, fileLine]));
    });
    return () => pressing.dispose();
  }, [editor, callouts, lineNumbers]);
  useEffect(() => {
    if (!editor) return;
    const zones: string[] = [];
    editor.changeViewZones((accessor) => {
      for (const callout of callouts.filter((each) => open.includes(each.line))) {
        zones.push(accessor.addZone({ afterLineNumber: editorLineOf(lineNumbers, callout.line), heightInLines: callout.text.split('\n').length + 1, domNode: calloutSection(callout) }));
      }
    });
    return () => editor.changeViewZones((accessor) => zones.forEach((zone) => accessor.removeZone(zone)));
  }, [editor, callouts, lineNumbers, open]);
  return open.length > 0;
}

function calloutMarks(callouts: SourceCallout[], lineNumbers: string[], open: number[]): monaco.IModelDeltaDecoration[] {
  return callouts.map((callout) => {
    const line = editorLineOf(lineNumbers, callout.line);
    return {
      range: { startLineNumber: line, startColumn: 1, endLineNumber: line, endColumn: 1 },
      options: {
        glyphMarginClassName: `${CALLOUT_MARK}${open.includes(callout.line) ? ' callout-mark-open' : ''}`,
        glyphMarginHoverMessage: { value: `${callout.title}: ${callout.path} lines ${callout.startLine} to ${callout.endLine}` },
      },
    };
  });
}

// The editor line that shows fileLine; calls opened in place add lines the file does not have there.
function editorLineOf(lineNumbers: string[], fileLine: number): number {
  const index = lineNumbers.indexOf(String(fileLine));
  return index >= 0 ? index + 1 : fileLine;
}

function calloutSection(callout: SourceCallout): HTMLElement {
  const section = document.createElement('div');
  section.className = 'callout-section';
  const from = document.createElement('p');
  from.className = 'callout-from';
  from.textContent = `${callout.path} · lines ${callout.startLine} to ${callout.endLine}`;
  const text = document.createElement('pre');
  text.className = 'callout-text';
  text.textContent = callout.text;
  section.append(from, text);
  return section;
}
