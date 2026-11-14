import { useCallback, useMemo, useRef, useState } from 'react'

import type { SessionFileData } from '@cdd/space/session/session'
import { SourceView, type SourceEditorInstance } from '@source-view/SourceView'

import { CommentCardView, CommentComposerView } from './comment-box-view'
import { placeUnder, useAddCommentAction, useFileMarks, useMarkerPresses } from './editor-comments'
import type { CommentLines, FileCommentsActions } from './file-comments-actions'
import { foldsOf, monacoLanguageOf, rulesOf, sourceOf, violationFocusOf } from './source-of-file'

// The open file in the graph explorer's source view: folds from the session's graph, its broken rules as chips with the
// chosen one marked, and the comments on it: Add comment on the right-click menu, a marker beside each comment's first
// line, and the box a marker opens.
export function FileSourceView({ file, actions }: { file: SessionFileData; actions: FileCommentsActions }) {
  const wrapper = useRef<HTMLDivElement>(null)
  const held = useRef(file)
  held.current = file
  const [editor, setEditor] = useState<SourceEditorInstance | null>(null)
  const [chosenRule, setChosenRule] = useState('')
  const [composing, setComposing] = useState<CommentLines | null>(null)
  const [opened, setOpened] = useState('')
  const source = useMemo(() => sourceOf(file), [file])
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
  useFileMarks(editor, file)
  useMarkerPresses(editor, held, open)
  const openedComment = file.comments.find(comment => comment.anchor === opened)
  return (
    <div className="file-source" ref={wrapper}>
      <SourceView
        source={source}
        violation={violationFocusOf(file, rule)}
        rules={rules}
        activeRule={rule}
        onSelectRule={setChosenRule}
        folds={folds}
        unfolded
        language={monacoLanguageOf(file)}
        keepGlyphMargin
        onEditor={setEditor}
      />
      {composing ? <CommentComposerView lines={composing} actions={actions} place={placeUnder(editor, wrapper.current, composing.end)} onDone={() => setComposing(null)} /> : null}
      {openedComment ? <CommentCardView key={openedComment.anchor} comment={openedComment} actions={actions} place={placeUnder(editor, wrapper.current, openedComment.range.end_line)} onClose={() => setOpened('')} /> : null}
    </div>
  )
}
