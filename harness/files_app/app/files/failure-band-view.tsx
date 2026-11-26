import { useSyncExternalStore } from 'react'

import type { ShownFailure } from './failure-fixes'
import type { FilesPage } from './files-page'
import './failure-band.css'

// The band of failures under the page's head: each failure the page met, with Fix and ✕. Fix lists the most common
// causes of that kind of failure, which Python answers (failure.describe), and sends the failure with those causes to
// the chat that opened the page to fix; ✕ takes the failure off the band.
export function FailureBandView({ page }: { page: FilesPage }) {
  const { failures } = useSyncExternalStore(page.store.subscribe, () => page.store.state)
  if (!failures.length) return null
  return (
    <ul className="failure-band" aria-label="Failures">
      {failures.map(shown => (
        <FailureFixView key={shown.failure} page={page} shown={shown} />
      ))}
    </ul>
  )
}

const FIX_LABELS: Record<ShownFailure['fix'], string> = { not_asked: 'Fix', asking: 'Sending…', sent: 'Sent to fix', not_sent: 'Fix again' }

// One failure with its Fix: what failed, unless the page's problem line already says it, the context it failed in, and,
// once Fix is pressed, the causes to check first and whether the fix reached the chat.
function FailureFixView({ page, shown }: { page: FilesPage; shown: ShownFailure }) {
  const fixes = page.notices.fixes
  return (
    <li className={`failure-fix is-${shown.fix}`}>
      <div className="failure-fix-line">
        <span className="failure-fix-said">
          {shown.isOnProblemLine ? null : <span className="failure-fix-failure">{shown.failure}</span>}
          <span className="failure-fix-context">{shown.context}</span>
        </span>
        <button type="button" className="failure-fix-button" disabled={shown.fix === 'asking' || shown.fix === 'sent'} title="Lists the most common causes of this failure and sends them with it to the chat to fix" onClick={() => void fixes.fix(shown.failure)}>
          {FIX_LABELS[shown.fix]}
        </button>
        <button type="button" className="failure-fix-dismiss" aria-label="Dismiss this failure" title="Take this failure off the page" onClick={() => fixes.dismiss(shown.failure)}>
          ✕
        </button>
      </div>
      {shown.described ? <FailureCausesView shown={shown} /> : null}
      {shown.note ? <p className="failure-fix-note" role="status">{shown.note}</p> : null}
    </li>
  )
}

// What Python answered for the failure: the most common causes of its kind, the likeliest first, and the command sent
// to the chat, which a page no chat opened shows for the person to copy.
function FailureCausesView({ shown }: { shown: ShownFailure }) {
  const described = shown.described!
  return (
    <div className="failure-fix-causes">
      {described.causes.length ? <p className="failure-fix-heading">Most common causes, checked first:</p> : <p className="failure-fix-heading">No common causes are known for this failure: the chat looks for its cause from the failure and its context.</p>}
      <ol>
        {described.causes.map(cause => (
          <li key={cause}>{cause}</li>
        ))}
      </ol>
      <details className="failure-fix-command">
        <summary>{shown.fix === 'sent' ? 'What was sent to the chat' : 'What goes to the chat'}</summary>
        <pre>{described.fix_command}</pre>
      </details>
    </div>
  )
}
