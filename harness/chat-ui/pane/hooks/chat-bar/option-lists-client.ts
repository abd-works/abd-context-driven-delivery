import type { EngineInterface } from 'claude-code'

import { closeActionPicker, currentActionPicker } from './action-picker-client'
import { closeCard, closeRepoList, closeSessionList, currentChatBarView } from './session-dialogs-client'
import { closeStagePicker, isStagePickerOpen } from './stage-client'
import { closeOverlayList, isOverlayListOpen } from './overlay-choices-client'

// The keys of the elements each list box of options on the chat bar, and the pinned session card, owns: its button and its rows. A press anywhere
// else, or typing in the prompt, closes it, as a click outside a menu does.
const SESSION_LIST_KEYS = /^(session-list-button$|session-(?!name-button$)|new-session$)/
const REPO_LIST_KEYS = /^(repo-|new-repo$)/
const STAGE_LIST_KEYS = /^stage-/
const ACTION_LIST_KEYS = /^(action-picker$|pick-)/
const OVERLAY_LIST_KEYS = /^overlay-/
// The pinned session card: its rows, folder chips and ✕, and the server health mark and panel stacked on it.
const CARD_KEYS = /^(card-|health-)/

// Whether the press on element leaves the list whose keys are owned open; no element, such as a keystroke, owns none.
function isOwnedBy(owned: RegExp, element: string): boolean {
  return Boolean(element) && owned.test(element)
}

// Close every open list box but the one element belongs to; with no element, such as a keystroke in the prompt, all.
// Each list is read and closed by a direct call: the engine refuses $ handed to a function kept in a table.
export async function closeOptionListsOutside($: EngineInterface, element = ''): Promise<void> {
  const view = await currentChatBarView($)
  if (!isOwnedBy(SESSION_LIST_KEYS, element) && view.isSessionListOpen) await closeSessionList($)
  if (!isOwnedBy(REPO_LIST_KEYS, element) && view.isRepoListOpen) await closeRepoList($)
  if (!isOwnedBy(STAGE_LIST_KEYS, element) && (await isStagePickerOpen($))) await closeStagePicker($)
  if (!isOwnedBy(ACTION_LIST_KEYS, element) && (await currentActionPicker($)).isOpen) await closeActionPicker($)
  if (!isOwnedBy(OVERLAY_LIST_KEYS, element) && (await isOverlayListOpen($))) await closeOverlayList($)
  if (!isOwnedBy(CARD_KEYS, element) && view.isCardOpen) await closeCard($)
}
