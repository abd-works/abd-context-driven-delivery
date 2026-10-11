import React, { Component, type ErrorInfo, type ReactNode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import './explorer.css';

class ExplorerErrorBoundary extends Component<{ children: ReactNode }, { error: string }> {
  state = { error: '' };

  static getDerivedStateFromError(error: Error) {
    return { error: error.message };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <main className="explore-knowledge-graph">
          <div className="knowledge-graph-explorer scan-error empty-state">
            <p>The explorer stopped rendering.</p>
            <pre>{this.state.error}</pre>
          </div>
        </main>
      );
    }
    return this.props.children;
  }
}

const stored = window.localStorage.getItem('kg-theme');
if (stored === 'engineering') {
  document.documentElement.dataset.theme = 'engineering';
}

createRoot(document.getElementById('root')!).render(
  <ExplorerErrorBoundary>
    <React.StrictMode>
      <App />
    </React.StrictMode>
  </ExplorerErrorBoundary>,
);
