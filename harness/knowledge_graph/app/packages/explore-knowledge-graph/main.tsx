import React from 'react';
import { createRoot } from 'react-dom/client';
import { ExploreKnowledgeGraphView } from './ExploreKnowledgeGraphView';

const graphId = new URLSearchParams(window.location.search).get('id') ?? '';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ExploreKnowledgeGraphView graphId={graphId} />
  </React.StrictMode>,
);
