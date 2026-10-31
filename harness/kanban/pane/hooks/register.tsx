import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { BoardJson, ColumnJson, TicketJson } from '../types'

// Draws the CDD session board from the cdd MCP server's kanban tools; the board's rules live there.
const PLUGIN = 'cdd-board'
const PANE = 'cdd-board'
const SERVER = 'cdd'
const STATE_COLOR: Record<string, 'success' | 'error' | 'warning' | 'inactive'> = {
  done: 'success',
  violations: 'error',
  in_progress: 'warning',
  not_started: 'inactive',
}

// Change the tag when the board's shape changes: it declines what an earlier version stored.
const board = atom({ plugin: 'cdd-board', key: 'board' } as const, null as BoardJson | null, { shape: 'board-1' })
const selected = atom({ plugin: 'cdd-board', key: 'selected' } as const, null as string | null)

const ticketsOf = (column: ColumnJson): TicketJson[] => [
  ...(column.in_progress ?? []),
  ...(column.done ?? []),
  ...(column.tickets ?? []),
]

const allTickets = (shown: BoardJson): TicketJson[] => shown.columns.flatMap(ticketsOf)

const activeTicket = (shown: BoardJson): TicketJson | undefined =>
  allTickets(shown).find(ticket => ticket.name === shown.active)

const violationsOf = (ticket: TicketJson): string[] =>
  Object.entries(ticket.progress)
    .filter(([, state]) => state === 'violations')
    .map(([slug]) => slug)

const statusOf = (ticket: TicketJson): string =>
  [ticket.name, ticket.column, ticket.next ? `next: ${ticket.next}` : ticket.is_done ? 'ready to pull' : '']
    .filter(Boolean)
    .join(' · ')

async function callBoard($: EngineInterface, tool: string, args: Record<string, unknown>): Promise<unknown> {
  let result
  try {
    result = await $.mcp.call(SERVER, tool, args)
  } catch (failure) {
    // The cdd server is not connected: say so on the status line rather than fail the hook.
    $.ui.status(`cdd board: ${String(failure)}`)
    return null
  }
  const text = result.content[0]?.text
  if (result.isError || text === undefined) {
    $.ui.toast(`cdd ${tool} failed${text ? `: ${text}` : ''}`)
    return null
  }
  return JSON.parse(text)
}

function announceChanges($: EngineInterface, before: BoardJson | null, after: BoardJson): void {
  if (!before) return
  const earlier = new Map(allTickets(before).map(ticket => [ticket.name, ticket]))
  for (const ticket of allTickets(after)) {
    const was = earlier.get(ticket.name)
    if (!was) continue
    if (was.column !== ticket.column) $.ui.toast(`${ticket.name} moved to ${ticket.column}`)
    for (const [slug, state] of Object.entries(ticket.progress)) {
      if (state === 'done' && was.progress[slug] !== 'done') $.ui.toast(`${slug} done on ${ticket.name}`)
    }
  }
}

async function refresh($: EngineInterface): Promise<void> {
  const shown = (await callBoard($, 'kanban.board', {})) as BoardJson | null
  if (!shown) return
  const before = await read($, board)
  await update($, board, () => shown)
  announceChanges($, before, shown)
  const active = activeTicket(shown)
  $.ui.status(active ? statusOf(active) : undefined)
  // The system prompt is cached; when the active ticket's summary changes, it is composed again next turn.
  const wasActive = before ? activeTicket(before) : undefined
  if (!before || (wasActive ? statusOf(wasActive) : '') !== (active ? statusOf(active) : '')) {
    await $.ui.invalidate('prompt.section')
  }
}

