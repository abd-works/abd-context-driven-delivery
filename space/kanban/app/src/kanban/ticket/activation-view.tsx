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

// Commit, push, and merge act on what is checked out, so with no branch of its own there is nothing to act on.
function LeaveGroupView({ open }: { open: Activation }) {
  const { page } = useBoard()
  const hasBranch = open.workspace.leavingHasBranch
  const options = [
    { key: 'commit', label: `Commit changes on ${open.leavingTitle}` },
    { key: 'push', label: `Push ${open.leavingTitle} to origin` },
    { key: 'merge', label: `Merge ${open.leavingTitle} into main` },
  ]
  return (
    <div className="dialog-group">
      <div className="dialog-group-heading">{open.isClosing ? 'CLOSE' : 'LEAVE'}</div>
      <SessionFactsView session={open.leavingTitle} branch={hasBranch ? open.leavingTitle : NONE_YET} />
      {options.map(option => (
        <OptionView key={option.key} label={option.label} isChecked={hasBranch && open.leaving.includes(option.key)} isOff={!hasBranch} onToggle={() => page.activation.toggleLeaving(option.key)} />
      ))}
    </div>
  )
}

function OpenGroupView({ open }: { open: Activation }) {
  const { page } = useBoard()
  const { hasBranch, hasWorktree } = open.workspace
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
