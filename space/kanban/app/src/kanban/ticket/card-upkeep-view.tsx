import { useBoard } from '../shared/board-context'
import { SessionActionIcon } from '../shared/icons'
import { CardFieldView, withoutSelecting } from '../shared/card-field-view'
import type { CardField } from '../shared/card-field-view'
import type { TicketClient } from './ticket-client'

const ADD_CHILD: CardField = { action: 'child', label: 'Add child', hint: 'Add a child ticket', field: 'Child title', placeholder: 'Child title, then Enter' }
const EDIT_TEXT: CardField = { action: 'text', label: 'Edit text', hint: 'Edit what this ticket is about', field: 'Ticket text', placeholder: 'Text, then Enter' }
const TAG: CardField = { action: 'tag', label: 'Tag', hint: "Tag this ticket's session", field: 'Tag', placeholder: 'Tag, then Enter' }

// A child added by hand: the plus opens a title field on the card, Enter adds the child, Escape leaves it.
export function AddChildView({ ticket }: { ticket: TicketClient }) {
  return <CardFieldView shape={ADD_CHILD} isOff={ticket.isClosed || ticket.isMain} onEnter={title => ticket.addChild(title)} />
}

// What the ticket's work is about, written in the idea file its session folder keeps; the field starts from its text.
export function EditTextView({ ticket }: { ticket: TicketClient }) {
  return <CardFieldView shape={EDIT_TEXT} isOff={ticket.isMain} typedAtFirst={ticket.text} onEnter={text => ticket.editText(text)} />
}

function TagView({ ticket }: { ticket: TicketClient }) {
  return <CardFieldView shape={TAG} isOff={ticket.isMain} onEnter={word => ticket.tag(word)} />
}

// Delete removes the ticket and its whole session folder, which cannot be undone, so the person confirms it first.
function DeleteView({ ticket }: { ticket: TicketClient }) {
  const deleted = () => window.confirm(`Delete ${ticket.title} and its session folder? This cannot be undone.`) && ticket.delete()
  return (
    <button className="file-view" aria-label="Delete" title="Delete this ticket and its session folder" disabled={ticket.isMain} onClick={withoutSelecting(deleted)}>
      <SessionActionIcon action="delete" />
    </button>
  )
}

// What an open card offers for keeping its ticket up to date: its text, its tags, and deleting it.
export function CardUpkeepView({ ticket }: { ticket: TicketClient }) {
  return (
    <div className="card-upkeep">
      <EditTextView ticket={ticket} />
      <TagView ticket={ticket} />
      <DeleteView ticket={ticket} />
    </div>
  )
}

const SHOWN_PARAGRAPHS = 2

// A card shows only the opening of what its ticket is about: its first paragraphs, then a link to the whole file.
export const openingOf = (text: string): { opening: string; isCut: boolean } => {
  const paragraphs = text.split(/\n\s*\n/).filter(paragraph => paragraph.trim())
  return { opening: paragraphs.slice(0, SHOWN_PARAGRAPHS).join('\n\n'), isCut: paragraphs.length > SHOWN_PARAGRAPHS }
}

// What a ticket is about, on its open card only: the opening paragraphs of its idea file and a link that opens the file.
function TicketTextView({ ticket }: { ticket: TicketClient }) {
  const { page } = useBoard()
  const file = `${ticket.name}.md`
  const path = ticket.session.session_file.replace(/session\.json$/, file)
  const { opening, isCut } = openingOf(ticket.text)
  return (
    <>
      <div className="ticket-text">{opening}</div>
      <button className="ticket-text-link" title={`Open ${file}`} onClick={withoutSelecting(() => page.files.openSessionFile(ticket, path))}>
        {isCut ? `More in ${file}` : file}
      </button>
    </>
  )
}

// What a ticket is about and the words it is tagged with, under its title on its card; the text only once it is open.
export function CardNotesView({ ticket, showsText }: { ticket: TicketClient; showsText: boolean }) {
  return (
    <>
      {showsText && ticket.text ? <TicketTextView ticket={ticket} /> : null}
      {ticket.tags.length ? (
        <div className="ticket-tags" aria-label="Tags">
          {ticket.tags.map(tag => (
            <span key={tag} className="ticket-tag">
              {tag}
            </span>
          ))}
        </div>
      ) : null}
    </>
  )
}
