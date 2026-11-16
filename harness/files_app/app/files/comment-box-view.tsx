import { useState, type CSSProperties, type KeyboardEvent } from 'react'

import type { FileCommentData } from '@cdd/space/session/file-comments'

import type { CommentLines, FileCommentsActions } from './file-comments-actions'
import { STATE_WORDS } from './file-marks'

const rangeWords = ({ start, end }: CommentLines): string => (start === end ? `line ${start}` : `lines ${start} to ${end}`)

// Enter finishes the comment, Shift+Enter starts a new line in it.
const isFinish = (event: KeyboardEvent): boolean => event.key === 'Enter' && !event.shiftKey

// The box a new comment is written in, at the selection: Enter keeps it and adds it to the chat's queue.
export function CommentComposerView({ lines, actions, place, onDone }: { lines: CommentLines; actions: FileCommentsActions; place: CSSProperties; onDone: () => void }) {
  const [text, setText] = useState('')
  const finish = () => void actions.addAndSend(lines, text).then(onDone)
  return (
    <div className="comment-box" style={place} role="group" aria-label="New comment">
      <div className="comment-box-head">Comment on {rangeWords(lines)}</div>
      <textarea
        aria-label="Comment"
        autoFocus
        value={text}
        placeholder="Enter adds it to the chat's queue; Shift+Enter starts a new line"
        onChange={event => setText(event.target.value)}
        onKeyDown={event => {
          if (event.key === 'Escape') onDone()
          if (!isFinish(event)) return
          event.preventDefault()
          finish()
        }}
      />
      <div className="comment-actions">
        <button disabled={!text.trim()} onClick={finish}>
          Add and send
        </button>
        <button disabled={!text.trim()} onClick={() => void actions.add(lines, text).then(onDone)}>
          Add
        </button>
        <button onClick={onDone}>Cancel</button>
      </div>
    </div>
  )
}

// A comment its marker opened, under its lines: its words, which can be edited and saved, its state, and Delete.
export function CommentCardView({ comment, actions, place, onClose }: { comment: FileCommentData; actions: FileCommentsActions; place: CSSProperties; onClose: () => void }) {
  const [text, setText] = useState(comment.text)
  const isEdited = text.trim() !== comment.text
  return (
    <div
      className="comment-box"
      style={place}
      role="group"
      aria-label={`Comment on ${comment.anchor}`}
      tabIndex={-1}
      onKeyDown={event => {
        if (event.key === 'Escape') onClose()
        if (event.key === 'Delete' && !(event.target instanceof HTMLTextAreaElement)) void actions.remove(comment.anchor).then(onClose)
      }}
    >
      <div className="comment-box-head">
        <span>{comment.anchor}</span>
        <span className={`comment-state is-${comment.state}`}>{STATE_WORDS[comment.state]}</span>
      </div>
      <textarea
        aria-label="Comment"
        value={text}
        onChange={event => setText(event.target.value)}
        onKeyDown={event => {
          if (!isFinish(event)) return
          event.preventDefault()
          if (isEdited) void actions.editAndSend(comment.anchor, text).then(onClose)
          else if (comment.state === 'not_sent') void actions.send(comment.anchor).then(onClose)
          else onClose()
        }}
      />
      <div className="comment-actions">
        <button disabled={!isEdited || !text.trim()} onClick={() => void actions.edit(comment.anchor, text)}>
          Save
        </button>
        {comment.state === 'not_sent' ? <button onClick={() => void actions.send(comment.anchor)}>Send</button> : null}
        <button onClick={() => void actions.remove(comment.anchor).then(onClose)}>Delete</button>
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  )
}
