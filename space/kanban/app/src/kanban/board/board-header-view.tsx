import { ChatMessagesView } from '../chat/chat-messages-view'
import { ChatPickerView } from '../chat/chat-picker-view'
import { useBoard } from '../shared/board-context'
import { BrandMark, ExpandIcon } from '../shared/icons'

function HeaderActionsView() {
  const { page, state } = useBoard()
  const isExpanded = state.expandedRegion === 'board'
  const label = isExpanded ? 'Collapse board' : 'Expand board'
  return (
    <>
      <button className="action" disabled={!page.chat.canSend} onClick={() => void page.openNewTicket()}>
        + Ticket
      </button>
      <button className="action" title="Open the knowledge graph on the active ticket, with every practice it works on" onClick={() => void page.graphApp.openOn(page.board.project)}>
        Graph
      </button>
      <button className="action" disabled={state.isUpdating} title="Get the latest code, rebuild the board, pin cdd to it, and reload this page" onClick={() => void page.update()}>
        {state.isUpdating ? 'Updating…' : 'Update'}
      </button>
      <button className="icon-button" aria-label={label} title={label} onClick={() => page.layout.toggleRegion('board')}>
        <ExpandIcon isExpanded={isExpanded} />
      </button>
    </>
  )
}

// The header's switches: Active session only for this page, Send fixes directly for the repository.
function HeaderSwitchesView() {
  const { page, state } = useBoard()
  const { board } = page
  return (
    <>
      <label className="header-field" title="Actions only run on the active session's ticket">
        <span>Active session only</span>
        <input type="checkbox" role="switch" className="practice-switch" checked={state.onlyActive} onChange={() => page.layout.toggleOnlyActive()} />
      </label>
      <label className="header-field" title="Off: a report's Fix goes into the chat's prompt for you to edit and send. On: it is sent to the chat directly.">
        <span>Send fixes directly</span>
        <input type="checkbox" role="switch" className="practice-switch" checked={board.sendsFixesDirectly} onChange={() => void board.setSendsFixesDirectly(!board.sendsFixesDirectly)} />
      </label>
    </>
  )
}

export function BoardHeaderView() {
  const { page } = useBoard()
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
      <ChatMessagesView />
      <HeaderSwitchesView />
      <HeaderActionsView />
    </header>
  )
}