async function act($: EngineInterface, tool: string, ticket: string): Promise<void> {
  await callBoard($, tool, { ticket })
  await refresh($)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'board', description: 'Show the CDD session board beside the chat' })
    void $.ui.open({ id: PANE, title: 'Board' })
    await refresh($)
    return next(e)
  })

  on('command.run', { command: 'board' }, async $ => {
    await $.ui.open({ id: PANE, title: 'Board' })
    await refresh($)
    return { text: 'Board opened.' }
  })

  // The cdd server can still be connecting at session start; by the first prompt it answers.
  on('prompt.submit', async ($, e, next) => {
    await refresh($)
    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    if (e.tool.startsWith(`mcp__${SERVER}__`)) await refresh($)
    return ran
  })

  on('prompt.compose', async ($, e, next) => {
    const composed = await next(e)
    // The first prompt is composed before the first prompt.submit; read the board here if it is still empty.
    if (!(await read($, board))) await refresh($)
    const shown = await read($, board)
    const active = shown ? activeTicket(shown) : undefined
    if (!active) return composed
    const text =
      `CDD session board: you are working on ticket ${active.name} ("${active.title}"), in ${active.column}. ` +
      (active.next ? `Its next guidance is ${active.next}. ` : 'Its stage is done and waits to be pulled. ') +
      'Each fidelity goes through generate, validate, then /review by a person.'
    return { sections: [...composed.sections, { id: `${PLUGIN}:ticket`, text, scope: 'session' as const }] }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const shown = await read($, board)
    const active = shown ? activeTicket(shown) : undefined
    const violations = active ? violationsOf(active) : []
    if (!active || violations.length === 0) return next(e)
    const { Box, Button, Text } = $.ui.resolve(e)
    return (
      <Box flexDirection="row" gap={1}>
        <Text color="error">
          {active.name} · {active.column} · violations: {violations.join(', ')}
        </Text>
        <Button key="open-board" label="Board" onPress={() => $.ui.open({ id: PANE, title: 'Board' })} />
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Button, Text } = $.ui.resolve(e)
    const shown = await read($, board)
    if (!shown) return <Text dimColor>No board yet: is the cdd MCP server connected?</Text>
    const chosenName = (await read($, selected)) ?? shown.active
    const chosen = allTickets(shown).find(ticket => ticket.name === chosenName)

    const card = (ticket: TicketJson) => (
      <Button key={`ticket-${ticket.name}`} onPress={() => update($, selected, () => ticket.name)}>
        {ticket.name === shown.active ? '▸ ' : ''}
        {ticket.title} <Text dimColor>{ticket.next ?? (ticket.is_done ? 'ready to pull' : '')}</Text>
      </Button>
    )

    const column = (shownColumn: ColumnJson) => (
      <Box key={`column-${shownColumn.name}`} flexDirection="column">
        <Text bold>
          {shownColumn.name} ({shownColumn.items ? shownColumn.items.length : ticketsOf(shownColumn).length})
        </Text>
        {(shownColumn.items ?? []).map(item => (
          <Text>{item.title}</Text>
        ))}
        {shownColumn.in_progress ? <Text dimColor>in progress</Text> : null}
        {(shownColumn.in_progress ?? []).map(card)}
        {shownColumn.done ? <Text dimColor>done</Text> : null}
        {(shownColumn.done ?? []).map(card)}
        {(shownColumn.tickets ?? []).map(card)}
      </Box>
    )

    const detail = (ticket: TicketJson) => (
      <Box key="detail" flexDirection="column">
        <Text bold>
          {ticket.title} <Text dimColor>{statusOf(ticket)}</Text>
        </Text>
        {shown.columns
          .filter(stage => stage.work_required)
          .map(stage => (
            <Text>
              {stage.name}:{' '}
              {(stage.work_required ?? []).map(slug => (
                <Text color={STATE_COLOR[ticket.progress[slug] ?? 'not_started']}>{slug} </Text>
              ))}
            </Text>
          ))}
        <Box key="actions" flexDirection="row" gap={1}>
          <Button key="pull" label="Pull" onPress={() => act($, 'kanban.pull', ticket.name)} />
          <Button
            key="run-next"
            label="Run next"
            onPress={() =>
              $.prompt.fill({
                text: `Work on ${ticket.next ?? 'the next stage'} for ticket ${ticket.name}: run its next action (generate, validate, or /review).`,
                mode: 'replace',
              })
            }
          />
          <Button key="close" label="Close" onPress={() => act($, 'kanban.close', ticket.name)} />
        </Box>
      </Box>
    )

    return (
      <Box flexDirection="column" gap={1}>
        <Box key="columns" flexDirection="row" gap={2}>
          {shown.columns.map(column)}
        </Box>
        {chosen ? detail(chosen) : null}
      </Box>
    )
  })
}
