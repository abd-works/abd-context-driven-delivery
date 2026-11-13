import { useEffect, useRef, useState } from 'react'
import type { MouseEvent } from 'react'

import type { FileCommentData, FileViolationData, FoldData, SessionFileData } from '@cdd/space/session/session'

import { useBoard } from '../shared/board-context'
import { markdownBlocksOf } from '../shared/markdown-text'
import { MarkdownView } from '../shared/markdown-view'

const NOT_GENERATED = ['Not generated yet.', 'Pick this format on the card, then generate or render it.']
// While a comment is with a chat, the file is read again this often, so the chat's change and the comment's processed
// state show without a reload.
const SENT_REFRESH_MILLISECONDS = 2_000
const STATE_WORDS: Record<FileCommentData['state'], string> = { not_sent: 'not sent', sent: 'sent', processed: 'processed' }

type Lines = { start: number; end: number }

const foldKey = (fold: FoldData): string => `${fold.name}:${fold.range.start_line}-${fold.range.end_line}`
const isMarkdown = (file: SessionFileData): boolean => file.language === 'markdown' || file.path.endsWith('.md')
const covers = (lines: Lines | null, line: number): boolean => Boolean(lines && line >= lines.start && line <= lines.end)
const rangeWords = ({ start, end }: Lines): string => (start === end ? `line ${start}` : `lines ${start} to ${end}`)

// A line is hidden when a closed fold holds it below the fold's own first line.
const isFolded = (folds: FoldData[], closed: string[], line: number): boolean =>
  folds.some(fold => closed.includes(foldKey(fold)) && line > fold.range.start_line && line <= fold.range.end_line)

function CommentMarkerView({ comment, onOpen }: { comment: FileCommentData; onOpen: () => void }) {
  return (
    <button className={`comment-marker is-${comment.state}`} aria-label={`Comment on ${comment.anchor}, ${STATE_WORDS[comment.state]}`} title={comment.text} onClick={onOpen}>
      ●
    </button>
  )
}

function FoldToggleView({ fold, isClosed, onToggle }: { fold: FoldData; isClosed: boolean; onToggle: () => void }) {
  const words = `${isClosed ? 'Unfold' : 'Fold'} ${fold.name}, lines ${fold.range.start_line} to ${fold.range.end_line}`
  return (
    <button className={`fold-toggle is-${fold.kind}`} aria-label={words} aria-expanded={!isClosed} title={words} onClick={onToggle}>
      {isClosed ? '▸' : '▾'}
    </button>
  )
}

// The comment a marker opened, under its lines: its words and state, and what a person can do with it.
function CommentCardView({ comment, onClose }: { comment: FileCommentData; onClose: () => void }) {
  const { page } = useBoard()
  return (
    <div className="comment-card" role="group" aria-label={`Comment on ${comment.anchor}`}>
      <div className="comment-card-head">
        <span>{comment.anchor}</span>
        <span className={`comment-state is-${comment.state}`}>{STATE_WORDS[comment.state]}</span>
      </div>
      <p className="comment-text">{comment.text}</p>
      <div className="comment-actions">
        {comment.state === 'not_sent' ? <button onClick={() => void page.files.sendComment(comment.anchor)}>Send</button> : null}
        <button onClick={() => void page.files.removeComment(comment.anchor).then(onClose)}>Delete</button>
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  )
}

function CommentComposerView({ lines, onDone }: { lines: Lines; onDone: () => void }) {
  const { page } = useBoard()
  const [text, setText] = useState('')
  return (
    <div className="comment-card" role="group" aria-label="New comment">
      <div className="comment-card-head">Comment on {rangeWords(lines)}</div>
      <textarea aria-label="Comment" autoFocus value={text} onChange={event => setText(event.target.value)} />
      <div className="comment-actions">
        <button disabled={!text.trim()} onClick={() => void page.files.addComment(lines.start, lines.end, text.trim()).then(onDone)}>
          Add comment
        </button>
        <button onClick={onDone}>Cancel</button>
      </div>
    </div>
  )
}

function ViolationNoteView({ found }: { found: FileViolationData }) {
  return (
    <div className="violation-note" role="note">
      <strong>{found.violation.rule}</strong>: {found.violation.message}
    </div>
  )
}

type CodeState = {
  closed: string[]
  selected: Lines | null
  composing: Lines | null
  opened: string
}

