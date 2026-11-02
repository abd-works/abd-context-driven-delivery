import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import './board/board.css'
import { BoardPage } from './board/board-page'
import { BoardPageView } from './board/board-page-view'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BoardPageView page={new BoardPage()} />
  </StrictMode>,
)
