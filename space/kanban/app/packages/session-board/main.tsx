import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import '@src/kanban/board/board.css'
import { BoardPage } from '@src/kanban/board/board-page'
import { BoardPageView } from '@src/kanban/board/board-page-view'
import { FilesPageView, isFilesPage } from '@src/kanban/files/files-page-view'

// One build answers two apps: the Files app at its own page shows the file viewer alone, and every other page the board.
const page = new BoardPage()

createRoot(document.getElementById('root')!).render(
  <StrictMode>{isFilesPage(location.pathname) ? <FilesPageView page={page} /> : <BoardPageView page={page} />}</StrictMode>,
)