// The file's numbered lines: a fold toggle where a class or member starts, a marker beside each comment's first line,
// and the lines a broken rule names marked with it. A click on a line number selects it; shift extends the selection.
function CodeLinesView({ file, marked }: { file: SessionFileData; marked: number }) {
  const markedLine = useRef<HTMLDivElement>(null)
  const [state, setState] = useState<CodeState>({ closed: [], selected: null, composing: null, opened: '' })
  const change = (changes: Partial<CodeState>) => setState(current => ({ ...current, ...changes }))
  // Braces matter: newer browsers return a promise from scrollIntoView, and React would call it as the effect's cleanup.
  useEffect(() => {
    markedLine.current?.scrollIntoView({ block: 'center' })
  }, [marked, file.path])
  const select = (line: number) => (event: MouseEvent) => {
    const from = event.shiftKey && state.selected ? state.selected.start : line
    change({ selected: { start: Math.min(from, line), end: Math.max(from, line) } })
  }
  const compose = (line: number) => (event: MouseEvent) => {
    event.preventDefault()
    change({ composing: covers(state.selected, line) ? state.selected : { start: line, end: line } })
  }
  const toggle = (fold: FoldData) => change({ closed: state.closed.includes(foldKey(fold)) ? state.closed.filter(key => key !== foldKey(fold)) : [...state.closed, foldKey(fold)] })
  return (
    <div className="file-lines">
      {state.selected && !state.composing ? (
        <div className="selection-bar">
          <span>Selected {rangeWords(state.selected)}</span>
          <button onClick={() => change({ composing: state.selected })}>Comment</button>
        </div>
      ) : null}
      {file.text.split('\n').map((text, index) => {
        const line = index + 1
        if (isFolded(file.folds, state.closed, line)) return null
        const folds = file.folds.filter(fold => fold.range.start_line === line)
        const comments = file.comments.filter(comment => comment.range.start_line === line)
        const broken = file.violations.filter(found => line >= found.range.start_line && line <= found.range.end_line)
        const opened = comments.find(comment => comment.anchor === state.opened)
        const classes = ['code-line', line === marked ? 'is-failing' : '', broken.length ? 'is-violated' : '', covers(state.selected, line) ? 'is-selected' : ''].filter(Boolean).join(' ')
        return (
          <div key={line} className="code-row" data-line={line}>
            <div ref={line === marked ? markedLine : undefined} className={classes} title={broken.map(found => `${found.violation.rule}: ${found.violation.message}`).join('\n') || undefined} onContextMenu={compose(line)}>
              <span className="line-gutter">
                {comments.map(comment => (
                  <CommentMarkerView key={comment.anchor} comment={comment} onOpen={() => change({ opened: state.opened === comment.anchor ? '' : comment.anchor })} />
                ))}
              </span>
              <button className="line-number" aria-label={`Line ${line}`} onClick={select(line)}>
                {line}
              </button>
              <span className="fold-gutter">
                {folds.slice(0, 1).map(fold => (
                  <FoldToggleView key={foldKey(fold)} fold={fold} isClosed={state.closed.includes(foldKey(fold))} onToggle={() => toggle(fold)} />
                ))}
              </span>
              <span className="line-text">{text}</span>
              {folds.some(fold => state.closed.includes(foldKey(fold))) ? <span className="fold-rest">⋯</span> : null}
            </div>
            {file.violations.filter(found => found.range.start_line === line).map(found => (
              <ViolationNoteView key={`${found.violation.rule}:${found.range.anchor}`} found={found} />
            ))}
            {opened ? <CommentCardView comment={opened} onClose={() => change({ opened: '' })} /> : null}
            {state.composing?.end === line ? <CommentComposerView lines={state.composing} onDone={() => change({ composing: null, selected: null })} /> : null}
          </div>
        )
      })}
    </div>
  )
}

// The open file's actions along the top left: send every open comment, clear the processed ones, and edit then save.
function FileToolbarView({ file, editing, onEdit }: { file: SessionFileData; editing: string | null; onEdit: (text: string | null) => void }) {
  const { page } = useBoard()
  const open = file.comments.filter(comment => comment.state === 'not_sent').length
  const processed = file.comments.filter(comment => comment.state === 'processed').length
  return (
    <div className="file-toolbar">
      <button disabled={!open} onClick={() => void page.files.sendOpenComments()}>
        Send all open comments
      </button>
      <button disabled={!processed} onClick={() => void page.files.clearProcessedComments()}>
        Clear processed comments
      </button>
      <span className="toolbar-gap" />
      {editing === null ? (
        <button onClick={() => onEdit(file.text)}>Edit</button>
      ) : (
        <>
          <button onClick={() => void page.files.save(editing).then(() => onEdit(null))}>Save</button>
          <button onClick={() => onEdit(null)}>Cancel</button>
        </>
      )}
    </div>
  )
}

// The open file: markdown drawn as its page, any other file as numbered lines; read-only until a person edits it.
export function FileViewerView({ file, marked }: { file: SessionFileData | null; marked: number }) {
  const { page } = useBoard()
  const [editing, setEditing] = useState<string | null>(null)
  const [isSource, setSource] = useState(false)
  const isSent = Boolean(file?.comments.some(comment => comment.state === 'sent'))
  useEffect(() => {
    if (!isSent) return
    const timer = setInterval(() => void page.files.refreshShown(), SENT_REFRESH_MILLISECONDS)
    return () => clearInterval(timer)
  }, [isSent, page])
  useEffect(() => setEditing(null), [file?.path])
  if (!file) return <div className="file-lines">{NOT_GENERATED.map(line => <p key={line} className="panel-note">{line}</p>)}</div>
  // A file opened at a failing line shows its numbered lines, so the line is marked; markdown is a page otherwise.
  const asPage = isMarkdown(file) && !isSource && !marked && editing === null
  return (
    <div className="file-viewer" data-language={file.language}>
      <FileToolbarView file={file} editing={editing} onEdit={setEditing} />
      {isMarkdown(file) && !marked && editing === null ? (
        <button className="source-toggle" onClick={() => setSource(!isSource)}>
          {isSource ? 'Show as page' : 'Show source'}
        </button>
      ) : null}
      {editing !== null ? <textarea className="file-editor" aria-label={`Edit ${file.path}`} value={editing} onChange={event => setEditing(event.target.value)} /> : null}
      {asPage ? (
        <div className="markdown-page">
          <MarkdownView blocks={markdownBlocksOf(file.text)} className="markdown-text" />
        </div>
      ) : null}
      {!asPage && editing === null ? <CodeLinesView file={file} marked={marked} /> : null}
    </div>
  )
}
