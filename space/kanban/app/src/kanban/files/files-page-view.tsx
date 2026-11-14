import { useEffect } from 'react'

import type { BoardPage } from '../board/board-page'
import { PageFailureView, ToastsView } from '../board/board-page-view'
import { BoardContext, useBoard } from '../shared/board-context'
import type { FilesPanel } from '../shared/board-store'
import { FilesPanelBodyView, FilesPanelHeadView } from '../ticket/files-panel-view'

// The Files app's page, an app of its own beside the chat: the file viewer alone, with its practice filters, comments
// and change marks, and none of the board. The chat bar's files button and session name open it at FILES_PAGE.
export const FILES_PAGE = '/files'

export const isFilesPage = (pathname: string): boolean => pathname === FILES_PAGE || pathname.startsWith(`${FILES_PAGE}/`)

function FilesBodyView() {
  const { page, state } = useBoard()
  useEffect(() => page.startFiles(), [page])
  const panel = state.panels.find((shown): shown is FilesPanel => shown.kind === 'files')
  return (
    <div className="board-root files-root">
      {panel ? (
        <aside className="report-root" data-panel="files" aria-label="files panel" style={{ flex: '1 1 0' }}>
          <header className="panel-head is-compact">
            <FilesPanelHeadView panel={panel} />
          </header>
          <FilesPanelBodyView panel={panel} />
        </aside>
      ) : (
        <div className="band" role="status">
          Opening files: the chat bar's files button or session name names the files to show.
        </div>
      )}
      <ToastsView />
    </div>
  )
}

export function FilesPageView({ page }: { page: BoardPage }) {
  return (
    <PageFailureView>
      <BoardContext.Provider value={page}>
        <FilesBodyView />
      </BoardContext.Provider>
    </PageFailureView>
  )
}
