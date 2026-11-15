import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import { FilesApi } from './files/files-api'
import { FilesLink } from './files/files-link'
import { FilesPage } from './files/files-page'
import { FilesFailureView, FilesPageView } from './files/files-page-view'
import { applyTheme, storedTheme } from './files/files-theme'
import './files.css'

// The page shows what its link names (files/files-link.ts), as the chat bar's files button and session name open it.
const page = new FilesPage(new FilesApi(), new FilesLink(window.location.search))
const lookFailed = (failure: string) => page.fail(failure, 'Opening the Files app in its look')
applyTheme(storedTheme(lookFailed), lookFailed)

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <FilesFailureView page={page}>
      <FilesPageView page={page} />
    </FilesFailureView>
  </StrictMode>,
)
