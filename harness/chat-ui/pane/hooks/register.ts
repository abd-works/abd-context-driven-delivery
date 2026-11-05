import type { BoardData } from '@cdd/harness/kanban/board'
import type { TicketData } from '@cdd/harness/kanban/ticket'
import type { ChatCommandData } from '@cdd/tools/chat/chat'
import type { EngineInterface, Register } from 'claude-code'

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
  SERVER,
  togglePin,
} from './health/server-health-client'
import { ServerHealthBandView } from './health/server-health-view'

// Connects this chat to cdd's chat tools, which the board sends commands through. The rules live in the cdd server.
const PLUGIN = 'cdd-board'
const BOARD_URL = 'http://127.0.0.1:8778'
// The board refuses a POST without this header, so another page cannot act on it.
const BOARD_HEADERS = { 'X-CDD-Board': '1', 'Content-Type': 'application/json' }
const CHECK_IN_MILLISECONDS = 1000

const NAME_CHARACTERS = 48

let isBusy = false
let chatName = ''
let active: TicketData | undefined

// The engine queues a plugin's prompt or slash command until the chat is idle, the same queue a person's Ctrl+Enter
// uses, and either resolves only once it has run. It refuses one it will not take straight away, so one not refused by
// now waits in that queue or is running.
const REFUSED_WITHIN_MILLISECONDS = 3_000

const after = ($: EngineInterface, milliseconds: number, answer: string): Promise<string> => new Promise(resolve => $.clock.after(milliseconds, () => resolve(answer)))

const reasonOf = (error: unknown): string => (error instanceof Error ? error.message : String(error))

// Messages the chat showed and is still working on, each with the turns started before it arrived; a message is done
// when a turn that started after it ends, not the turn the chat was already in.
const unfinished = new Map<string, number>()
// Counts the chat's own turns, so a command that returned without starting one is known to be done.
let turnsStarted = 0

// A slash command runs as if the person typed it, its line in the transcript; the engine refuses a submitted prompt
// that starts with a slash.
function ranCommand($: EngineInterface, chat: string, command: ChatCommandData): Promise<string> {
  const [name = '', ...words] = command.text.slice(1).split(' ')
  const turnsBefore = turnsStarted
  const running = $.command.run({ command: name, args: words.join(' ') }).then(() => '', reasonOf)
  // A command that printed its line and started no turn, such as /board, is done once it returns.
  void running.then(reason => {
    if (!reason && turnsStarted === turnsBefore && !isBusy) void finish($, chat, command.message)
  })
  return Promise.race([running, after($, REFUSED_WITHIN_MILLISECONDS, '')])
}

async function finish($: EngineInterface, chat: string, message: string): Promise<void> {
  if (!unfinished.delete(message)) return
  await post($, chat, 'finish', { message })
}

// Adds to the box, so a draft the person is typing stays.
async function filled($: EngineInterface, text: string): Promise<string> {
  const answer = await $.prompt.fill({ text, mode: 'append' })
  return answer.isFilled ? '' : `the prompt box did not take it (${answer.refusal ?? 'refused by a hook'})`
}

// Any other text arrives as the person's own message, the same as typing it.
function submitted($: EngineInterface, text: string): Promise<string> {
  const submitting = $.prompt.submit({ text, asUser: true }).then(answer => (answer.drop === undefined ? '' : `the chat dropped it: ${answer.drop || 'no reason given'}`), reasonOf)
  return Promise.race([submitting, after($, REFUSED_WITHIN_MILLISECONDS, '')])
}

// The engine refuses a plugin's command in some states, such as after the person stopped the session and has typed
// nothing since. The command then waits in the prompt box for the person to send, so it is never lost; once they send
// it, its turn finishes it like any other.
async function ranOrFilled($: EngineInterface, chat: string, command: ChatCommandData): Promise<string> {
  const refusal = await ranCommand($, chat, command)
  if (!refusal) return ''
  const unfilled = await filled($, command.text).catch(reasonOf)
  if (unfilled) return `${refusal}; ${unfilled}`
  $.ui.toast(`The chat would not run ${command.text} (${refusal}), so it is in the prompt box: press Enter to send it`)
  return ''
}

