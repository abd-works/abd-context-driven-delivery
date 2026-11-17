import { useState } from 'react'
import type { KeyboardEvent, MouseEvent } from 'react'

import { SessionActionIcon } from './icons'

// A press on a card's control does the control's work only, not the card's own press, which would open the card.
export const withoutSelecting = (press: () => unknown) => (event: MouseEvent) => {
  event.stopPropagation()
  void press()
}

// What a field on a card writes: its icon, the button that opens it, and the field itself. A text field is a box of
// several lines that wraps what is typed, so the whole text shows while it is edited.
export type CardField = { action: string; label: string; hint: string; field: string; placeholder: string; isText?: boolean }

const TEXT_FIELD_LINES = 3

type CardFieldProps = { shape: CardField; isOff: boolean; typedAtFirst?: string; onEnter: (typed: string) => unknown }

// What is typed in a field while it is open, none while it is put away: Enter writes it, Escape puts it away unwritten;
// in a box of several lines, Shift+Enter starts a new line.
export function useTypedField(onEnter: (typed: string) => unknown) {
  const [typed, setTyped] = useState<string | null>(null)
  const pressed = (event: KeyboardEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    event.stopPropagation()
    if (event.key === 'Escape') setTyped(null)
    if (event.key !== 'Enter' || event.shiftKey) return
    event.preventDefault()
    if (!typed?.trim()) return
    void onEnter(typed.trim())
    setTyped(null)
  }
  return { typed, setTyped, pressed }
}

// A field opened from an icon on a card; leaving the field puts it away.
export function CardFieldView({ shape, isOff, typedAtFirst = '', onEnter }: CardFieldProps) {
  const { typed, setTyped, pressed } = useTypedField(onEnter)
  if (typed !== null && shape.isText) {
    const rows = Math.max(typed.split('\n').length, TEXT_FIELD_LINES)
    return <textarea className="card-field item-text-editor" aria-label={shape.field} placeholder={shape.placeholder} rows={rows} value={typed} autoFocus onClick={event => event.stopPropagation()} onChange={event => setTyped(event.target.value)} onKeyDown={pressed} onBlur={() => setTyped(null)} />
  }
  if (typed !== null) {
    return <input className="child-title card-field" aria-label={shape.field} placeholder={shape.placeholder} value={typed} autoFocus onClick={event => event.stopPropagation()} onChange={event => setTyped(event.target.value)} onKeyDown={pressed} onBlur={() => setTyped(null)} />
  }
  return (
    <button className="file-view" aria-label={shape.label} title={shape.hint} disabled={isOff} onClick={withoutSelecting(() => setTyped(typedAtFirst))}>
      <SessionActionIcon action={shape.action} />
    </button>
  )
}
