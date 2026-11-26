import { useEffect, useRef, useState } from 'react';
import type { Held } from './held';
import { LOADING_GRAPH } from '../graph/query-progress';
import type { CddProgress } from '@cdd/cdd-shared';
import { reasonOf } from '@cdd/cdd-page-failures';
import { failures, graphs } from '../graph/graph-page';

// How often the page reads the cdd server's progress while it shows.
const PROGRESS_READ_MS = 400;

interface LoadStatusState {
  loading: Held<boolean>;
  label: Held<string>;
  log: Held<string[]>;
  error: Held<string>;
  // Whether a load runs now, read by the progress loop, which outlives the render that started it.
  loadingNow: { current: boolean };
}

// What the graph pane says about the load in progress: whether one runs, its label, the steps the server reported,
// and the error the last operation failed with.
export class LoadStatus {
  constructor(private readonly state: LoadStatusState) {}

  get loading(): boolean {
    return this.state.loading[0];
  }

  get label(): string {
    return this.state.label[0];
  }

  get log(): string[] {
    return this.state.log[0];
  }

  get error(): string {
    return this.state.error[0];
  }

  // Whether a load runs now, read by code that outlives the render that made this status.
  get loadingNow(): boolean {
    return this.state.loadingNow.current;
  }

  // A load or an overlay change starts: the pane shows label, and the last error goes.
  begin(label: string = LOADING_GRAPH): void {
    this.state.loading[1](true);
    this.state.label[1](label);
    this.state.error[1]('');
  }

  end(): void {
    this.state.loading[1](false);
  }

  clearLog(): void {
    this.state.log[1]([]);
  }

  // The newest line of the server's progress, added to the log once, and shown as the label while the graph loads.
  logLine(line: string, labels: boolean): void {
    this.state.log[1]((current) => (current[current.length - 1] === line ? current : [...current, line]));
    if (labels && this.state.loadingNow.current) this.state.label[1](line);
  }

  // A failure of an operation the graph pane shows: kept in the pane, and shown and sent to the opening chat.
  failed(cause: unknown, context: string): void {
    this.state.error[1](reasonOf(cause));
    failures.fail(reasonOf(cause), context);
  }
}

export function useLoadStatus(): LoadStatus {
  const loadingNow = useRef(false);
  const loading = useState(false);
  loadingNow.current = loading[0];
  return new LoadStatus({ loading, label: useState(LOADING_GRAPH), log: useState<string[]>([]), error: useState(''), loadingNow });
}

// Read the cdd server's progress every PROGRESS_READ_MS while the page shows, into status's log.
export function useServerProgress(status: LoadStatus): void {
  useEffect(() => {
    let stop = false;
    void (async () => {
      while (!stop) {
        await readProgress(status);
        await new Promise((resolve) => setTimeout(resolve, PROGRESS_READ_MS));
      }
    })();
    return () => {
      stop = true;
    };
  }, []);
}

async function readProgress(status: LoadStatus): Promise<void> {
  try {
    const steps = (await graphs.api.post<CddProgress[]>('/cdd/progress', {})) ?? [];
    const newest = steps[steps.length - 1]?.message;
    if (newest) status.logLine(newest, true);
  } catch (cause) {
    status.logLine(`error: Progress check failed: ${reasonOf(cause)}`, false);
    failures.fail(`The Graph app did not read the cdd server's progress: ${reasonOf(cause)}`, 'Reading the progress of the cdd server while the page shows');
  }
}
