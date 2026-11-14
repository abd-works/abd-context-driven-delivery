import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import '@src/kanban/board/board.css'
import { BoardPage } from '@src/kanban/board/board-page'
import { BoardPageView } from '@src/kanban/board/board-page-view'

// The board's page. Files open in the Files app (space/session/files_app), never here.
const page = new BoardPage()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BoardPageView page={page} />
  </StrictMode>,
)
