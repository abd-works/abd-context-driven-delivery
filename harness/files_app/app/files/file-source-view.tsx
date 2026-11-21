import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'

import type { NodeSourceData } from '@cdd/harness/graph/graph'
import type { SessionFileData } from '@cdd/space/session/session'
import { SourceView, type SourceEditorInstance } from '@source-view/SourceView'
import type { GoToFile } from '@source-view/source-callouts'
import type { SourceLines } from '@source-view/source-folding'
import type { Monaco } from '@monaco-editor/react'

import { memberLines } from './code-outline'
import { CommentCardView, CommentComposerView } from './comment-box-view'
import { placeUnder, useAddCommentAction, useAddToContextAction, useFileMarks, useMarkerPresses } from './editor-comments'
import type { CommentLines, FileCommentsActions } from './file-comments-actions'
import { selectedMarks } from './file-marks'
import { keepWrap, storedWrap, type ThemeFailure } from './files-theme'
import type { FilesFoldKeys } from './files-fold-keys'
import { calloutsOf, expandedLines, isStoryTest, monacoLanguageOf, rulesOf, sourceOf, violationFocusOf } from './source-of-file'

// How far down the window the first line asked to show sits once the page scrolls to it: near the top, so it is plain
// where the page went, with a line or two above it for context.
const SHOWN_FROM_TOP = 1 / 10
// How long a file's folds take to close after it opens, during which the page keeps the line asked for in view.
const FOLDS_SETTLE_MILLISECONDS = 1500

// The nodes selected in the graph view, marked by one orange line beside their lines rather than by shading the text.
function useSelectedMarks(editor: SourceEditorInstance | null, openAround: SourceLines[], lineCount: number): void {
  useEffect(() => {
    if (!editor) return
    const marks = editor.createDecorationsCollection(selectedMarks(openAround, lineCount))
    return () => marks.clear()
  }, [editor, openAround, lineCount])
}

// A code file opened with no node selected opens as an outline: its classes open and their members folded. Only a
// newly opened text folds so; a node selected opens its own folds instead, as useOpenAround does.
function useMembersFolded(editor: SourceEditorInstance | null, text: string, language: string, openAround: SourceLines[]): void {
  const selected = useRef(openAround)
  selected.current = openAround
  useEffect(() => {
    const members = memberLines(text, language)
    if (!editor || selected.current.length || !members.length) return
    editor.trigger('files-outline', 'editor.fold', { selectionLines: members.map(line => line - 1), levels: 1 })
  }, [editor, text, language])
}

