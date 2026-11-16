import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import '@src/kanban/board/board.css'
import { BoardPage } from '@src/kanban/board/board-page'
import { BoardPageView } from '@src/kanban/board/board-page-view'

// The board's page. Files open in the Files app (harness/files_app), never here.
const page = new BoardPage()

// A failure nothing on the page caught still reaches the page and the chat that opened it.
const UNCAUGHT = 'An uncaught failure in the Kanban board page'
window.addEventListener('error', event => page.failures.failWith(event.error ?? event.message, UNCAUGHT))
window.addEventListener('unhandledrejection', event => page.failures.failWith(event.reason, UNCAUGHT))

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BoardPageView page={page} />
  </StrictMode>,
)