// Why the chat did not show the command, or nothing once it did.
function shown($: EngineInterface, chat: string, command: ChatCommandData): Promise<string> {
  if (command.kind === 'fill') return filled($, command.text).catch(reasonOf)
  return command.text.startsWith('/') ? ranOrFilled($, chat, command) : submitted($, command.text)
}

// The board shows each message as shown or failed, so a message the chat could not take is never silent. A fill waits
// for the person to send it, so only a command or a submit has work for the chat to finish.
async function run($: EngineInterface, chat: string, command: ChatCommandData): Promise<void> {
  const hasTurn = command.kind === 'command' || command.kind === 'submit'
  $.ui.toast(`Board message arrived: ${command.text}`)
  if (hasTurn) unfinished.set(command.message, turnsStarted)
  const reason = await shown($, chat, command)
  $.ui.toast(reason ? `Board message failed: ${reason}: ${command.text}` : `Board sent: ${command.text}`)
  if (reason) unfinished.delete(command.message)
  await post($, chat, 'confirm', { message: command.message, is_shown: !reason, reason })
}

function post($: EngineInterface, chat: string, operation: string, body: object) {
  return $.http.fetch(`${BOARD_URL}/api/chat/${encodeURIComponent(chat)}/${operation}`, { method: 'POST', headers: BOARD_HEADERS, body: JSON.stringify(body) })
}

// Checks in through the board, which runs chat.check_in on the cdd server every chat shares. The folder the chat works in
// lets the board find a ticket's chat: the one working in the ticket's worktree.
async function checkIn($: EngineInterface, chat: string): Promise<void> {
  const answer = await post($, chat, 'check-in', { is_busy: isBusy, name: chatName, folder: await $.session.cwd() })
  if (!answer.ok) return
  for (const command of JSON.parse(answer.text) as ChatCommandData[]) await run($, chat, command)
}

// A compacted chat opens with its summary, not with anything the person typed, so that message names nothing.
const SUMMARY_OPENINGS = ['This session is being continued', 'The summarized conversation']

