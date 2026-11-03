import type { ChatMessageData } from '@cdd/tools/chat/chat'

import { useBoard } from '../board/board-context'

const MILLISECONDS_PER_SECOND = 1000

const sentTime = (message: ChatMessageData): string => new Date(message.sent_at * MILLISECONDS_PER_SECOND).toLocaleTimeString()

function ChatMessageView({ message }: { message: ChatMessageData }) {
  return (
    <li className={message.is_waiting ? 'chat-message is-waiting' : 'chat-message'}>
      <div className="chat-message-head">
        <span className="chat-message-kind">{message.kind}</span>
        <span className="chat-message-state">{message.is_waiting ? 'waiting' : 'delivered'}</span>
        <span className="chat-message-time">{sentTime(message)}</span>
      </div>
      <code className="chat-message-text">{message.text}</code>
    </li>
  )
}

// What the board has sent the chosen chat, newest first, so a person can see what ran and what still waits.
export function ChatMessagesView() {
  const { page, state } = useBoard()
  if (!state.targetChat) return null
  const waiting = state.messages.filter(message => message.is_waiting).length
  return (
    <div className="chat-messages">
      <button className="action" aria-expanded={state.isMessagesOpen} onClick={() => page.chat.toggleMessages()}>
        Messages{waiting ? ` · ${waiting} waiting` : ''}
      </button>
      {state.isMessagesOpen ? (
        <ul className="chat-message-list" aria-label="Messages sent to the chat">
          {state.messages.length ? state.messages.map((message, index) => <ChatMessageView key={`${message.sent_at}-${index}`} message={message} />) : <li className="chat-message-empty">Nothing sent to this chat yet</li>}
        </ul>
      ) : null}
    </div>
  )
}
