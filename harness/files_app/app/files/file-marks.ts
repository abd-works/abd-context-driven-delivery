import type { editor as monaco } from 'monaco-editor'

import type { FileChangeData, FileCommentData, FileViolationData, SessionFileData } from '@cdd/space/session/session'
import { SOURCE_MARK } from '@source-view/SourceView'

export const COMMENT_MARKER = 'file-comment-marker'

export const STATE_WORDS: Record<FileCommentData['state'], string> = { not_sent: 'not sent', sent: 'sent', processed: 'processed' }
const CHANGE_WORDS: Record<FileChangeData['kind'], string> = { changed: 'Changed by the chat', added: 'Added by the chat', removed: 'Removed by the chat' }

type Decoration = monaco.IModelDeltaDecoration

const wholeLines = (start: number, end: number) => ({ startLineNumber: start, startColumn: 1, endLineNumber: Math.max(start, end), endColumn: 1 })

// A marker beside the first line of each comment, coloured by its state, with its words on hover.
function commentMarks(comments: FileCommentData[]): Decoration[] {
  return comments.map(comment => ({
    range: wholeLines(comment.range.start_line, comment.range.start_line),
    options: {
      glyphMarginClassName: `${SOURCE_MARK} ${COMMENT_MARKER} is-${comment.state}`,
      glyphMarginHoverMessage: { value: `**${comment.anchor}**, ${STATE_WORDS[comment.state]}\n\n${comment.text}` },
    },
  }))
}

// Every line a broken rule names, marked with the rule and its message on hover.
function violationMarks(violations: FileViolationData[]): Decoration[] {
  return violations.map(found => ({
    range: wholeLines(found.range.start_line, found.range.end_line),
    options: { isWholeLine: true, className: 'file-violation', hoverMessage: { value: `**${found.violation.rule}**: ${found.violation.message}` } },
  }))
}

// What the chat changed for its processed comments: the lines it changed or added, and where it removed lines, with
// the lines it replaced on hover.
function changeMarks(changes: FileChangeData[]): Decoration[] {
  return changes.map(change => {
    const removed = change.removed.length ? `\n\nReplaced:\n\n${change.removed.map(line => `    ${line}`).join('\n')}` : ''
    const lines = change.kind === 'removed' ? wholeLines(change.range.start_line, change.range.start_line) : wholeLines(change.range.start_line, change.range.end_line)
    return { range: lines, options: { isWholeLine: true, linesDecorationsClassName: `file-change is-${change.kind}`, hoverMessage: { value: `${CHANGE_WORDS[change.kind]}${removed}` } } }
  })
}

export function marksOf(file: SessionFileData): Decoration[] {
  return [...violationMarks(file.violations), ...changeMarks(file.changes), ...commentMarks(file.comments)]
}

// The comment whose marker sits beside line; the latest written when several start there.
export const commentAt = (file: SessionFileData, line: number): FileCommentData | undefined => file.comments.filter(comment => comment.range.start_line === line).at(-1)
