import { useBoard } from './board-context'
import { BrandMark, ExpandIcon } from './icons'

function ChatPickerView() {
  const { page, state } = useBoard()
  if (!state.chats.length) return <span className="chat-missing">No chat connected: load the cdd-board mod in a chat to send commands</span>
  return (
    <label className="header-field">
      <span>Chat</span>
      <select className="chat-picker" aria-label="Chat to send commands to" value={state.targetChat ?? ''} onChange={event => page.chat.choose(event.target.value)}>
        {state.targetChat ? null : <option value="">Pick a chat</option>}
        {state.chats.map(chat => (
          <option key={chat.id} value={chat.id}>
            {chat.isBusy ? `${chat.id} (busy)` : chat.id}
          </option>
        ))}
      </select>
    </label>
  )
}

export function BoardHeaderView() {
  const { page, state } = useBoard()
  const isExpanded = state.expandedRegion === 'board'
  const label = isExpanded ? 'Collapse board' : 'Expand board'
  return (
    <header className="board-header">
      <BrandMark />
      <span className="wordmark">
        BOARD<span className="accent-mark">_</span>
      </span>
      <span className="header-meta">
        {page.board.project} · {page.board.ticketCount} tickets · active: <span className="header-active">{page.board.activeTicket?.title ?? 'none'}</span>
      </span>
      <ChatPickerView />
      <label className="header-field" title="Actions only run on the active session's ticket">
        <span>Active session only</span>
        <input type="checkbox" role="switch" className="practice-switch" checked={state.onlyActive} onChange={() => page.board.toggleOnlyActive()} />
      </label>
      <button className="action" disabled={!page.chat.canSend} onClick={() => void page.openNewTicket()}>
        + Ticket
      </button>
      <button className="action" onClick={() => void page.board.refreshPressed()}>
        Refresh
      </button>
      <button className="icon-button" aria-label={label} title={label} onClick={() => page.board.toggleRegion('board')}>
        <ExpandIcon isExpanded={isExpanded} />
      </button>
    </header>
  )
}
