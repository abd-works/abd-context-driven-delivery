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

// Every command the board sends shows in the chat: a command or a submit arrives as the person's own message, the
// same as typing it, so the transcript always holds what ran; a fill shows in the prompt box.
async function run($: EngineInterface, command: ChatCommandData): Promise<void> {
  $.ui.toast(`Board sent: ${command.text}`)
  // Adds to the box, so a draft the person is typing stays.
  if (command.kind === 'fill') await $.prompt.fill({ text: command.text, mode: 'append' })
  else void $.prompt.submit({ text: command.text, asUser: true })
}

// Checks in through the board's own cdd server, which runs chat.check_in. A chat's cdd server keeps the code it started
// with, so one started before the chat tools existed could never check in; the board always runs the current code.
async function checkIn($: EngineInterface, chat: string): Promise<void> {
  const answer = await $.http.fetch(`${BOARD_URL}/api/chat/${encodeURIComponent(chat)}/check-in`, {
    method: 'POST',
    headers: BOARD_HEADERS,
    body: JSON.stringify({ is_busy: isBusy, name: chatName }),
  })
  if (!answer.ok) return
  for (const command of JSON.parse(answer.text) as ChatCommandData[]) await run($, command)
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
    if (!e.agentId) isBusy = true
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const finished = await next(e)
    if (!e.agentId) isBusy = false
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
