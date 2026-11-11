import type { FormEvent, KeyboardEvent } from 'react'

import { useBoard } from '../shared/board-context'
import type { Closing } from '../shared/board-store'
import { closingHeading } from './activation-client'

const NONE_YET = 'none yet'

type OptionProps = { label: string; isChecked: boolean; onToggle: () => void }

function OptionView({ label, isChecked, onToggle }: OptionProps) {
  return (
    <label className="dialog-option">
      <input type="checkbox" checked={isChecked} onChange={onToggle} />
      <span>{label}</span>
    </label>
  )
}

function SessionFactsView({ session, branch }: { session: string; branch: string }) {
  return (
    <div className="dialog-facts">
      <span className="fact-name">session</span>
      <span className="fact-value">{session}</span>
      <span className="fact-name">branch</span>
      <span className="fact-value">{branch}</span>
    </div>
  )
}

// Python says which choices closing offers; the dialog words them. Commit, push, and merge act on the branch the
// ticket's work is on, its own or main, so they name it while it is checked out.
function CloseGroupView({ closing }: { closing: Closing }) {
  const { page } = useBoard()
  const branch = closing.leavingBranch
  const named = branch || closing.ticket.title
  const labels: Record<string, string> = {
    handoff: 'Create handoff',
    commit: `Commit changes on ${named}`,
    push: `Push ${named} to origin`,
    merge: `Merge ${named} into main`,
    delete_branch: `Delete branch ${named} once merged`,
    delete_worktree: `Delete the worktree of ${named}`,
  }
  return (
    <div className="dialog-group">
      <div className="dialog-group-heading">CLOSE</div>
      <SessionFactsView session={closing.ticket.title} branch={branch || NONE_YET} />
      {closing.offeredLeaving.map(choice => (
        <OptionView key={choice} label={labels[choice] ?? choice} isChecked={closing.leaving.includes(choice)} onToggle={() => page.activation.toggleLeaving(choice)} />
      ))}
    </div>
  )
}

function DialogActionsView() {
  const { page } = useBoard()
  return (
    <div className="dialog-actions">
      <button className="action" type="button" autoFocus onClick={() => page.activation.cancel()}>
        Cancel
      </button>
      <button className="action primary" type="submit">
        Close session
      </button>
    </div>
  )
}

// The Close dialog, which asks before closing a ticket's session because closing can commit, push, and merge its work.
export function ActivationView() {
  const { page, state } = useBoard()
  const closing = state.closing
  if (!closing) return null
  const submit = (event: FormEvent) => {
    event.preventDefault()
    void page.activation.confirm()
  }
  const pressed = (event: KeyboardEvent) => {
    if (event.key === 'Escape') page.activation.cancel()
  }
  return (
    <div className="dialog-backdrop" onKeyDown={pressed}>
      <form role="dialog" aria-modal="true" aria-labelledby="close-title" className="dialog" onSubmit={submit}>
        <h2 id="close-title">{closingHeading(closing)}</h2>
        <CloseGroupView closing={closing} />
        <DialogActionsView />
      </form>
    </div>
  )
}