// The open file in the graph explorer's source view, folding as Monaco folds its language, with the project's fold keys:
// its broken rules as chips with the chosen one marked, and the comments on it: Add comment and Add to context on the
// right-click menu, a marker beside each comment's first line, and the box a marker opens.
// Lines asked to show, such as the nodes selected in the graph view, unfold and the page scrolls the first into view: the
// editor is as tall as the file, so the page scrolls, not the editor. Every other fold closes; with none asked, a code
// file opens with its classes open and their members folded, and any other file with every fold open. Long lines scroll sideways, or wrap once the reader turns on Wrap lines. With the graph's members,
// once the graph view read them, a call opens in place even when it reaches another file; in a story test, what each
// step invokes and observes opens on the step's line instead. toggle, for a file with a rendered form, leads its bar.
export function FileSourceView({
  file,
  actions,
  onAddToContext,
  openAround = [],
  expanded = [],
  onGoToFile,
  members = [],
  keys,
  fail,
  toggle,
}: {
  file: SessionFileData
  actions: FileCommentsActions
  onAddToContext: (lines: CommentLines) => void
  openAround?: SourceLines[]
  expanded?: string[]
  onGoToFile?: GoToFile
  members?: NodeSourceData[]
  keys: FilesFoldKeys
  fail: ThemeFailure
  toggle?: ReactNode
}) {
  const wrapper = useRef<HTMLDivElement>(null)
  const held = useRef(file)
  held.current = file
  const [editor, setEditor] = useState<SourceEditorInstance | null>(null)
  const onEditor = useCallback((made: SourceEditorInstance, monacoApi: Monaco) => {
    keys.bindIn(monacoApi)
    setEditor(made)
  }, [keys])
  const [chosenRule, setChosenRule] = useState('')
  const [composing, setComposing] = useState<CommentLines | null>(null)
  const [opened, setOpened] = useState('')
  const [wrap, setWrap] = useState(() => storedWrap(fail))
  const toggleWrap = () => {
    keepWrap(!wrap, fail)
    setWrap(!wrap)
  }
  const source = useMemo(() => sourceOf(file, members), [file, members])
  // The file's callouts as the session answered them for the file view's filters; the page reads the file again when a
  // practice, a format or a connector changes.
  const callouts = useMemo(() => calloutsOf(file), [file])
  // A node selected through a connector shows on the line of its holder that uses it, which its fold-out opens under.
  const expandLines = useMemo(() => expandedLines(callouts, expanded, openAround), [callouts, expanded, openAround])
  const shownAround = useMemo(() => (expandLines.length ? expandLines.map(line => ({ start: line, end: line })) : openAround), [expandLines, openAround])
  const rules = useMemo(() => rulesOf(file), [file])
  const rule = rules.some(shown => shown.name === chosenRule) ? chosenRule : (rules[0]?.name ?? '')
  const compose = useCallback((lines: CommentLines) => {
    setOpened('')
    setComposing(lines)
  }, [])
  const open = useCallback((anchor: string) => {
    setComposing(null)
    setOpened(current => (current === anchor ? '' : anchor))
  }, [])
  useAddCommentAction(editor, compose)
  useAddToContextAction(editor, onAddToContext)
  useFileMarks(editor, file)
  useMarkerPresses(editor, held, open)
  useSelectedMarks(editor, shownAround, source.end_line)
  useMembersFolded(editor, file.text, monacoLanguageOf(file), shownAround)
  const firstShown = shownAround[0]?.start ?? 0
  useEffect(() => {
    if (!editor || !firstShown) return
    let frame = 0
    const scrollToShown = () => {
      cancelAnimationFrame(frame)
      frame = requestAnimationFrame(() => {
        const top = wrapper.current?.getBoundingClientRect().top
        if (top === undefined) return
        window.scrollTo({ top: window.scrollY + top + editor.getTopForLineNumber(firstShown) - window.innerHeight * SHOWN_FROM_TOP, behavior: 'smooth' })
      })
    }
    scrollToShown()
    // A file just opened folds after it draws, which moves the line up: while the folds settle, the page follows it.
    const resizing = editor.onDidContentSizeChange(scrollToShown)
    const settled = setTimeout(() => resizing.dispose(), FOLDS_SETTLE_MILLISECONDS)
    return () => {
      cancelAnimationFrame(frame)
      clearTimeout(settled)
      resizing.dispose()
    }
  }, [editor, firstShown])
  const openedComment = file.comments.find(comment => comment.anchor === opened)
  return (
    <div className="file-source" ref={wrapper}>
      <div className="file-source-bar">
        {toggle}
        <button type="button" className={wrap ? 'file-wrap is-on' : 'file-wrap'} aria-pressed={wrap} title="Wrap long lines instead of scrolling sideways (shift+wheel)" onClick={toggleWrap}>
          Wrap lines
        </button>
      </div>
      <SourceView
        source={source}
        violation={violationFocusOf(file, rule)}
        rules={rules}
        activeRule={rule}
        onSelectRule={setChosenRule}
        onCorrect={actions.correct}
        openAround={shownAround}
        language={monacoLanguageOf(file)}
        keepGlyphMargin
        wordWrap={wrap}
        callouts={callouts}
        expandLines={expandLines}
        onGoToFile={onGoToFile}
        opensCalls={!isStoryTest(file)}
        onEditor={onEditor}
      />
      {composing ? <CommentComposerView lines={composing} actions={actions} place={placeUnder(editor, wrapper.current, composing.end)} onDone={() => setComposing(null)} /> : null}
      {openedComment ? <CommentCardView key={openedComment.anchor} comment={openedComment} actions={actions} place={placeUnder(editor, wrapper.current, openedComment.range.end_line)} onClose={() => setOpened('')} /> : null}
    </div>
  )
}
