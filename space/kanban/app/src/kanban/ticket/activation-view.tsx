import type { FormEvent, KeyboardEvent } from 'react'

import { useBoard } from '../board/board-context'
import type { Activation } from '../board/board-store'
import { activationHeading } from './activation-client'

const NONE_YET = 'none yet'

type OptionProps = { label: string; isChecked: boolean; isOff: boolean; onToggle: () => void }

function OptionView({ label, isChecked, isOff, onToggle }: OptionProps) {
  return (
    <label className={isOff ? 'dialog-option is-off' : 'dialog-option'}>
      <input type="checkbox" checked={isChecked} disabled={isOff} onChange={onToggle} />
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

// A handoff is written for the session left whatever is checked out. Commit, push, and merge act on what is checked
// out, so they act on the branch the work is on, its own or main, and on nothing when neither is checked out.
function LeaveGroupView({ open }: { open: Activation }) {
  const { page } = useBoard()
  const branch = open.leavingBranch?.is_checked_out ? open.leavingBranch.name : ''
  const options = [
    { key: 'commit', label: `Commit changes on ${branch || open.leavingTitle}` },
    { key: 'push', label: `Push ${branch || open.leavingTitle} to origin` },
    { key: 'merge', label: `Merge ${branch || open.leavingTitle} into main` },
  ]
  const hasBranch = branch !== ''
  return (
    <div className="dialog-group">
      <div className="dialog-group-heading">{open.isClosing ? 'CLOSE' : 'LEAVE'}</div>
      <SessionFactsView session={open.leavingTitle} branch={branch || NONE_YET} />
      <OptionView label="Create handoff" isChecked={open.leaving.includes('handoff')} isOff={false} onToggle={() => page.activation.toggleLeaving('handoff')} />
      {options.map(option => (
        <OptionView key={option.key} label={option.label} isChecked={hasBranch && open.leaving.includes(option.key)} isOff={!hasBranch} onToggle={() => page.activation.toggleLeaving(option.key)} />
      ))}
    </div>
  )
}

function OpenGroupView({ open }: { open: Activation }) {
  const { page } = useBoard()
  const hasBranch = open.branch.exists
  const hasWorktree = open.ticket.worktree !== ''
  return (
    <div className="dialog-group">
      <div className="dialog-group-heading">OPEN</div>
      <SessionFactsView session={open.ticket.title} branch={hasBranch ? open.ticket.name : NONE_YET} />
      <OptionView label={hasBranch ? `Branch ${open.ticket.name} already exists` : `Create branch ${open.ticket.name}`} isChecked={!hasBranch && open.opening.includes('branch')} isOff={hasBranch} onToggle={() => page.activation.toggleOpening('branch')} />
      <OptionView label={hasWorktree ? 'Worktree already exists' : `Create worktree for ${open.ticket.name}`} isChecked={!hasWorktree && open.opening.includes('worktree')} isOff={hasWorktree} onToggle={() => page.activation.toggleOpening('worktree')} />
    </div>
  )
}

function DialogActionsView({ isClosing }: { isClosing: boolean }) {
  const { page } = useBoard()
  return (
    <div className="dialog-actions">
      <button className="action" type="button" autoFocus onClick={() => page.activation.cancel()}>
        Cancel
      </button>
      <button className="action primary" type="submit">
        {isClosing ? 'Close session' : 'Activate'}
      </button>
    </div>
  )
}

export function ActivationView() {
  const { page, state } = useBoard()
  const open = state.activation
  if (!open) return null
  const submit = (event: FormEvent) => {
    event.preventDefault()
    void page.activation.confirm()
  }
  const pressed = (event: KeyboardEvent) => {
    if (event.key === 'Escape') page.activation.cancel()
  }
  return (
    <div className="dialog-backdrop" onKeyDown={pressed}>
      <form role="dialog" aria-modal="true" aria-labelledby="switch-title" className="dialog" onSubmit={submit}>
        <h2 id="switch-title">{activationHeading(open)}</h2>
        {open.leavingTitle ? <LeaveGroupView open={open} /> : null}
        {open.isClosing ? null : <OpenGroupView open={open} />}
        <DialogActionsView isClosing={open.isClosing} />
      </form>
    </div>
  )
}
