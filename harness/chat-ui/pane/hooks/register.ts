import type { EngineInterface, Register } from 'claude-code'

import { checkIn } from './board-chat/board-chat-client'
import { isCheckInDue, turnCompleted, turnStarted } from './board-chat/chat-turns'
import { readName } from './board-chat/chat-name'
import { openedBoard } from './board-chat/board-server'
import { currentChatBar, refreshChatBar } from './chat-bar/chat-bar-client'
import { ChatBarView } from './chat-bar/chat-bar-view'
import { clearBusy, currentBusy } from './chat-bar/busy-client'
import { currentActionPicker } from './chat-bar/action-picker-client'
import { isStagePickerOpen } from './chat-bar/stage-client'
import { currentFormatChips, forgetFormatChips, loadFormatChips } from './chat-bar/format-choices-client'
import { currentOverlayChips, loadOverlayChoices } from './chat-bar/overlay-choices-client'
import { currentFidelityHelp, forgetHelp, HELP_PANE } from './chat-bar/fidelity-help-client'
import { FidelityHelpView } from './chat-bar/fidelity-help-view'
import { currentChatBarView } from './chat-bar/session-dialogs-client'
import { closeOptionListsOutside } from './chat-bar/option-lists-client'
import { currentFailure, shownAsFailure } from './error-display/failure-client'
import {
  currentHealthView,
  currentInstall,
  currentServerHealth,
  hideDetails,
  openDetails,
  reconnect,
  refreshHealth,
  refreshHealthSoon,
  runInstall,
} from './health/server-health-client'
import { ServerHealthBandView, ServerHealthPanelView } from './health/server-health-view'
import { currentAppOpening, openAppBesideChat } from './health/app-client'
import { FOLDER_QUERY, PROJECT_QUERY, projectPageUrl } from './board-chat/board'
import { CARD_SCOPE } from './chat-bar/session-card-view'
import { toggleCard } from './chat-bar/session-dialogs-client'
import { withChatNamed } from './session/session-log-client'

const PLUGIN = 'cdd-board'
// The presses that change which fidelities or stage the action button acts on: a fidelity's dot or card row, a stage.
const CHANGES_FIDELITIES = /^(dot-|card-pick-|stage-pick-)/
const CHECK_IN_MILLISECONDS = 1000
const CDD_TOOL = /^mcp__(plugin_cdd_)?cdd__/

// The agent context the system prompt last held, so the cached prompt is composed again only when it changes.
let shownContext = ''

// The status line below the chat, where the host draws a plugin's status: the whole path of the folder the session
// works in. The host draws it at the right.
async function showStatus($: EngineInterface): Promise<void> {
  $.ui.status((await currentChatBar($)).statusLine || undefined)
}

// The system prompt and the chat bar read the same ChatBarClient. The cdd server can still be
// connecting at session start; the chat bar then shows why, and the next event reads again.
async function readActive($: EngineInterface): Promise<void> {
  await refreshChatBar($)
  await showStatus($)
  const chatBar = await currentChatBar($)
  if (chatBar.problem) return
  await loadFormatChips($, chatBar)
  await loadOverlayChoices($, chatBar).catch(shownAsFailure($, 'The overlay choices did not load', 'Reading the board, calling ticket.overlay_choices'))
  // The system prompt is cached; when the active session's summary changes, it is composed again next turn.
  if (chatBar.agentContext !== shownContext) await $.ui.invalidate('prompt.section')
  shownContext = chatBar.agentContext
}

// The hooks below hand the event on first and then call one of these without waiting, so a failure shows on the failure line.
async function readBoardAfterStart($: EngineInterface): Promise<void> {
  await readName($).catch(shownAsFailure($, 'The chat was not named', 'Starting the chat, reading its name'))
  await readActive($).catch(shownAsFailure($, 'The board did not load', 'Starting the chat, calling board.show'))
  refreshHealthSoon($)
}

async function readBoardAfterTurn($: EngineInterface, isMainChat: boolean): Promise<void> {
  if (isMainChat) await turnCompleted($).catch(shownAsFailure($, 'The turn was not recorded as finished', 'Finishing a turn in the main chat'))
  await readName($).catch(shownAsFailure($, 'The chat was not named', 'Finishing a turn, reading the chat name'))
  await Promise.all([readActive($), refreshHealth($)]).catch(shownAsFailure($, 'The board did not load', 'Finishing a turn, calling board.show and reading the server health'))
}

