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
import { currentFidelityFiles, FILES_PANE, forgetFiles } from './chat-bar/fidelity-files-client'
import { currentFidelityHelp, forgetHelp, HELP_PANE } from './chat-bar/fidelity-help-client'
import { FidelityHelpView } from './chat-bar/fidelity-help-view'
import { FidelityFilesView } from './chat-bar/fidelity-files-view'
import { currentChatBarView } from './chat-bar/session-dialogs-client'
import { closeOptionListsOutside } from './chat-bar/option-lists-client'
import { reasonOf } from './shared/failure'
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
import { openApp, type AppName } from './health/open-app-client'
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

// A failure the mod rides over, such as the cdd server still connecting, goes to the debug log, never nowhere.
function logged($: EngineInterface, doing: string): (failure: unknown) => void {
  return failure => $.ui.log(`${PLUGIN}: ${doing} failed: ${reasonOf(failure)}`, { to: 'debug' })
}

// The host draws a plugin's status at the right of the line below the chat and cannot set it left, so the chat bar
// draws its own status row instead, and the host's line is cleared of what an earlier version showed there.
function clearStatus($: EngineInterface): void {
  $.ui.status(undefined)
}

// The system prompt and the chat bar read the same ChatBarClient. The cdd server can still be
// connecting at session start; the chat bar then shows why, and the next event reads again.
async function readActive($: EngineInterface): Promise<void> {
  await refreshChatBar($)
  const chatBar = await currentChatBar($)
  if (chatBar.problem) return
  await loadFormatChips($, chatBar)
  await loadOverlayChoices($, chatBar).catch(logged($, 'reading the overlay choices'))
  // The system prompt is cached; when the active session's summary changes, it is composed again next turn.
  if (chatBar.agentContext !== shownContext) await $.ui.invalidate('prompt.section')
  shownContext = chatBar.agentContext
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'board', description: 'Open the CDD session board, starting it when it is not running' })
    await clearBusy($)
    const chat = await $.session.id()
    await readName($).catch(logged($, 'naming the chat'))
    $.clock.every(CHECK_IN_MILLISECONDS, () => {
      if (!isCheckInDue()) return
      // The cdd server can still be connecting at session start; the next check-in tries again.
      void checkIn($, chat).catch(logged($, 'checking in with the board'))
    })
    clearStatus($)
    await readActive($)
    refreshHealthSoon($)
    return next(e)
  })

  on('command.run', { command: 'board' }, async $ => ({ text: await openedBoard($) }))

  on('turn.start', async ($, e, next) => {
    if (!e.agentId) turnStarted()
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const finished = await next(e)
    if (!e.agentId) await turnCompleted($)
    await readName($).catch(logged($, 'naming the chat'))
    await Promise.all([readActive($), refreshHealth($)])
    return finished
  })

  // A cdd tool call names this chat for session.log. The agent changes the board through cdd's tools without telling
  // the mod, so a cdd tool call that finishes reads it again.
  on('tool.call', async ($, e, next) => {
    const ran = await next(await withChatNamed($, e))
    if (CDD_TOOL.test(e.tool)) {
      forgetFormatChips()
      await refreshChatBar($)
    }
    return ran
  })

  // A press can change which fidelities or stage the action button acts on, so the format chips are read again after it.
  // A press anywhere else on the bar closes an open list box of options, as a click outside a menu does.
  on('ui.press', async ($, e, next) => {
    const pressed = await next(e)
    if (e.plugin === PLUGIN) await closeOptionListsOutside($, e.element)
    if (e.plugin === PLUGIN && CHANGES_FIDELITIES.test(e.element)) void loadFormatChips($, await currentChatBar($)).catch(logged($, 'reading the format chips'))
    return pressed
  })

  // Typing in the prompt is a click outside the bar's list boxes: any one open closes.
  on('prompt.change', async ($, e, next) => {
    await closeOptionListsOutside($)
    return next(e)
  })

  on('prompt.submit', async ($, e, next) => {
    await closeOptionListsOutside($)
    await Promise.all([refreshHealth($), refreshChatBar($)])
    return next(e)
  })

  // The status line, the repository, the session's branch and its folder, sits in the hint line under the prompt, after
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
      // Starting the Graph app can take a minute, so the press returns at once and the app opens when it answers.
      openApp: (app: AppName) => void openApp($, app).catch(logged($, `opening the ${app}`)),
    }
    const band = { health: await currentServerHealth($), view: await currentHealthView($), install: await currentInstall($), actions }
    const elements = $.ui.resolve(e)
    try {
    const chatBar = await currentChatBar($)
    return ChatBarView($, elements, {
      chatBar,
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

  // The files pane beside the chat: a fidelity's files or its validation report, never drawn in the chat itself.
  on('ui.render', { component: 'Pane', requestId: FILES_PANE }, async ($, e) => FidelityFilesView($, $.ui.resolve(e), await currentFidelityFiles($)))

  on('ui.close', { id: FILES_PANE }, async ($, e, next) => {
    if (e.origin.kind === 'person') await forgetFiles($)
    return next(e)
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
