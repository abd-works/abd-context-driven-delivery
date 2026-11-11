import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { OverlayChoiceJson, OverlayChoicesJson } from '../../types'
import { reasonOf } from '../shared/failure'
import { callTool, type ChatBarClient } from './chat-bar-client'

// The pattern overlays beside the fidelity dots: Python's ticket.overlay_choices answers every pattern with its icon and
// whether the session chose it, and ticket.choose_overlays keeps a new choice in the session and applies it to its
// graph. The bar keeps only those answers and whether its + list box is open. Atom overlayChoices, declared in
// pane/types/index.d.ts.
const overlayChoices = atom({ plugin: 'cdd-board', key: 'overlayChoices' } as const, { ticket: '', choices: [], isOpen: false } as OverlayChoicesJson)

export type OverlayChips = { ticket: string; choices: OverlayChoiceJson[]; chosen: OverlayChoiceJson[]; isOpen: boolean }

// The overlays as last read for the session the bar shows; drawing only reads.
export async function currentOverlayChips($: EngineInterface, chatBar: ChatBarClient): Promise<OverlayChips> {
  const held = (await read($, overlayChoices)) ?? { ticket: '', choices: [], isOpen: false }
  const choices = held.ticket === chatBar.ticketName ? held.choices : []
  return { ticket: chatBar.ticketName, choices, chosen: choices.filter(choice => choice.is_chosen), isOpen: held.isOpen && choices.length > 0 }
}

// Read the overlay choices again when the bar shows another session; called from events, never a draw.
export async function loadOverlayChoices($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  const held = await read($, overlayChoices)
  if (!chatBar.ticketName || held?.ticket === chatBar.ticketName) return
  const choices = await callTool<OverlayChoiceJson[]>($, 'ticket.overlay_choices', { ticket: chatBar.ticketName })
  await update($, overlayChoices, () => ({ ticket: chatBar.ticketName, choices, isOpen: false }))
}

// A press on the + opens or closes the list box of patterns.
export async function toggleOverlayList($: EngineInterface): Promise<void> {
  await update($, overlayChoices, held => ({ ...(held ?? { ticket: '', choices: [] }), isOpen: !held?.isOpen }))
}

// A press on a pattern in the list box adds it to the session's overlays or takes it out; the list stays open so a
// person can pick several. A refusal shows as a toast and leaves the choices as they were.
export async function toggleOverlay($: EngineInterface, chips: OverlayChips, pattern: string): Promise<void> {
  const chosen = chips.chosen.map(choice => choice.pattern)
  const overlays = chosen.includes(pattern) ? chosen.filter(each => each !== pattern) : [...chosen, pattern]
  try {
    const choices = await callTool<OverlayChoiceJson[]>($, 'ticket.choose_overlays', { ticket: chips.ticket, overlays })
    await update($, overlayChoices, held => ({ ...(held ?? { isOpen: true }), ticket: chips.ticket, choices }))
  } catch (failure) {
    $.ui.toast(`Overlay ${pattern}: ${reasonOf(failure)}`)
  }
}
