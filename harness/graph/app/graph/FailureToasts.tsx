import { useEffect, useState } from 'react';
import type { GraphFailures } from './graph-failures';

// The failures the page met, each shown for a few seconds over the page.
export function FailureToasts({ failures }: { failures: GraphFailures }) {
  const [toasts, setToasts] = useState(failures.shown);
  useEffect(() => failures.onChange(setToasts), [failures]);
  if (!toasts.length) return null;
  return (
    <ul className="failure-toasts" data-testid="failure-toasts" role="alert">
      {toasts.map((toast) => (
        <li key={toast}>{toast}</li>
      ))}
    </ul>
  );
}
