import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { ActionPickerJson } from '../../types'

// Whether the action button's ▾ menu is open. The actions it offers run through fidelity-client.ts.
const actionPicker = atom({ plugin: 'cdd-board', key: 'actionPicker' } as const, { isOpen: false } as ActionPickerJson)

// Atom actionPicker, declared in pane/types/index.d.ts and kept in this file.
export function currentActionPicker($: EngineInterface) {
  return read($, actionPicker)
}

export async function toggleActionPicker($: EngineInterface): Promise<void> {
  await update($, actionPicker, picker => ({ ...picker, isOpen: !picker.isOpen }))
}

export async function closeActionPicker($: EngineInterface): Promise<void> {
  await update($, actionPicker, () => ({ isOpen: false }))
}
