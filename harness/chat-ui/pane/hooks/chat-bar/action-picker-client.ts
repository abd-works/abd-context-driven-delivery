import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { ActionPickerJson } from '../../types'

// Whether the action button's ▾ menu is open, and the action picked from it. The button runs it through
// fidelity-client.ts.
const actionPicker = atom({ plugin: 'cdd-board', key: 'actionPicker' } as const, { isOpen: false, chosenAction: null } as ActionPickerJson)

// Atom actionPicker, declared in pane/types/index.d.ts and kept in this file.
export async function currentActionPicker($: EngineInterface): Promise<ActionPickerJson> {
  const picker = await read($, actionPicker)
  return { isOpen: picker.isOpen, chosenAction: picker.chosenAction ?? null }
}

export async function toggleActionPicker($: EngineInterface): Promise<void> {
  await update($, actionPicker, picker => ({ ...picker, isOpen: !picker.isOpen }))
}

// Picking from the menu closes it and puts the action on the button; it runs when the button is pressed.
export async function chooseAction($: EngineInterface, action: string): Promise<void> {
  await update($, actionPicker, () => ({ isOpen: false, chosenAction: action }))
}

// Once the button has run the chosen action, it shows the fidelity's next action again.
export async function clearChosenAction($: EngineInterface): Promise<void> {
  await update($, actionPicker, picker => ({ ...picker, chosenAction: null }))
}
