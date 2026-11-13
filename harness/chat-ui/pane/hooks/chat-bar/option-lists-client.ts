import type { EngineInterface } from 'claude-code'

import { closeActionPicker, currentActionPicker } from './action-picker-client'
import { closeRepoList, closeSessionList, currentChatBarView } from './session-dialogs-client'
import { closeStagePicker, isStagePickerOpen } from './stage-client'
import { closeOverlayList, isOverlayListOpen } from './overlay-choices-client'

// Each list box of options on the chat bar, the keys of the elements that are its own (its button and its rows), and
// how to read and close it. A press anywhere else, or typing in the prompt, closes it, as a click outside a menu does.
type OptionList = { owns: RegExp; isOpen: ($: EngineInterface) => Promise<boolean>; close: ($: EngineInterface) => Promise<void> }

const OPTION_LISTS: OptionList[] = [
  { owns: /^(session-list-button$|session-(?!name-button$)|new-session$)/, isOpen: async $ => (await currentChatBarView($)).isSessionListOpen, close: closeSessionList },
  { owns: /^(repo-|new-repo$)/, isOpen: async $ => (await currentChatBarView($)).isRepoListOpen, close: closeRepoList },
  { owns: /^stage-/, isOpen: async $ => Boolean(await isStagePickerOpen($)), close: closeStagePicker },
  { owns: /^(action-picker$|pick-)/, isOpen: async $ => (await currentActionPicker($)).isOpen, close: closeActionPicker },
  { owns: /^overlay-/, isOpen: isOverlayListOpen, close: closeOverlayList },
]

// Close every open list box but the one element belongs to; with no element, such as a keystroke in the prompt, all.
export async function closeOptionListsOutside($: EngineInterface, element = ''): Promise<void> {
  for (const list of OPTION_LISTS) {
    if (element && list.owns.test(element)) continue
    if (await list.isOpen($)) await list.close($)
  }
}
