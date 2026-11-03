import type { BoardData } from '@cdd/harness/kanban/board'
import type { TicketData } from '@cdd/harness/kanban/ticket'
import type { ChatCommandData } from '@cdd/tools/chat/chat'
import type { EngineInterface, Register } from 'claude-code'

// Connects this chat to cdd's chat tools, which the board sends commands through. The rules live in the cdd server.
const PLUGIN = 'cdd-board'
const SERVER = 'cdd'
const BOARD_URL = 'http://127.0.0.1:8778'
// The board refuses a POST without this header, so another page cannot act on it.
const BOARD_HEADERS = { 'X-CDD-Board': '1', 'Content-Type': 'application/json' }
const CHECK_IN_MILLISECONDS = 1000

const NAME_CHARACTERS = 48

let isBusy = false
let chatName = ''
let active: TicketData | undefined

// The engine queues a plugin's prompt until the chat is idle; one still queued this long after an idle chat took it is
// not coming, and the board says so instead of showing it as taken forever.
const SHOWN_WITHIN_MILLISECONDS = 20_000
// A slash command resolves only once it has finished, which for a skill takes minutes; the engine refuses one it cannot
// run straight away, so one not refused by now is running.
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
  return Promise.race([submitting, after($, SHOWN_WITHIN_MILLISECONDS, `the chat had not shown it ${SHOWN_WITHIN_MILLISECONDS / 1000} s after taking it`)])
}

// Why the chat did not show the command, or nothing once it did.
function shown($: EngineInterface, chat: string, command: ChatCommandData): Promise<string> {
  if (command.kind === 'fill') return filled($, command.text).catch(reasonOf)
  return command.text.startsWith('/') ? ranCommand($, chat, command) : submitted($, command.text)
}

// The board shows each message as shown or failed, so a message the chat could not take is never silent. A fill waits
// for the person to send it, so only a command or a submit has work for the chat to finish.
async function run($: EngineInterface, chat: string, command: ChatCommandData): Promise<void> {
  $.ui.toast(`Board message arrived: ${command.text}`)
  if (command.kind !== 'fill') unfinished.set(command.message, turnsStarted)
  const reason = await shown($, chat, command)
  $.ui.toast(reason ? `Board message failed: ${reason}: ${command.text}` : `Board sent: ${command.text}`)
  if (reason) unfinished.delete(command.message)
  await post($, chat, 'confirm', { message: command.message, is_shown: !reason, reason })
}

function post($: EngineInterface, chat: string, operation: string, body: object) {
  return $.http.fetch(`${BOARD_URL}/api/chat/${encodeURIComponent(chat)}/${operation}`, { method: 'POST', headers: BOARD_HEADERS, body: JSON.stringify(body) })
}

// Checks in through the board's own cdd server, which runs chat.check_in. A chat's cdd server keeps the code it started
// with, so one started before the chat tools existed could never check in; the board always runs the current code.
async function checkIn($: EngineInterface, chat: string): Promise<void> {
  const answer = await post($, chat, 'check-in', { is_busy: isBusy, name: chatName })
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

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'board', description: 'Say where the CDD session board is' })
    const chat = await $.session.id()
    await readName($).catch(() => undefined)
    $.clock.every(CHECK_IN_MILLISECONDS, () => {
      // The cdd server can still be connecting at session start; the next check-in tries again.
      void checkIn($, chat).catch(() => undefined)
    })
    await readActive($)
    return next(e)
  })

  on('command.run', { command: 'board' }, async () => ({ text: `The board is at ${BOARD_URL}. Start it with: npm start, in harness/kanban/app.` }))

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
    await readActive($)
    return finished
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
