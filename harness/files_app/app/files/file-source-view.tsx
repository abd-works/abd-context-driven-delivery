import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

import type { NodeSourceData } from '@cdd/harness/graph/graph'
import type { SessionFileData } from '@cdd/space/session/session'
import { SourceView, type SourceEditorInstance, type SourceLines } from '@source-view/SourceView'

import { CommentCardView, CommentComposerView } from './comment-box-view'
import { placeUnder, useAddCommentAction, useAddToContextAction, useFileMarks, useMarkerPresses } from './editor-comments'
import type { CommentLines, FileCommentsActions } from './file-comments-actions'
import { foldsOf, monacoLanguageOf, rulesOf, sourceOf, violationFocusOf } from './source-of-file'

// How far down the window the first line asked to show sits once the page scrolls to it.
const SHOWN_FROM_TOP = 1 / 3

// Whether long lines wrap is the reader's own choice, kept in their browser across files and visits.
const WRAP_KEY = 'files.wrap-lines'

function wrapChosen(): boolean {
  try {
    return localStorage.getItem(WRAP_KEY) === 'on'
  } catch {
    return false
  }
}

function keepWrap(wrap: boolean): void {
  try {
    localStorage.setItem(WRAP_KEY, wrap ? 'on' : 'off')
  } catch {
    // The choice still holds for this page; only the next visit forgets it.
  }
}

// The open file in the graph explorer's source view: folds from the session's graph, its broken rules as chips with the
// chosen one marked, and the comments on it: Add comment and Add to context on the right-click menu, a marker beside
// each comment's first line, and the box a marker opens.
// Lines asked to show, such as the nodes selected in the graph view, unfold and the page scrolls the first into view: the
// editor is as tall as the file, so the page scrolls, not the editor. Every other fold stays closed; with none asked,
// every fold starts open. Long lines scroll sideways, or wrap once the reader turns on Wrap lines. With the graph's members, once the graph view read them, a call opens in place even when it
// reaches another file.
export function FileSourceView({
  file,
  actions,
  onAddToContext,
  openAround = [],
  members = [],
}: {
  file: SessionFileData
  actions: FileCommentsActions
  onAddToContext: (lines: CommentLines) => void
  openAround?: SourceLines[]
  members?: NodeSourceData[]
}) {
  const wrapper = useRef<HTMLDivElement>(null)
  const held = useRef(file)
  held.current = file
  const [editor, setEditor] = useState<SourceEditorInstance | null>(null)
  const [chosenRule, setChosenRule] = useState('')
  const [composing, setComposing] = useState<CommentLines | null>(null)
  const [opened, setOpened] = useState('')
  const [wrap, setWrap] = useState(wrapChosen)
  const toggleWrap = useCallback(() => {
    setWrap(current => {
      keepWrap(!current)
      return !current
    })
  }, [])
  const source = useMemo(() => sourceOf(file, members), [file, members])
  const folds = useMemo(() => foldsOf(file), [file])
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
  const firstShown = openAround[0]?.start ?? 0
  useEffect(() => {
    if (!editor || !firstShown) return
    const frame = requestAnimationFrame(() => {
      const top = wrapper.current?.getBoundingClientRect().top
      if (top === undefined) return
      window.scrollTo({ top: window.scrollY + top + editor.getTopForLineNumber(firstShown) - window.innerHeight * SHOWN_FROM_TOP, behavior: 'smooth' })
    })
    return () => cancelAnimationFrame(frame)
  }, [editor, firstShown])
  const openedComment = file.comments.find(comment => comment.anchor === opened)
  return (
    <div className="file-source" ref={wrapper}>
      <div className="file-source-bar">
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
        folds={folds}
        unfolded
        openAround={openAround}
        language={monacoLanguageOf(file)}
        keepGlyphMargin
        wordWrap={wrap}
        onEditor={setEditor}
      />
      {composing ? <CommentComposerView lines={composing} actions={actions} place={placeUnder(editor, wrapper.current, composing.end)} onDone={() => setComposing(null)} /> : null}
      {openedComment ? <CommentCardView key={openedComment.anchor} comment={openedComment} actions={actions} place={placeUnder(editor, wrapper.current, openedComment.range.end_line)} onClose={() => setOpened('')} /> : null}
    </div>
  )
}
