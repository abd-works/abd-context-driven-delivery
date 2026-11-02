import { useEffect } from 'react'

import { ActivationView } from '../ticket/activation-view'
import { DetailsView } from '../ticket/details-view'
import type { TicketClient } from '../ticket/ticket-client'
import { BoardColumnsView } from './board-columns-view'
import { BoardContext, useBoard } from './board-context'
import { BoardHeaderView } from './board-header-view'
import type { BoardPage } from './board-page'
import { useDragGrip } from './drag-grip'
import { SidePanelsView } from './side-panels-view'

function ServerBandView({ failure, hasBoard }: { failure: string; hasBoard: boolean }) {
  const consequence = hasBoard ? 'this board may be out of date. It reads again every two seconds' : 'there is no board to show yet. It tries again every two seconds'
  return (
    <div className="band band-failure" role="alert">
      cdd is not connected, so {consequence} · {failure}
    </div>
  )
}

function ViolationsBandView({ ticket }: { ticket: TicketClient }) {
  const { page } = useBoard()
  const isOff = !page.chat.canSend
  return (
    <div className="band" role="status" aria-label="Active ticket's violations">
      <span className="band-words">
        {ticket.name} · {ticket.column} · violations: {ticket.violations.join(', ')}
      </span>
      <button className="action" disabled={isOff} onClick={() => void ticket.fillShowViolations()}>
        Show
      </button>
      <button className="action primary" disabled={isOff} onClick={() => void ticket.fillSatisfy()}>
        Satisfy
      </button>
    </div>
  )
}

function BandsView() {
  const { page, state } = useBoard()
  const active = page.board.activeTicket
  return (
    <>
      {state.serverFailure ? <ServerBandView failure={state.serverFailure} hasBoard={state.board !== null} /> : null}
      {active?.violations.length ? <ViolationsBandView ticket={active} /> : null}
    </>
  )
}

function SplitGripView() {
  const { page, state } = useBoard()
  const grip = useDragGrip(
    'y',
    () => state.boardHeight,
    (height, distance, element) => page.layout.setBoardHeight(height + distance, element.closest('main')?.clientHeight ?? 0),
  )
  return (
    <div className="split-bar">
      <button className="grip" aria-label="Drag to resize the board and the details" {...grip}>
        <span className="grip-line" />
      </button>
    </div>
  )
}

function ToastsView() {
  const { state } = useBoard()
  return (
    <div className="toasts">
      {state.toasts.map(toast => (
        <div key={toast.id} role="status" className={toast.isFailure ? 'toast toast-failure' : 'toast'}>
          {toast.text}
        </div>
      ))}
    </div>
  )
}

function MainView() {
  const { state } = useBoard()
  const isCovered = state.panels.some(panel => panel.isExpanded)
  const { expandedRegion } = state
  return (
    <main className={isCovered ? 'board-main is-covered' : 'board-main'}>
      <BoardHeaderView />
      {expandedRegion !== 'details' ? <BoardColumnsView /> : null}
      {expandedRegion ? null : <SplitGripView />}
      {expandedRegion !== 'board' ? <DetailsView /> : null}
    </main>
  )
}

function PageBodyView() {
  const { page } = useBoard()
  useEffect(() => page.start(), [page])
  return (
    <div className="board-root">
      <BandsView />
      <div className="page-body">
        <MainView />
        <SidePanelsView />
      </div>
      <ActivationView />
      <ToastsView />
    </div>
  )
}

export function BoardPageView({ page }: { page: BoardPage }) {
  return (
    <BoardContext.Provider value={page}>
      <PageBodyView />
    </BoardContext.Provider>
  )
}
