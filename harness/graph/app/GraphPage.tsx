import React, { Component, useEffect, type ErrorInfo, type ReactNode } from 'react';
import { App } from './App';
import { FailureToasts } from './graph/FailureToasts';
import { reasonOf } from './graph/graph-failures';
import { failures } from './graph/graph-page';

const UNCAUGHT = 'An uncaught failure in the Graph page';

class ExplorerErrorBoundary extends Component<{ children: ReactNode }, { error: string }> {
  state = { error: '' };

  static getDerivedStateFromError(error: Error) {
    return { error: error.message };
  }

  // What stopped the page goes to the chat bar too, so the person sees it there and not only on the page.
  componentDidCatch(error: Error, rendering: ErrorInfo) {
    failures.fail(`The Graph app stopped rendering: ${error.message}`, `Rendering the Graph page:${rendering.componentStack ?? ''}`);
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

// The Graph page: the explorer, the failures it met, and a failure nothing caught sent to the chat that opened it. It
// lives in a component module, not in main.tsx, so a change to the failures or the api is swapped in here while the
// page runs; main.tsx run a second time would make a second React root on the same element, and the two remove each
// other's nodes.
export function GraphPage() {
  useEffect(() => {
    const onError = (event: ErrorEvent) => failures.fail(`The Graph app failed: ${reasonOf(event.error ?? event.message)}`, UNCAUGHT);
    const onRejection = (event: PromiseRejectionEvent) => failures.fail(`The Graph app failed: ${reasonOf(event.reason)}`, UNCAUGHT);
    window.addEventListener('error', onError);
    window.addEventListener('unhandledrejection', onRejection);
    return () => {
      window.removeEventListener('error', onError);
      window.removeEventListener('unhandledrejection', onRejection);
    };
  }, []);
  return (
    <>
      <ExplorerErrorBoundary>
        <React.StrictMode>
          <App />
        </React.StrictMode>
      </ExplorerErrorBoundary>
      <FailureToasts failures={failures} />
    </>
  );
}
