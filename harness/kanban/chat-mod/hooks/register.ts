import type { BoardData } from '@cdd/harness/kanban/board'
import type { TicketData } from '@cdd/harness/kanban/ticket'
import type { EngineInterface, Register } from 'claude-code'

// Connects this chat to the board app. The page and its rules live in harness/kanban/app and the cdd server.
const PLUGIN = 'cdd-board'
const SERVER = 'cdd'
const BOARD_URL = 'http://127.0.0.1:8778'
const POLL_MILLISECONDS = 1000

type Command = { kind: 'submit' | 'fill' | 'command'; text: string }

let isBusy = false
let active: TicketData | undefined

const post = ($: EngineInterface, path: string, body: unknown) =>
  $.http.fetch(`${BOARD_URL}${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CDD-Board': '1' }, body: JSON.stringify(body) })

async function run($: EngineInterface, command: Command): Promise<void> {
  if (command.kind === 'submit') void $.prompt.submit({ text: command.text })
  // Adds to the box, so a draft the person is typing stays.
  if (command.kind === 'fill') await $.prompt.fill({ text: command.text, mode: 'append' })
  if (command.kind === 'command') {
    const [name = '', ...words] = command.text.slice(1).split(' ')
    await $.command.run({ command: name, args: words.join(' ') })
  }
}

async function poll($: EngineInterface, chat: string): Promise<void> {
  const response = await post($, `/api/chats/${encodeURIComponent(chat)}/next`, { is_busy: isBusy })
  const command = JSON.parse(response.text) as Command | null
  if (command) await run($, command)
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
    $.clock.every(POLL_MILLISECONDS, () => {
      // The board app may not be running; the next poll tries again.
      void poll($, chat).catch(() => undefined)
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
      'Each fidelity goes through generate, validate, then /review by a person.'
    return { sections: [...composed.sections, { id: `${PLUGIN}:ticket`, text, scope: 'session' as const }] }
  })
}
