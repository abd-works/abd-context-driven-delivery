import { useEffect, useRef, useState } from 'react';
import { queryProgress } from './query-progress';

function elapsedLabel(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  return `${minutes}:${rest.toString().padStart(2, '0')}`;
}

// What a graph load is doing while it runs: the step now, the time it has taken, a meter while the steps are counted, and
// the steps done so far, read from the cdd server's progress reports. The Graph app and the Files app's graph view show it.
export function LoadProgressView({ loadingLabel, loadingLog }: { loadingLabel?: string; loadingLog: string[] }) {
  const progress = queryProgress(loadingLog);
  const log = useRef<HTMLOListElement>(null);
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    const started = Date.now();
    const id = window.setInterval(() => setElapsed(Math.floor((Date.now() - started) / 1000)), 1000);
    return () => window.clearInterval(id);
  }, []);
  useEffect(() => {
    const list = log.current;
    if (list) {
      list.scrollTop = list.scrollHeight;
    }
  }, [progress.headline, progress.steps.length, loadingLog.length, elapsed]);
  const active =
    progress.steps.length === 0 || progress.steps[progress.steps.length - 1]?.name !== progress.headline.split(' ').at(-1);
  const headline = progress.headline === 'Loading the graph…' ? loadingLabel ?? progress.headline : progress.headline;
  const shown = elapsed > 0 ? `${headline} · ${elapsedLabel(elapsed)}` : headline;
  const fraction = progress.total > 0 ? Math.min(100, Math.round((100 * progress.index) / progress.total)) : 0;
  return (
    <div className="empty-state work-progress is-working" data-testid="extraction-progress">
      <p className="query-now">{shown}</p>
      {progress.total > 0 ? (
        <div
          className="load-meter"
          data-testid="load-meter"
          role="progressbar"
          aria-valuenow={progress.index}
          aria-valuemin={0}
          aria-valuemax={progress.total}
          aria-label={headline}
        >
          <span style={{ width: `${fraction}%` }} />
        </div>
      ) : null}
      <ol className="loading-log" data-testid="loading-log" ref={log}>
        {progress.steps.map((step) => (
          <li key={`${step.index}-${step.name}`}>
            {step.index}/{step.total} {step.name}
          </li>
        ))}
        {progress.steps.length === 0
          ? (loadingLog.length > 0 ? loadingLog.slice(-12) : [shown]).map((line, index) => <li key={`${index}-${line}`}>{line}</li>)
          : null}
        {active && progress.detail ? <li className="is-current">{progress.detail}</li> : null}
      </ol>
    </div>
  );
}
