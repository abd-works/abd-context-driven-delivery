import type { ChatMessageData } from '@cdd/tools/chat/chat'

import { useBoard } from '../board/board-context'

const MILLISECONDS_PER_SECOND = 1000

const sentTime = (message: ChatMessageData): string => new Date(message.sent_at * MILLISECONDS_PER_SECOND).toLocaleTimeString()

// What each state means to the person, who reads it to know whether to look in the chat.
const STATE_WORDS: Record<ChatMessageData['state'], string> = {
  waiting: 'waiting for the chat',
  taken: 'taken, not shown yet',
  shown: 'running',
  done: '✓ done',
  failed: 'failed',
}

// A shown fill sits in the prompt box for the person to send, so only a command or a submit is running in the chat.
const isRunning = (message: ChatMessageData): boolean => message.state === 'shown' && message.kind !== 'fill'

function ChatMessageStateView({ message }: { message: ChatMessageData }) {
  if (message.state === 'shown' && message.kind === 'fill') return <span className="chat-message-state">in the prompt box</span>
  return (
    <span className="chat-message-state">
      {isRunning(message) ? <span className="progress-wheel" aria-hidden="true" /> : null}
      {STATE_WORDS[message.state]}
    </span>
  )
}

// A message the chat took and never showed, or failed to show, can go to the chat again.
const UNSHOWN_STATES: ChatMessageData['state'][] = ['taken', 'failed']

function ChatMessageView({ message }: { message: ChatMessageData }) {
  const { page } = useBoard()
  return (
    <li className={`chat-message is-${message.state}`}>
      <div className="chat-message-head">
        <span className="chat-message-kind">{message.kind}</span>
        <ChatMessageStateView message={message} />
        <span className="chat-message-time">{sentTime(message)}</span>
        {UNSHOWN_STATES.includes(message.state) ? (
          <button className="chat-message-button" title="Put it back in the chat's queue" onClick={() => void page.chat.resend(message.message)}>
            Resend
          </button>
        ) : null}
        <button className="chat-message-button" title="Remove it from the list; a waiting message never reaches the chat" onClick={() => void page.chat.remove(message.message)}>
          Remove
        </button>
      </div>
      <code className="chat-message-text">{message.text}</code>
      {message.reason ? <div className="chat-message-reason">{message.reason}</div> : null}
    </li>
  )
}

// What the board has sent the chosen chat, newest first, so a person can see what ran and what still waits.
export function ChatMessagesView() {
  const { page, state } = useBoard()
  if (!state.targetChat) return null
  const waiting = state.messages.filter(message => message.state === 'waiting' || message.state === 'taken').length
  const failed = state.messages.filter(message => message.state === 'failed').length
  const running = state.messages.filter(isRunning).length
  const counts = [running ? `${running} running` : '', waiting ? `${waiting} waiting` : '', failed ? `${failed} failed` : ''].filter(Boolean)
  return (
    <div className="chat-messages">
      <button className={failed ? 'action is-failing' : 'action'} aria-expanded={state.isMessagesOpen} onClick={() => page.chat.toggleMessages()}>
        {running ? <span className="progress-wheel" aria-hidden="true" /> : null}
        {['Messages', ...counts].join(' · ')}
      </button>
      {state.isMessagesOpen ? (
        <ul className="chat-message-list" aria-label="Messages sent to the chat">
          {state.messages.length ? state.messages.map((message, index) => <ChatMessageView key={`${message.sent_at}-${index}`} message={message} />) : <li className="chat-message-empty">Nothing sent to this chat yet</li>}
        </ul>
      ) : null}
    </div>
  )
}
