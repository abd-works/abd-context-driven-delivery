import { useEffect, useRef, useState } from 'react';
import { queryProgress, type QueryProgress } from './query-progress';

const SECONDS_PER_MINUTE = 60;
const MILLISECONDS_PER_SECOND = 1000;

function elapsedLabel(seconds: number): string {
  const minutes = Math.floor(seconds / SECONDS_PER_MINUTE);
  const rest = seconds % SECONDS_PER_MINUTE;
  return `${minutes}:${rest.toString().padStart(2, '0')}`;
}

// The seconds since the view showed, counted while it shows.
function useElapsed(): number {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    const started = Date.now();
    const id = window.setInterval(() => setElapsed(Math.floor((Date.now() - started) / MILLISECONDS_PER_SECOND)), MILLISECONDS_PER_SECOND);
    return () => window.clearInterval(id);
  }, []);
  return elapsed;
}

// The meter while the server counts its steps.
function LoadMeter({ progress, headline }: { progress: QueryProgress; headline: string }) {
  if (progress.total <= 0) return null;
  const fraction = Math.min(100, Math.round((100 * progress.index) / progress.total));
  return (
    <div className="load-meter" data-testid="load-meter" role="progressbar" aria-valuenow={progress.index} aria-valuemin={0} aria-valuemax={progress.total} aria-label={headline}>
      <span style={{ width: `${fraction}%` }} />
    </div>
  );
}

// The steps done so far, kept scrolled to the newest; the server's own lines while it names no step, and the step it is
// on last.
function LoadLog({ progress, loadingLog, shown, elapsed }: { progress: QueryProgress; loadingLog: string[]; shown: string; elapsed: number }) {
  const log = useRef<HTMLOListElement>(null);
  useEffect(() => {
    if (log.current) log.current.scrollTop = log.current.scrollHeight;
  }, [progress.headline, progress.steps.length, loadingLog.length, elapsed]);
  const isOnStep = progress.steps.length === 0 || progress.steps[progress.steps.length - 1]?.name !== progress.headline.split(' ').at(-1);
  const lines = progress.steps.length === 0 ? (loadingLog.length > 0 ? loadingLog.slice(-12) : [shown]) : [];
  return (
    <ol className="loading-log" data-testid="loading-log" ref={log}>
      {progress.steps.map((step) => <li key={`${step.index}-${step.name}`}>{step.index}/{step.total} {step.name}</li>)}
      {lines.map((line, index) => <li key={`${index}-${line}`}>{line}</li>)}
      {isOnStep && progress.detail ? <li className="is-current">{progress.detail}</li> : null}
    </ol>
  );
}

// What a graph load is doing while it runs: the step now, the time it has taken, a meter while the steps are counted, and
// the steps done so far, read from the cdd server's progress reports. The Graph app and the Files app's graph view show it.
export function LoadProgressView({ loadingLabel, loadingLog }: { loadingLabel?: string; loadingLog: string[] }) {
  const progress = queryProgress(loadingLog);
  const elapsed = useElapsed();
  const headline = progress.headline === 'Loading the graph…' ? loadingLabel ?? progress.headline : progress.headline;
  const shown = elapsed > 0 ? `${headline} · ${elapsedLabel(elapsed)}` : headline;
  return (
    <div className="empty-state work-progress is-working" data-testid="extraction-progress">
      <p className="query-now">{shown}</p>
      <LoadMeter progress={progress} headline={headline} />
      <LoadLog progress={progress} loadingLog={loadingLog} shown={shown} elapsed={elapsed} />
    </div>
  );
}
