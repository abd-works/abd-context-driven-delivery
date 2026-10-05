import React from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import './explorer.css';

const stored = window.localStorage.getItem('kg-theme');
if (stored === 'engineering') {
  document.documentElement.dataset.theme = 'engineering';
}

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
