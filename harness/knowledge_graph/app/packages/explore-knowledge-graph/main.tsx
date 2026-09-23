import React from 'react';
import { createRoot } from 'react-dom/client';
import './monaco-host';
import { ExploreKnowledgeGraphView } from './ExploreKnowledgeGraphView';

const stored = window.localStorage.getItem('kg-theme');
if (stored === 'engineering') {
  document.documentElement.dataset.theme = 'engineering';
}

const graphId = new URLSearchParams(window.location.search).get('id') ?? '';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ExploreKnowledgeGraphView graphId={graphId} />
  </React.StrictMode>,
);
