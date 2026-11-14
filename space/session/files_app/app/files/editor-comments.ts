import { useEffect, type CSSProperties, type RefObject } from 'react'

import type { SessionFileData } from '@cdd/space/session/session'
import type { SourceEditorInstance } from '@source-view/SourceView'

import type { CommentLines } from './file-comments-actions'
import { COMMENT_MARKER, commentAt, marksOf } from './file-marks'

export const ADD_COMMENT_ACTION = 'files.add-comment'
// Monaco's MouseTargetType.GUTTER_GLYPH_MARGIN: a press on the gutter where the markers sit.
const GLYPH_MARGIN = 2
const BOX_INDENT = 8

type SelectingEditor = Pick<SourceEditorInstance, 'getSelection' | 'getPosition'>

// The selected lines; a selection that ends at the very start of a line does not take that line.
function selectedLines(editor: SelectingEditor): CommentLines {
  const selection = editor.getSelection()
  const line = editor.getPosition()?.lineNumber ?? 1
  if (!selection) return { start: line, end: line }
  const end = selection.endColumn === 1 && selection.endLineNumber > selection.startLineNumber ? selection.endLineNumber - 1 : selection.endLineNumber
  return { start: selection.startLineNumber, end }
}

// Add comment on the editor's right-click menu: it opens a comment box at the selection.
export function useAddCommentAction(editor: SourceEditorInstance | null, onCompose: (lines: CommentLines) => void): void {
  useEffect(() => {
    if (!editor) return
    const action = editor.addAction({ id: ADD_COMMENT_ACTION, label: 'Add comment', contextMenuGroupId: 'navigation', contextMenuOrder: 0, run: shown => onCompose(selectedLines(shown)) })
    return () => action.dispose()
  }, [editor, onCompose])
}

// The file's comment markers, violation marks and the chat's changes, drawn again each time the file is read.
export function useFileMarks(editor: SourceEditorInstance | null, file: SessionFileData): void {
  useEffect(() => {
    if (!editor) return
    const marks = editor.createDecorationsCollection(marksOf(file))
    return () => marks.clear()
  }, [editor, file])
}

// A press on a comment's marker opens that comment, or closes it when it is the one open.
export function useMarkerPresses(editor: SourceEditorInstance | null, file: RefObject<SessionFileData>, onOpen: (anchor: string) => void): void {
  useEffect(() => {
    if (!editor) return
    const listening = editor.onMouseDown(event => {
      const line = event.target.position?.lineNumber
      const isMarker = event.target.type === GLYPH_MARGIN && Boolean(event.target.element?.classList.contains(COMMENT_MARKER))
      const comment = isMarker && line && file.current ? commentAt(file.current, line) : undefined
      if (comment) onOpen(comment.anchor)
    })
    return () => listening.dispose()
  }, [editor, file, onOpen])
}

// Where a comment box sits on the page: under the last of its lines, over the code, inside the wrapper around the view.
export function placeUnder(editor: SourceEditorInstance | null, wrapper: HTMLElement | null, line: number): CSSProperties {
  const shown = editor?.getDomNode()
  if (!editor || !shown || !wrapper) return { top: 0, left: 0 }
  const editorTop = shown.getBoundingClientRect().top - wrapper.getBoundingClientRect().top
  const lineHeight = editor.getBottomForLineNumber(line) - editor.getTopForLineNumber(line)
  const top = editorTop + editor.getTopForLineNumber(line) + lineHeight - editor.getScrollTop()
  return { top, left: editor.getLayoutInfo().contentLeft + BOX_INDENT }
}
