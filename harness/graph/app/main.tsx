import React, { Component, type ErrorInfo, type ReactNode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import { FailureToasts } from './graph/FailureToasts';
import { reasonOf } from './graph/graph-failures';
import { failures } from './graph/graph-page';
import './explorer.css';

const UNCAUGHT = 'An uncaught failure in the Graph page';

class ExplorerErrorBoundary extends Component<{ children: ReactNode }, { error: string }> {
  state = { error: '' };

  static getDerivedStateFromError(error: Error) {
    return { error: error.message };
  }

  // What stopped the page goes to the chat bar too, so the person sees it there and not only on the page.
  componentDidCatch(error: Error, info: ErrorInfo) {
    failures.fail(`The Graph app stopped rendering: ${error.message}`, `Rendering the Graph page:${info.componentStack ?? ''}`);
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

// A failure no operation of the page caught still reaches the page and the chat that opened it.
window.addEventListener('error', (event) => failures.fail(`The Graph app failed: ${reasonOf(event.error ?? event.message)}`, UNCAUGHT));
window.addEventListener('unhandledrejection', (event) => failures.fail(`The Graph app failed: ${reasonOf(event.reason)}`, UNCAUGHT));

const stored = window.localStorage.getItem('kg-theme');
if (stored === 'engineering') {
  document.documentElement.dataset.theme = 'engineering';
}

createRoot(document.getElementById('root')!).render(
  <>
    <ExplorerErrorBoundary>
      <React.StrictMode>
        <App />
      </React.StrictMode>
    </ExplorerErrorBoundary>
    <FailureToasts failures={failures} />
  </>,
);
