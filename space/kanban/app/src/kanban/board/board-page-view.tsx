import { Component, useEffect } from 'react'
import type { ReactNode } from 'react'

import { ActivationView } from '../ticket/activation-view'
import { RootChoiceView } from '../ticket/root-choice-view'
import { DetailsView } from '../ticket/details-view'
import type { TicketClient } from '../ticket/ticket-client'
import { BoardColumnsView } from './board-columns-view'
import { BoardContext, useBoard } from '../shared/board-context'
import { BoardHeaderView } from './board-header-view'
import type { BoardPage } from './board-page'
import { BOARD_SERVER_DOWN } from './board-api'
import { useDragGrip } from './drag-grip'
import { SidePanelsView } from './side-panels-view'

// A server that is down answers with whatever its process printed, often a whole Python traceback, whose last line names
// the exception; the band shows that one line and keeps the rest behind Details.
export function headlineOf(failure: string): string {
  const lines = failure.split('\n').map(line => line.trim()).filter(Boolean)
  return (lines[0]?.startsWith('Traceback') ? lines.at(-1) : lines[0]) ?? ''
}

// What starts the server that is not answering: the board's own server, or the cdd server behind it.
const startingOf = (failure: string): string =>
  failure === BOARD_SERVER_DOWN ? "The session board server is not answering: open the Kanban from the chat bar's status row to start it." : 'The cdd server is not answering: start it again with /cdd-restart in a chat, or open the Kanban from the chat bar.'

function ServerBandView({ failure }: { failure: string }) {
  const headline = headlineOf(failure)
  return (
    <div className="band band-failure" role="alert">
      {startingOf(failure)} The board shows no columns until it answers, and tries again every two seconds · {headline}
      {headline !== failure.trim() ? (
        <details className="band-details">
          <summary>Details</summary>
          <pre>{failure}</pre>
        </details>
      ) : null}
    </div>
  )
}

// A change git refused to save on main is still on disk and on the board, but no other chat or checkout sees it until it
// is saved; the band names the changes and saves them again.
function UnsavedBandView({ changes, error }: { changes: string[]; error: string }) {
  const { page } = useBoard()
  return (
    <div className="band band-failure" role="alert" aria-label="Changes not saved">
      Not saved on main: {changes.join('; ')} · {headlineOf(error)}
      <button className="action" onClick={() => void page.board.saveAgain()}>
        Save again
      </button>
    </div>
  )
}

function ViolationsBandView({ ticket }: { ticket: TicketClient }) {
  return (
    <div className="band" role="status" aria-label="Active ticket's violations">
      <span className="band-words">
        {ticket.name} · {ticket.column.name} · violations: {ticket.violatedSlugs.join(', ')}
      </span>
    </div>
  )
}

function BandsView() {
  const { page, state } = useBoard()
  if (state.serverFailure) return <ServerBandView failure={state.serverFailure} />
  const active = page.board.activeTicket
  return (
    <>
      {page.board.unsaved ? <UnsavedBandView changes={page.board.unsaved.changes} error={page.board.unsaved.error} /> : null}
      {active?.violatedSlugs.length ? <ViolationsBandView ticket={active} /> : null}
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
  const { expandedRegion, serverFailure } = state
  return (
    <main className={isCovered ? 'board-main is-covered' : 'board-main'}>
      <BoardHeaderView />
      {expandedRegion !== 'details' ? <BoardColumnsView /> : null}
      {expandedRegion ? null : <SplitGripView />}
      {expandedRegion !== 'board' && !serverFailure ? <DetailsView /> : null}
    </main>
  )
}

function PageBodyView() {
  const { page, state } = useBoard()
  useEffect(() => page.start(), [page])
  // A page left open across a rebuild loads the new build, so it never shows the old code.
  useEffect(() => {
    if (state.isNewBuild) globalThis.location.reload()
  }, [state.isNewBuild])
  return (
    <div className="board-root">
      <BandsView />
      <div className="page-body">
        <MainView />
        <SidePanelsView />
      </div>
      <ActivationView />
      <RootChoiceView />
      <ToastsView />
    </div>
  )
}

// A view that throws would otherwise leave an empty black page, so the person sees what broke and can read the board again.
class PageFailureView extends Component<{ children: ReactNode }, { failure: string }> {
  state = { failure: '' }

  static getDerivedStateFromError(error: unknown) {
    return { failure: error instanceof Error ? error.message : String(error) }
  }

  render() {
    if (!this.state.failure) return this.props.children
    return (
      <div className="band band-failure" role="alert">
        The board page failed: {this.state.failure}
        <button className="action" onClick={() => location.reload()}>
          Reload
        </button>
      </div>
    )
  }
}

export function BoardPageView({ page }: { page: BoardPage }) {
  return (
    <PageFailureView>
      <BoardContext.Provider value={page}>
        <PageBodyView />
      </BoardContext.Provider>
    </PageFailureView>
  )
}
