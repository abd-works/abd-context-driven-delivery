import type { KeyboardEvent } from 'react'

import { useBoard } from '../shared/board-context'
import type { RootChoice } from '../shared/board-store'
import { TICKET_ROOT } from './root-choice-client'
import type { TicketClient } from './ticket-client'

const WHOLE_REPOSITORY = 'whole repository'

const shownPath = (path: string): string => path || WHOLE_REPOSITORY

function RootLineView({ label, root, standing, onChange, onDefault }: { label: string; root: string; standing: string; onChange: () => void; onDefault?: () => void }) {
  return (
    <div className="root-line">
      <span className="root-label">{label}</span>
      <span className="root-path" title={shownPath(root)}>
        {shownPath(root)}
        {standing ? <span className="root-standing"> · {standing}</span> : null}
      </span>
      <span className="root-buttons">
        {onDefault ? (
          <button className="action small" type="button" onClick={onDefault}>
            Use default
          </button>
        ) : null}
        <button className="action small" type="button" aria-label={`Change the root of ${label}`} onClick={onChange}>
          Change
        </button>
      </span>
    </div>
  )
}

// The ticket's workpath on top; every practice under it writes under its default folder there unless a person chose another practice root.
function RootsListView({ ticket }: { ticket: TicketClient }) {
  const { page } = useBoard()
  const practices = page.board.shownPractices.filter(practice => ticket.session.practices[practice.key])
  return (
    <>
      <RootLineView label="Session" root={ticket.session.workpath} standing="" onChange={() => void page.roots.browse(TICKET_ROOT, ticket.session.workpath)} />
      <div className="dialog-group-heading">PRACTICES</div>
      {practices.map(practice => {
        const { root, is_root_chosen: isChosen } = ticket.session.practices[practice.key]!
        return (
          <RootLineView
            key={practice.key}
            label={practice.name}
            root={root}
            standing={isChosen ? 'chosen' : 'default'}
            onChange={() => void page.roots.browse(practice.key, root)}
            onDefault={isChosen ? () => void page.roots.useDefault(practice.key) : undefined}
          />
        )
      })}
      <div className="dialog-actions">
        <button className="action primary" type="button" autoFocus onClick={() => page.roots.close()}>
          Done
        </button>
      </div>
    </>
  )
}

function FolderBrowserView({ browsing }: { browsing: NonNullable<RootChoice['browsing']> }) {
  const { page } = useBoard()
  const name = (folder: string) => folder.split('/').at(-1)
  return (
    <>
      <div className="folder-place">
        <button className="action small" type="button" disabled={!browsing.path} onClick={() => void page.roots.up()}>
          Up
        </button>
        <span className="root-path">{shownPath(browsing.path)}</span>
      </div>
      <div className="folder-list" role="list" aria-label="Folders">
        {browsing.folders.length ? (
          browsing.folders.map(folder => (
            <button key={folder} className="folder-entry-button" role="listitem" type="button" onClick={() => void page.roots.browse(browsing.target, folder)}>
              {name(folder)}/
            </button>
          ))
        ) : (
          <span className="root-standing">No folders inside.</span>
        )}
      </div>
      <div className="dialog-actions">
        <button className="action" type="button" onClick={() => page.roots.stopBrowsing()}>
          Cancel
        </button>
        <button className="action primary" type="button" autoFocus onClick={() => void page.roots.use()}>
          Use {shownPath(browsing.path)}
        </button>
      </div>
    </>
  )
}

function headingOf(choice: RootChoice, ticket: TicketClient | undefined, practiceName: (key: string) => string): string {
  const subject = choice.startingItem ? choice.startingItem.title : (ticket?.title ?? '')
  if (!choice.browsing) return `Roots of ${subject}`
  if (choice.startingItem) return `Where ${subject} works`
  return choice.browsing.target === TICKET_ROOT ? `Session root of ${subject}` : `${practiceName(choice.browsing.target)} root of ${subject}`
}

export function RootChoiceView() {
  const { page, state } = useBoard()
  const choice = state.rootChoice
  if (!choice) return null
  const ticket = page.roots.ticket
  const pressed = (event: KeyboardEvent) => {
    if (event.key === 'Escape') page.roots.close()
  }
  return (
    <div className="dialog-backdrop" onKeyDown={pressed}>
      <div role="dialog" aria-modal="true" aria-labelledby="roots-title" className="dialog roots-dialog">
        <h2 id="roots-title">{headingOf(choice, ticket, key => page.board.practiceNamed(key)?.name ?? key)}</h2>
        {choice.browsing ? <FolderBrowserView browsing={choice.browsing} /> : ticket ? <RootsListView ticket={ticket} /> : null}
      </div>
    </div>
  )
}
