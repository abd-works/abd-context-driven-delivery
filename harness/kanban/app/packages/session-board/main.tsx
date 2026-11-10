import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import '@src/kanban/board/board.css'
import { BoardPage } from '@src/kanban/board/board-page'
import { BoardPageView } from '@src/kanban/board/board-page-view'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BoardPageView page={new BoardPage()} />
  </StrictMode>,
)
