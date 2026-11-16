import React from 'react'
import { createRoot } from 'react-dom/client'

import { chatOfPage } from '@cdd/cdd-shared'

import './workspace.css'
import { StoryMapApi } from './story-map/story-map-api'
import { StoryMapFailures } from './story-map/story-map-failures'
import { StoryMapFailureView, StoryMapWorkspaceView } from './story-map/story-map-views'

// The page opens the Stories file its ?file= link names, as the chat bar's file viewer links it; with none it follows
// the story map of the session open in the project. Its ?chat= link names the chat it was opened beside, whose file
// viewer shows a story's acceptance tests, and which is told every failure the page meets.
const file = new URLSearchParams(window.location.search).get('file')
const failures = new StoryMapFailures(chatOfPage(), notTold => new StoryMapApi(notTold))

// A failure nothing on the page caught still reaches the page and the chat that opened it.
const UNCAUGHT = 'An uncaught failure in the Story UI page'
window.addEventListener('error', event => failures.failWith(event.error ?? event.message, UNCAUGHT))
window.addEventListener('unhandledrejection', event => failures.failWith(event.reason, UNCAUGHT))

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <StoryMapFailureView failures={failures}>
      <StoryMapWorkspaceView file={file} failures={failures} />
    </StoryMapFailureView>
  </React.StrictMode>,
)