// What a person typed, without the notices the app wraps in tags, inside and all.
const typedText = (text: string): string =>
  text
    .replace(/<([a-z][\w-]*)[^>]*>[\s\S]*?<\/\1>/gi, ' ')
    .replace(/<[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

// A mod cannot read the title the app shows for a chat, so the board names it by its folder and the first thing the
// person typed. The board keeps sending to the chat's id; the name is only what a person reads in its picker.
async function readName($: EngineInterface): Promise<void> {
  const folder = (await $.session.cwd()).split(/[\\/]/).filter(Boolean).at(-1) ?? ''
  const typed = (await $.session.messages()).filter(message => message.role === 'user').map(message => typedText(message.text))
  const opening = typed.find(text => text && !SUMMARY_OPENINGS.some(summary => text.startsWith(summary))) ?? ''
  const words = opening.length > NAME_CHARACTERS ? `${opening.slice(0, NAME_CHARACTERS)}…` : opening
  chatName = [folder, words].filter(Boolean).join(' · ')
}

const statusOf = (ticket: TicketData): string => {
  const violations = Object.values(ticket.progress).filter(state => state === 'violations').length
  return [ticket.name, ticket.column, ticket.next ? `next: ${ticket.next}` : ticket.is_done ? 'done' : '', violations ? `${violations} with violations` : ''].filter(Boolean).join(' · ')
}

// The cdd server can still be connecting at session start, so a failed read waits for the next event.
async function readActive($: EngineInterface): Promise<void> {
  const result = await $.mcp.call(SERVER, 'board.show', {}).catch(() => null)
  const text = result?.content[0]?.text
  if (!text || result.isError) return
  const board = JSON.parse(text) as BoardData
  const tickets = board.columns.flatMap(column => [...(column.in_progress ?? []), ...(column.done ?? []), ...(column.tickets ?? [])])
  const found = tickets.find(ticket => ticket.name === board.active)
  // The system prompt is cached; when the active ticket's summary changes, it is composed again next turn.
  if ((found && statusOf(found)) !== (active && statusOf(active))) await $.ui.invalidate('prompt.section')
  active = found
  $.ui.status(found ? statusOf(found) : undefined)
}

const BOARD_APP = 'harness/kanban/app'
const START_BY_HAND = `Start it with: npm install, npm run build, then npm start, in ${BOARD_APP}.`
const STARTED_WITHIN_MILLISECONDS = 20_000
const STARTED_CHECK_MILLISECONDS = 500

const isBoardUp = ($: EngineInterface): Promise<boolean> =>
  $.http
    .fetch(`${BOARD_URL}/api/build`)
    .then(answer => answer.ok)
    .catch(() => false)

async function boardAppFolder($: EngineInterface): Promise<string> {
  const { exitCode, stdout } = await $.process.run(['git', 'rev-parse', '--show-toplevel'])
  return exitCode === 0 ? `${stdout.trim()}/${BOARD_APP}` : ''
}

// The board lives as long as this chat's mod: leaving the loop, or the module unloading, ends the server.
function startServer($: EngineInterface, folder: string): void {
  void (async () => {
    const server = $.process.spawn({ argv: ['node', '--import', 'tsx', 'packages/session-board/serve.ts'], cwd: folder })
    for await (const { text } of server) $.ui.log(text, { to: 'debug' })
  })().catch(error => $.ui.log(`The session board stopped: ${reasonOf(error)}`, { to: 'debug' }))
}

async function cameUp($: EngineInterface): Promise<boolean> {
  for (let waited = 0; waited < STARTED_WITHIN_MILLISECONDS; waited += STARTED_CHECK_MILLISECONDS) {
    if (await isBoardUp($)) return true
    await after($, STARTED_CHECK_MILLISECONDS, '')
  }
  return false
}

// Starts the board when nothing answers on its port, so /board always ends with a board to open.
async function openedBoard($: EngineInterface): Promise<string> {
  if (await isBoardUp($)) return `The board is at ${BOARD_URL}.`
  const folder = await boardAppFolder($)
  if (!folder || !(await $.fs.exists(`${folder}/node_modules`)) || !(await $.fs.exists(`${folder}/dist`))) return `The board is not running and is not installed here. ${START_BY_HAND}`
  startServer($, folder)
  return (await cameUp($)) ? `Started the board at ${BOARD_URL}. It stops when this chat ends.` : `The board did not start within ${STARTED_WITHIN_MILLISECONDS / 1000} s. ${START_BY_HAND}`
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'board', description: 'Open the CDD session board, starting it when it is not running' })
    const chat = await $.session.id()
    await readName($).catch(() => undefined)
    $.clock.every(CHECK_IN_MILLISECONDS, () => {
      // The cdd server can still be connecting at session start; the next check-in tries again.
      void checkIn($, chat).catch(() => undefined)
    })
    await readActive($)
    refreshHealthSoon($)
    return next(e)
  })

  on('command.run', { command: 'board' }, async $ => ({ text: await openedBoard($) }))

  on('turn.start', async ($, e, next) => {
    if (!e.agentId) {
      isBusy = true
      turnsStarted += 1
    }
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const finished = await next(e)
    if (!e.agentId) {
      isBusy = false
      const chat = await $.session.id()
      for (const [message, turnsBefore] of [...unfinished]) if (turnsStarted > turnsBefore) await finish($, chat, message)
    }
    await readName($).catch(() => undefined)
    await Promise.all([readActive($), refreshHealth($)])
    return finished
  })

  on('prompt.submit', async ($, e, next) => {
    await refreshHealth($)
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)
    const actions = {
      togglePin: () => togglePin($),
      openDetails: () => openDetails($),
      hideDetails: () => hideDetails($),
      reconnect: () => reconnect($, () => readActive($)),
      runInstall: () => runInstall($),
    }
    const band = {
      health: await currentServerHealth($),
      view: await currentHealthView($),
      install: await currentInstall($),
      actions,
    }
    return ServerHealthBandView($.ui.resolve(e), band)
  })

  on('prompt.compose', async ($, e, next) => {
    const composed = await next(e)
    if (!active) await readActive($)
    if (!active) return composed
    const text =
      `CDD session board: you are working on ticket ${active.name} ("${active.title}"), in ${active.column}. ` +
      (active.next ? `Its next guidance is ${active.next}. ` : 'Its stage is done and waits for a person to move it. ') +
      'Each fidelity goes through generate, validate, then review, which a person records on the board.'
    return { sections: [...composed.sections, { id: `${PLUGIN}:ticket`, text, scope: 'session' as const }] }
  })
}
