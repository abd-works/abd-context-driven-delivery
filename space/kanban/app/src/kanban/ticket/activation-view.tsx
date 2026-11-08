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

// Python says which choices leaving offers; the dialog words them. Commit, push, and merge act on the branch the work
// being left is on, its own or main, so they name it while it is checked out.
function LeaveGroupView({ open }: { open: Activation }) {
  const { page } = useBoard()
  const branch = open.leavingBranch
  const named = branch || open.leavingTitle
  const labels: Record<string, string> = {
    handoff: 'Create handoff',
    commit: `Commit changes on ${named}`,
    push: `Push ${named} to origin`,
    merge: `Merge ${named} into main`,
  }
  return (
    <div className="dialog-group">
      <div className="dialog-group-heading">{open.isClosing ? 'CLOSE' : 'LEAVE'}</div>
      <SessionFactsView session={open.leavingTitle} branch={branch || NONE_YET} />
      {open.ticket.leaveChoices.map(choice => {
        const isOffered = open.offeredLeaving.includes(choice)
        return <OptionView key={choice} label={labels[choice] ?? choice} isChecked={isOffered && open.leaving.includes(choice)} isOff={!isOffered} onToggle={() => page.activation.toggleLeaving(choice)} />
      })}
    </div>
  )
}

function OpenGroupView({ open }: { open: Activation }) {
  const { page } = useBoard()
  const { name } = open.ticket
  const labels: Record<string, [offered: string, made: string]> = {
    branch: [`Create branch ${name}`, `Branch ${name} already exists`],
    worktree: [`Create worktree for ${name}`, 'Worktree already exists'],
  }
  return (
    <div className="dialog-group">
      <div className="dialog-group-heading">OPEN</div>
      <SessionFactsView session={open.ticket.title} branch={open.hasBranch ? name : NONE_YET} />
      {open.ticket.openChoices.map(choice => {
        const isOffered = open.offeredOpening.includes(choice)
        return (
          <OptionView
            key={choice}
            label={labels[choice]?.[isOffered ? 0 : 1] ?? choice}
            isChecked={isOffered && open.opening.includes(choice)}
            isOff={!isOffered}
            onToggle={() => page.activation.toggleOpening(choice)}
          />
        )
      })}
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
