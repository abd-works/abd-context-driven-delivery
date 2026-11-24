import { useState } from 'react';
import type { FixOutcome } from './violation-prompt';

// A Fix button: while its fix is sent it says so, then beside it shows what came of it, sent to the chat or not sent, the
// page's toast saying why.
export function FixButton({ label, title, testId, fix }: { label: string; title: string; testId: string; fix: () => Promise<FixOutcome> }) {
  const [isSending, setSending] = useState(false);
  const [outcome, setOutcome] = useState<FixOutcome | null>(null);
  async function send() {
    setSending(true);
    setOutcome(null);
    setOutcome(await fix());
    setSending(false);
  }
  return (
    <span className="violation-correct">
      {outcome ? (
        <span className={`violation-correct-outcome ${outcome.isSent ? 'is-sent' : 'is-failed'}`} data-testid={`${testId}-outcome`} role="status">
          {outcome.words}
        </span>
      ) : null}
      <button type="button" className="copy-prompt" data-testid={testId} disabled={isSending} title={title} onClick={() => void send()}>
        {isSending ? 'Sending…' : label}
      </button>
    </span>
  );
}