async function readBoardAfterSubmit($: EngineInterface): Promise<void> {
  await Promise.all([refreshHealth($), refreshChatBar($)]).catch(shownAsFailure($, 'The board did not load', 'Sending a prompt, calling board.show and reading the server health'))
  await showStatus($).catch(shownAsFailure($, 'The status line was not shown', 'Sending a prompt, showing the session folder'))
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'board', description: 'Open the CDD session board, starting it when it is not running' })
    await clearBusy($)
    const chat = await $.session.id()
    $.clock.every(CHECK_IN_MILLISECONDS, () => {
      if (!isCheckInDue()) return
      // The cdd server can still be connecting at session start; the next check-in tries again.
      void checkIn($, chat).catch(shownAsFailure($, 'This chat did not check in with the board', 'The check-in every second, calling chat.check_in'))
    })
    // The chat opens first and the bar fills in after it, so a slow or still-connecting cdd server never holds the chat up.
    const started = await next(e)
    void readBoardAfterStart($)
    return started
  })

  on('command.run', { command: 'board' }, async $ => ({ text: await openedBoard($) }))

  on('turn.start', async ($, e, next) => {
    if (!e.agentId) turnStarted()
    return next(e)
  })

  // The turn ends first and the bar is read again after it, so the next prompt does not wait on the cdd server.
  on('turn.complete', async ($, e, next) => {
    const finished = await next(e)
    void readBoardAfterTurn($, !e.agentId)
    return finished
  })

  // A cdd tool call names this chat for session.log. The agent changes the board through cdd's tools without telling
  // the mod, so a cdd tool call that finishes reads it again.
  on('tool.call', async ($, e, next) => {
    const ran = await next(await withChatNamed($, e))
    if (CDD_TOOL.test(e.tool)) {
      forgetFormatChips()
      await refreshChatBar($)
      await showStatus($)
    }
    return ran
  })

  // A press can change which fidelities or stage the action button acts on, so the format chips are read again after it.
  // A press anywhere else on the bar closes an open list box of options, as a click outside a menu does.
  on('ui.press', async ($, e, next) => {
    const pressed = await next(e)
    if (e.plugin === PLUGIN) await closeOptionListsOutside($, e.element)
    if (e.plugin === PLUGIN && CHANGES_FIDELITIES.test(e.element)) void loadFormatChips($, await currentChatBar($)).catch(shownAsFailure($, 'The format chips did not load', `Pressing ${e.element}, reading the format choices`))
    return pressed
  })

  // Typing in the prompt is a click outside the bar's list boxes: any one open closes.
  on('prompt.change', async ($, e, next) => {
    await closeOptionListsOutside($)
    return next(e)
  })

  // The prompt goes to the agent first and the bar is read again after it, so a prompt never waits on the cdd server.
  on('prompt.submit', async ($, e, next) => {
    await closeOptionListsOutside($)
    const submitted = await next(e)
    void readBoardAfterSubmit($)
    return submitted
  })

  // The status line, the whole path of the session's folder, sits in the hint line under the prompt, after
  // what the engine writes there, not in the chat bar above it.
  on('ui.render', { component: 'PromptHint' }, async ($, e, next) => {
    const status = (await currentChatBar($)).statusLine
    if (!status) return next(e)
    return next({ ...e, props: { ...e.props, hint: e.props.hint ? `${e.props.hint} · ${status}` : status } })
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)
    // A press on the health mark reads the board and the server again, and shows the card with the diagnostics open.
    const actions = {
      toggleCard: async () => {
        await Promise.all([clearBusy($), readActive($), refreshHealth($), openDetails($)])
        await toggleCard($)
      },
      openDetails: () => openDetails($),
      hideDetails: () => hideDetails($),
      reconnect: () => reconnect($, () => readActive($)),
      runInstall: () => runInstall($),
      // An app opens on the project this chat works in, its worktree for a ticket's chat, so it shows the session open
      // there, not the main checkout's; and on the folder that session works in, which the Graph loads.
      openApp: (label: string) =>
        openAppBesideChat($, label, async url => {
          const { workpath } = await currentChatBar($)
          return projectPageUrl($, url, { [PROJECT_QUERY]: await $.session.root(), ...(workpath ? { [FOLDER_QUERY]: workpath } : {}) })
        }),
    }
    const band = { health: await currentServerHealth($), view: await currentHealthView($), install: await currentInstall($), opening: await currentAppOpening($), actions }
    const elements = $.ui.resolve(e)
    try {
    const chatBar = await currentChatBar($)
    return ChatBarView($, elements, {
      chatBar,
      failure: await currentFailure($),
      formats: await currentFormatChips($, chatBar),
      overlays: await currentOverlayChips($, chatBar),
      view: await currentChatBarView($),
      picker: await currentActionPicker($),
      isStagePickerOpen: await isStagePickerOpen($),
      busy: await currentBusy($),
      health: { band: ServerHealthBandView(elements, band, CARD_SCOPE), panel: ServerHealthPanelView(elements, band) },
      width: e.props.bodyColumns,
    })
    } catch (failure) {
      // A draw that throws shows why, in red, instead of leaving no bar at all.
      return h(elements.Text, { color: '#EF4444' }, `chat bar failed to draw: ${failure instanceof Error ? `${failure.message}
${failure.stack ?? ''}` : String(failure)}`)
    }
  })

  // The help pane beside the chat: a fidelity's help, as the ? beside a practice on a board ticket shows it.
  on('ui.render', { component: 'Pane', requestId: HELP_PANE }, async ($, e) => FidelityHelpView($.ui.resolve(e), await currentFidelityHelp($)))

  on('ui.close', { id: HELP_PANE }, async ($, e, next) => {
    if (e.origin.kind === 'person') await forgetHelp($)
    return next(e)
  })

  on('prompt.compose', async ($, e, next) => {
    const composed = await next(e)
    if (!(await currentChatBar($)).hasSession) await readActive($)
    const { agentContext } = await currentChatBar($)
    if (!agentContext) return composed
    return { sections: [...composed.sections, { id: `${PLUGIN}:ticket`, text: agentContext, scope: 'session' as const }] }
  })
}
