import type { EngineInterface, Register } from 'claude-code'

import { checkIn } from './board-chat/board-chat-client'
import { turnCompleted, turnStarted } from './board-chat/chat-turns'
import { readName } from './board-chat/chat-name'
import { openedBoard } from './board-chat/board-server'
import { currentChatBar, refreshChatBar } from './chat-bar/chat-bar-client'
import { ChatBarView } from './chat-bar/chat-bar-view'
import { checkChatFolder, currentChatFolder } from './chat-bar/chat-folder-client'
import { currentActionPicker } from './chat-bar/action-picker-client'
import { currentFidelityFiles, FILES_PANE, forgetFiles } from './chat-bar/fidelity-files-client'
import { FidelityFilesView } from './chat-bar/fidelity-files-view'
import { currentChatBarView } from './chat-bar/session-dialogs-client'
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
import { CARD_SCOPE } from './chat-bar/session-card-view'
import { toggleCard } from './chat-bar/session-dialogs-client'
import { withChatNamed } from './session/session-log-client'

const PLUGIN = 'cdd-board'
const CHECK_IN_MILLISECONDS = 1000
const CDD_TOOL = /^mcp__(plugin_cdd_)?cdd__/

// The status line the chat last showed, so the cached system prompt is composed again only when it changes.
let shownStatus = ''

// A failure the mod rides over, such as the cdd server still connecting, goes to the debug log, never nowhere.
function logged($: EngineInterface, doing: string): (failure: unknown) => void {
  return failure => $.ui.log(`${PLUGIN}: ${doing} failed: ${reasonOf(failure)}`, { to: 'debug' })
}

// The status line, the system prompt and the chat bar read the same ChatBarClient. The cdd server can still be
// connecting at session start; the chat bar then shows why, and the next event reads again.
async function readActive($: EngineInterface): Promise<void> {
  await refreshChatBar($)
  const chatBar = await currentChatBar($)
  if (chatBar.problem) return
  await checkChatFolder($, chatBar)
  // The system prompt is cached; when the active session's summary changes, it is composed again next turn.
  if (chatBar.statusLine !== shownStatus) await $.ui.invalidate('prompt.section')
  shownStatus = chatBar.statusLine
  $.ui.status(chatBar.statusLine || undefined)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'board', description: 'Open the CDD session board, starting it when it is not running' })
    const chat = await $.session.id()
    await readName($).catch(logged($, 'naming the chat'))
    $.clock.every(CHECK_IN_MILLISECONDS, () => {
      // The cdd server can still be connecting at session start; the next check-in tries again.
      void checkIn($, chat).catch(logged($, 'checking in with the board'))
    })
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
    if (CDD_TOOL.test(e.tool)) await refreshChatBar($)
    return ran
  })

  on('prompt.submit', async ($, e, next) => {
    await Promise.all([refreshHealth($), refreshChatBar($)])
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)
    const actions = {
      toggleCard: () => toggleCard($),
      openDetails: () => openDetails($),
      hideDetails: () => hideDetails($),
      reconnect: () => reconnect($, () => readActive($)),
      runInstall: () => runInstall($),
    }
    const band = { health: await currentServerHealth($), view: await currentHealthView($), install: await currentInstall($), actions }
    const elements = $.ui.resolve(e)
    return ChatBarView($, elements, {
      chatBar: await currentChatBar($),
      view: await currentChatBarView($),
      picker: await currentActionPicker($),
      folder: await currentChatFolder($),
      health: { band: ServerHealthBandView(elements, band, CARD_SCOPE), panel: ServerHealthPanelView(elements, band) },
      width: e.props.bodyColumns,
    })
  })

  // The files pane beside the chat: a fidelity's files or its validation report, never drawn in the chat itself.
  on('ui.render', { component: 'Pane', requestId: FILES_PANE }, async ($, e) => FidelityFilesView($, $.ui.resolve(e), await currentFidelityFiles($)))

  on('ui.close', { id: FILES_PANE }, async ($, e, next) => {
    if (e.origin.kind === 'person') await forgetFiles($)
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
