import { useBoard } from '../shared/board-context'

export function ChatPickerView() {
  const { page, state } = useBoard()
  if (!state.chats.length) return <span className="chat-missing">No chat connected: load the cdd-board mod in a chat to send commands</span>
  return (
    <label className="header-field">
      <span>Chat</span>
      <select className="chat-picker" aria-label="Chat to send commands to" value={state.targetChat ?? ''} onChange={event => page.chat.choose(event.target.value)}>
        {state.targetChat ? null : <option value="">Pick a chat</option>}
        {state.chats.map(chat => {
          const shown = page.chatName(chat)
          return (
            <option key={chat.id} value={chat.id} title={chat.id}>
              {chat.is_busy ? `${shown} (busy)` : shown}
            </option>
          )
        })}
      </select>
    </label>
  )
}
