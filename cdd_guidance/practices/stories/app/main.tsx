import React from 'react'
import { createRoot } from 'react-dom/client'

import { chatOfPage } from '@cdd/cdd-shared'

import './workspace.css'
import { StoryMapWorkspaceView } from './story-map/story-map-views'

// The page opens the Stories file its ?file= link names, as the chat bar's file viewer links it; with none it follows
// the story map of the session open in the project. Its ?chat= link names the chat it was opened beside, whose file
// viewer shows a story's acceptance tests.
const file = new URLSearchParams(window.location.search).get('file')

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <StoryMapWorkspaceView file={file} chat={chatOfPage()} />
  </React.StrictMode>,
)
