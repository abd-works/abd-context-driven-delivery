import React from 'react'
import { createRoot } from 'react-dom/client'

import './workspace.css'
import { StoryMapWorkspaceView } from './story-map/story-map-views'

// The page opens the Stories file its ?file= link names, as the chat bar's file viewer links it; with none it follows
// the story map of the session open in the project.
const file = new URLSearchParams(window.location.search).get('file')

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <StoryMapWorkspaceView file={file} />
  </React.StrictMode>,
)
