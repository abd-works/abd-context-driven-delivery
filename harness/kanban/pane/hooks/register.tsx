import { atom, read, update } from 'claude-code'
import type { ElementTable, EngineInterface, Register } from 'claude-code'

import type { BacklogItemJson, BoardJson, ColumnJson, SplitLayoutJson, TicketCardJson, TicketJson } from '../types'

// Draws the CDD session board from the cdd MCP server's kanban tools; the board's rules live there.
const PLUGIN = 'cdd-board'
const PANE = 'cdd-board'
const SERVER = 'cdd'
const BACKLOG = 'Backlog'
const FIRST_STAGE = 'Discovery'
const FINAL_STAGE = 'Implementation'
const WIDE_PANE_COLUMNS = 140
const BOARD_SHARE = 0.6
const MINIMUM_REGION_ROWS = 6
const MAXIMUM_HOVER_SCOPE = 64
const SURFACE_MODULE_SURFACES: string[] = ['terminal', 'desktop']

// abd.works engineering (dark) tokens, from the brand repository's css/brand.css. The pane paints its own canvas,
// so these colors hold on either Claude Code theme.
const BRAND = {
  canvas: '#0B0B0B',
  surface: '#111113',
  raised: '#1B1B20',
  border: '#2A2A2A',
  text: '#E8E8ED',
  muted: '#9B9BA8',
  idle: '#71717A',
  accent: '#E5531A',
  success: '#22C55E',
  warning: '#F59E0B',
  error: '#EF4444',
}

const STATES: Record<string, { label: string; color: string }> = {
  done: { label: 'reviewed', color: BRAND.success },
  in_progress: { label: 'in progress', color: BRAND.warning },
  violations: { label: 'violations', color: BRAND.error },
  not_started: { label: 'not started', color: BRAND.idle },
}

const PRACTICES = [
  { name: 'Stories', prefix: 'stories-' },
  { name: 'DDD', prefix: 'ddd-' },
  { name: 'UX', prefix: 'ux-' },
  { name: 'CE', prefix: 'clean_engineering-' },
  { name: 'BDD', prefix: 'bdd-' },
]

// The board's stages and the details' stages share these, so Discovery sits over Discovery all the way down.
const EDGE_COLUMN_WIDTH = '14%'
const STAGE_WIDTH = '23%'
const COLUMN_GAP = 1

// The brand's chevron: the symbol-only mark is the one for compact product UI.
const CHEVRON =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><path fill="#e5531a" fill-rule="evenodd" ' +
  'd="M52.98,20.31l150.04,84.18v46.44S52.98,235.69,52.98,235.69v-54.77s104.7-53.41,104.7-53.41l-104.7-52.83V20.31Z"/></svg>'
const CHEVRON_PIXELS = 18

const TICKET_ACTIONS: Record<string, { tool: string; argument: string }> = {
  close: { tool: 'kanban.close', argument: 'ticket' },
  switch: { tool: 'session.switch', argument: 'name' },
}

const MINUTE = 60_000
const MINUTES_PER_HOUR = 60
const HOURS_PER_DAY = 24

// Change the tag when the board's shape changes: it declines what an earlier version stored.
const board = atom({ plugin: 'cdd-board', key: 'board' } as const, null as BoardJson | null, { shape: 'board-2' })
const selected = atom({ plugin: 'cdd-board', key: 'selected' } as const, null as string | null)
const splitLayout = atom({ plugin: 'cdd-board', key: 'splitLayout' } as const, { expanded: null, boardRows: null } as SplitLayoutJson)
const surfaceModulesFailed = atom({ plugin: 'cdd-board', key: 'surfaceModulesFailed' } as const, false)

const ticketsOf = (column: ColumnJson): TicketJson[] => [
  ...(column.in_progress ?? []),
  ...(column.done ?? []),
  ...(column.tickets ?? []),
]

const allTickets = (shown: BoardJson): TicketJson[] => shown.columns.flatMap(ticketsOf)

const backlogItems = (shown: BoardJson): BacklogItemJson[] => shown.columns.flatMap(column => column.items ?? [])

const activeTicket = (shown: BoardJson): TicketJson | undefined =>
  allTickets(shown).find(ticket => ticket.name === shown.active)

// A session can sit in closed/ under the name of an open one, so a column and name together say which ticket is meant.
const ticketAddress = (ticket: TicketJson): string => `${ticket.column}/${ticket.name}`
const itemAddress = (item: BacklogItemJson): string => `${BACKLOG}/${item.title}`

const latestTicket = (shown: BoardJson): TicketJson | undefined =>
  [...allTickets(shown)].sort((one, other) => other.last_activity.localeCompare(one.last_activity))[0]

const violationsOf = (ticket: TicketJson): string[] =>
  Object.entries(ticket.progress)
    .filter(([, state]) => state === 'violations')
    .map(([slug]) => slug)

const statusOf = (ticket: TicketJson): string => {
  const violations = violationsOf(ticket).length
  return [
    ticket.name,
    ticket.column,
    ticket.next ? `next: ${ticket.next}` : ticket.is_done ? 'ready to pull' : '',
    violations ? `${violations} ${violations === 1 ? 'violation' : 'violations'}` : '',
  ]
    .filter(Boolean)
    .join(' · ')
}

const placeOf = (ticket: TicketJson): string => {
  const standing = ticket.column === 'Complete' ? '' : ticket.is_done ? 'done, ready to pull' : 'in progress'
  const origin = ticket.scope && ticket.parent ? `${ticket.scope} of ${ticket.parent}` : ticket.scope
  return [ticket.name, origin, ticket.column, standing].filter(Boolean).join(' · ')
}

const ageOf = (now: number, stamp: string): string => {
  if (!stamp) return 'no activity yet'
  const minutes = Math.floor((now - Date.parse(stamp)) / MINUTE)
  if (minutes < 1) return 'just now'
  if (minutes < MINUTES_PER_HOUR) return `${minutes} min ago`
  const hours = Math.floor(minutes / MINUTES_PER_HOUR)
  if (hours < HOURS_PER_DAY) return `${hours} hours ago`
  const days = Math.floor(hours / HOURS_PER_DAY)
  return days === 1 ? 'yesterday' : `${days} days ago`
}

const canMovePrevious = (ticket: TicketJson): boolean => ticket.column !== FIRST_STAGE
const canMoveNext = (ticket: TicketJson): boolean => ticket.column !== 'Complete'

const fidelityName = (slug: string, prefix: string): string => slug.slice(prefix.length)

const guidanceSlug = (slug: string): string => slug.replaceAll('_', '-')

// The practice's skill for a fidelity: `clean_engineering-code` is /practices-clean-engineering-clean-engineering-code.
const skillOf = (slug: string): string => {
  const practice = PRACTICES.find(candidate => slug.startsWith(candidate.prefix))
  return `/practices-${guidanceSlug(practice?.prefix ?? '')}${guidanceSlug(slug)}`
}

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
  const named = allTickets(after).map(ticket => ticket.name)
  for (const ticket of allTickets(after)) {
    const was = earlier.get(ticket.name)
    // A name held by an open and a closed session cannot be compared across reads, so it announces nothing.
    if (!was || named.indexOf(ticket.name) !== named.lastIndexOf(ticket.name)) continue
    if (was.column !== ticket.column) $.ui.toast(`${ticket.name} moved to ${ticket.column}`)
    for (const [slug, state] of Object.entries(ticket.progress)) {
      if (state === 'done' && was.progress[slug] !== 'done') $.ui.toast(`${slug} reviewed on ${ticket.name}`)
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

async function act($: EngineInterface, tool: string, args: Record<string, unknown>): Promise<void> {
  await callBoard($, tool, args)
  await refresh($)
}

const fillPrompt = ($: EngineInterface, text: string) => $.prompt.fill({ text, mode: 'replace' })

type View = {
  elements: ElementTable
  shown: BoardJson
  address: string | null
  now: number
  isWide: boolean
  hasSurfaceModules: boolean
  hasPictures: boolean
}

function actionButton({ elements: { Button } }: View, key: string, label: string, onPress: (() => unknown) | null, isMain = false) {
  // Button has no disabled state: an action the ticket does not allow is drawn dim and does nothing.
  return (
    <Button
      key={key}
      label={label}
      dimColor={!onPress}
      variant={isMain && onPress ? 'primary' : 'secondary'}
      onPress={onPress ?? (() => undefined)}
    />
  )
}

function headerView($: EngineInterface, view: View) {
  const { elements, shown } = view
  const { Box, Text } = elements
  const distinct = new Set(allTickets(shown).map(ticket => ticket.name)).size
  const Svg = view.hasPictures ? (elements as ElementTable<'desktop'>).Svg : null
  return (
    <Box key="header" flexDirection="row" gap={1} alignItems="center" paddingX={1} backgroundColor={BRAND.surface}>
      {Svg ? <Svg source={CHEVRON} alt="abd.works" width={CHEVRON_PIXELS} height={CHEVRON_PIXELS} /> : null}
      <Text bold color={BRAND.text}>
        BOARD<Text color={BRAND.accent}>_</Text>
      </Text>
      <Box key="header-meta" flexGrow={1}>
        <Text color={BRAND.muted}>
          {shown.project} · {distinct} tickets
        </Text>
      </Box>
      {actionButton(view, 'new-ticket', '+ Ticket', () => fillPrompt($, 'Open a new ticket with kanban.new, titled: '))}
      {actionButton(view, 'refresh', 'Refresh', () => refresh($))}
    </Box>
  )
}

function legendView({ elements: { Box, Text } }: View) {
  return (
    <Box key="legend" flexDirection="row" flexWrap="wrap" columnGap={2} paddingX={1}>
      {Object.values(STATES).map(state => (
        <Text color={BRAND.muted}>
          <Text color={state.color}>■</Text> {state.label}
        </Text>
      ))}
      <Text color={BRAND.muted}>bars: {PRACTICES.map(practice => practice.name).join(' · ')}</Text>
    </Box>
  )
}

const stateOf = (ticket: TicketJson, slug: string) =>
  STATES[ticket.progress[slug] ?? 'not_started'] ?? STATES.not_started

const cardSlugs = ({ shown }: View, ticket: TicketJson): string[] => {
  const stageName = ticket.column === 'Complete' ? FINAL_STAGE : ticket.column
  return shown.columns.find(column => column.name === stageName)?.work_required ?? []
}

function progressBar(view: View, ticket: TicketJson) {
  const { Text } = view.elements
  return (
    <Text>
      {cardSlugs(view, ticket).map(slug => (
        <Text color={stateOf(ticket, slug).color}>▬▬ </Text>
      ))}
    </Text>
  )
}

function cardTail(ticket: TicketJson): TicketCardJson['tail'] {
  if (ticket.is_done) return { text: 'ready to pull', color: BRAND.success }
  return ticket.next ? { text: `next: ${ticket.next}`, color: BRAND.accent } : null
}

function cardJson(view: View, ticket: TicketJson): TicketCardJson {
  const { shown, address, now } = view
  const place = ticketAddress(ticket)
  return {
    address: place,
    name: ticket.name,
    canMovePrevious: canMovePrevious(ticket),
    canMoveNext: canMoveNext(ticket),
    title: ticket.title,
    meta: [ticket.scope, ageOf(now, ticket.last_activity)].filter(Boolean).join(' · '),
    segments: cardSlugs(view, ticket).map(slug => ({
      scope: `skill-${place}-${slug}`.slice(0, MAXIMUM_HOVER_SCOPE),
      color: stateOf(ticket, slug).color,
      skill: skillOf(slug),
    })),
    tail: cardTail(ticket),
    borderColor: ticket.name === shown.active ? BRAND.accent : place === address ? BRAND.text : BRAND.border,
    hoverColor: BRAND.muted,
    backgroundColor: BRAND.raised,
    titleColor: BRAND.text,
    mutedColor: BRAND.muted,
  }
}

function ticketCard($: EngineInterface, view: View, ticket: TicketJson) {
  const { elements, shown, address, now, hasSurfaceModules } = view
  const { Box, Button, Text } = elements
  const place = ticketAddress(ticket)
  const Client = hasSurfaceModules ? (elements as ElementTable<'desktop'>).Client : null
  if (Client) return <Client key={`card-${place}`} module="./ticket-card.tsx" props={cardJson(view, ticket)} width="100%" />
  const borderColor = ticket.name === shown.active ? BRAND.accent : place === address ? BRAND.text : BRAND.border
  return (
    <Box
      key={`card-${place}`}
      flexDirection="column"
      borderStyle="single"
      borderColor={borderColor}
      hover={{ borderColor: BRAND.muted }}
      backgroundColor={BRAND.raised}
      paddingX={1}
    >
      <Button key={`ticket-${place}`} plain onPress={() => update($, selected, () => place)}>
        <Text bold color={BRAND.text}>
          {ticket.title}
        </Text>
      </Button>
      <Text color={BRAND.muted}>{[ticket.scope, ageOf(now, ticket.last_activity)].filter(Boolean).join(' · ')}</Text>
      {progressBar(view, ticket)}
      {ticket.is_done ? <Text color={BRAND.success}>ready to pull</Text> : null}
      {ticket.next ? <Text color={BRAND.accent}>next: {ticket.next}</Text> : null}
      <Box key={`moves-${place}`} flexDirection="row" justifyContent="space-between">
        {actionButton(view, `previous-${place}`, '←', canMovePrevious(ticket) ? () => act($, 'kanban.move_previous', { ticket: ticket.name }) : null)}
        {actionButton(view, `next-${place}`, '→', canMoveNext(ticket) ? () => act($, 'kanban.move_next', { ticket: ticket.name }) : null)}
      </Box>
    </Box>
  )
}

function backlogCard($: EngineInterface, { elements: { Box, Button, Text }, address, now }: View, item: BacklogItemJson) {
  const place = itemAddress(item)
  return (
    <Box
      key={`card-${place}`}
      flexDirection="column"
      borderStyle="single"
      borderColor={place === address ? BRAND.text : BRAND.border}
      hover={{ borderColor: BRAND.muted }}
      backgroundColor={BRAND.raised}
      paddingX={1}
    >
      <Button key={`item-${item.title}`} plain onPress={() => update($, selected, () => place)}>
        <Text bold color={BRAND.text}>
          {item.title}
        </Text>
      </Button>
      <Text color={BRAND.muted}>{ageOf(now, item.last_activity)}</Text>
    </Box>
  )
}

function stageBody($: EngineInterface, view: View, column: ColumnJson) {
  const { Box, Text } = view.elements
  const list = (label: string, tickets: TicketJson[]) => (
    <Box key={`${column.name}-${label}`} flexDirection="column" gap={1} width={view.isWide ? '50%' : '100%'}>
      <Text color={BRAND.muted}>{label}</Text>
      {tickets.map(ticket => ticketCard($, view, ticket))}
    </Box>
  )
  return (
    <Box key={`${column.name}-body`} flexDirection={view.isWide ? 'row' : 'column'} gap={1} padding={1}>
      {list('IN PROGRESS', column.in_progress ?? [])}
      {list('DONE', column.done ?? [])}
    </Box>
  )
}

function columnView($: EngineInterface, view: View, column: ColumnJson) {
  const { Box, Text } = view.elements
  const count = column.items ? column.items.length : ticketsOf(column).length
  return (
    <Box
      key={`column-${column.name}`}
      flexDirection="column"
      width={column.work_required ? STAGE_WIDTH : EDGE_COLUMN_WIDTH}
      borderStyle="single"
      borderColor={BRAND.border}
      backgroundColor={BRAND.surface}
    >
      <Box key={`${column.name}-heading`} flexDirection="row" justifyContent="space-between" paddingX={1}>
        <Text bold color={BRAND.text}>
          {column.name.toUpperCase()}
        </Text>
        <Text color={BRAND.muted}>{count}</Text>
      </Box>
      {column.work_required ? (
        stageBody($, view, column)
      ) : (
        <Box key={`${column.name}-body`} flexDirection="column" gap={1} padding={1}>
          {(column.items ?? []).map(item => backlogCard($, view, item))}
          {(column.tickets ?? []).map(ticket => ticketCard($, view, ticket))}
        </Box>
      )}
    </Box>
  )
}

function gridCell(view: View, ticket: TicketJson, column: ColumnJson, prefix: string) {
  const { Box, Text } = view.elements
  const slug = (column.work_required ?? []).find(required => required.startsWith(prefix))
  const state = slug ? (ticket.progress[slug] ?? 'not_started') : 'not_started'
  const { label, color } = STATES[state] ?? STATES.not_started
  const isRequired = column.name === ticket.column && !ticket.is_done && state !== 'done'
  return (
    <Box
      key={`cell-${column.name}-${prefix}`}
      flexDirection="column"
      width={STAGE_WIDTH}
      borderStyle="single"
      borderColor={isRequired ? BRAND.accent : BRAND.border}
      paddingX={1}
    >
      <Text color={BRAND.muted}>{slug ? fidelityName(slug, prefix) : '—'}</Text>
      {slug ? (
        <Text backgroundColor={color} color={BRAND.canvas}>
          {' '}
          {label}{' '}
        </Text>
      ) : null}
      {slug ? (
        <Box display="none" hover={{ display: 'flex' }}>
          <Text color={BRAND.text}>{skillOf(slug)}</Text>
        </Box>
      ) : null}
    </Box>
  )
}

function practiceGrid(view: View, ticket: TicketJson) {
  const { Box, Text } = view.elements
  const stages = view.shown.columns.filter(column => column.work_required)
  const rowHeading = (label: string) => (
    <Box key={`heading-${label}`} width={EDGE_COLUMN_WIDTH} paddingX={1}>
      <Text color={BRAND.muted}>{label}</Text>
    </Box>
  )
  return (
    <Box key="practices" flexDirection="column">
      <Box key="stage-names" flexDirection="row" columnGap={COLUMN_GAP}>
        {rowHeading('')}
        {stages.map(stage => (
          <Box key={`stage-${stage.name}`} width={STAGE_WIDTH} paddingX={1}>
            <Text color={BRAND.muted}>{stage.name}</Text>
          </Box>
        ))}
      </Box>
      {PRACTICES.map(practice => (
        <Box key={`practice-${practice.name}`} flexDirection="row" columnGap={COLUMN_GAP}>
          {rowHeading(practice.name)}
          {stages.map(stage => gridCell(view, ticket, stage, practice.prefix))}
        </Box>
      ))}
    </Box>
  )
}

function ticketActions($: EngineInterface, view: View, ticket: TicketJson) {
  const { elements, shown } = view
  const { Box } = elements
  const { name, next } = ticket
  const isClosed = ticket.column === 'Complete'
  const runNext = `Work on ${next} for ticket ${name}: run its next action (generate, validate, or /review).`
  const split = `Split ticket ${name} into child tickets, one per story on its story map: call kanban.new with parent ${name} for each story.`
  return (
    <Box key="actions" flexDirection="row" flexWrap="wrap" gap={1}>
      {actionButton(view, 'run-next', 'Run next', next ? () => fillPrompt($, runNext) : null)}
      {actionButton(view, 'split', 'Split', isClosed ? null : () => fillPrompt($, split))}
      {actionButton(view, 'switch-to', 'Switch to', name === shown.active || isClosed ? null : () => act($, 'session.switch', { name }))}
      {actionButton(view, 'handoff', 'Handoff', isClosed ? null : () => fillPrompt($, `Write a handoff for ticket ${name} with /space-handoff-handoff-session.`))}
      {actionButton(view, 'close', 'Close', isClosed ? null : () => act($, 'kanban.close', { ticket: name }))}
    </Box>
  )
}

function ticketDetail($: EngineInterface, view: View, ticket: TicketJson) {
  const { Box, Text } = view.elements
  return (
    <Box key="detail" flexDirection="column" gap={1} paddingX={1}>
      <Text bold color={BRAND.text}>
        {ticket.title} <Text color={BRAND.muted}>{placeOf(ticket)}</Text>
      </Text>
      {practiceGrid(view, ticket)}
      <Text color={BRAND.muted}>
        {ticket.handoff ? `Latest handoff: ${ticket.handoff}` : 'No handoff yet'}
        {ticket.next ? ` · Next: ${ticket.next}` : ''}
      </Text>
      {ticketActions($, view, ticket)}
    </Box>
  )
}

function backlogDetail($: EngineInterface, view: View, item: BacklogItemJson) {
  const { Box, Text } = view.elements
  return (
    <Box key="detail" flexDirection="column" gap={1} paddingX={1}>
      <Text bold color={BRAND.text}>
        {item.title} <Text color={BRAND.muted}>{item.path}</Text>
      </Text>
      <Box key="actions" flexDirection="row">
        {actionButton(view, 'start', 'Start', () => act($, 'kanban.start', { backlog_item: item.title }), true)}
      </Box>
    </Box>
  )
}

function detailView($: EngineInterface, view: View) {
  const { shown, address } = view
  const item = backlogItems(shown).find(entry => itemAddress(entry) === address)
  if (item) return backlogDetail($, view, item)
  const chosen =
    allTickets(shown).find(ticket => ticketAddress(ticket) === address) ?? activeTicket(shown) ?? latestTicket(shown)
  return chosen ? ticketDetail($, view, chosen) : null
}

function splitBar($: EngineInterface, view: View, layout: SplitLayoutJson, boardRows: number) {
  const { elements } = view
  const { Box, Button, Text } = elements
  const Client = view.hasSurfaceModules && !layout.expanded ? (elements as ElementTable<'desktop'>).Client : null
  const show = (expanded: SplitLayoutJson['expanded']) => () => update($, splitLayout, now => ({ ...now, expanded }))
  return (
    <Box key="split-bar" flexDirection="row" gap={1} alignItems="center" flexShrink={0} paddingX={1}>
      {Client ? (
        <Client
          key="split-grip"
          module="./split-grip.tsx"
          props={{ boardRows, color: BRAND.idle, hoverColor: BRAND.accent }}
          flexGrow={1}
          height={1}
        />
      ) : (
        <Box key="split-space" flexGrow={1}>
          <Text color={BRAND.idle}> </Text>
        </Box>
      )}
      {layout.expanded === 'board' ? null : <Button key="expand-board" label="Expand board" onPress={show('board')} />}
      {layout.expanded === 'details' ? null : <Button key="expand-details" label="Expand details" onPress={show('details')} />}
      {layout.expanded ? <Button key="show-both" label="Show both" onPress={show(null)} /> : null}
    </Box>
  )
}

function boardRegion($: EngineInterface, view: View) {
  const { Box } = view.elements
  return (
    <Box key="board-region" flexDirection="column" gap={1}>
      {headerView($, view)}
      {legendView(view)}
      <Box key="columns" flexDirection="row" columnGap={COLUMN_GAP} paddingX={1}>
        {view.shown.columns.map(column => columnView($, view, column))}
      </Box>
    </Box>
  )
}

function paneLayout($: EngineInterface, view: View, layout: SplitLayoutJson, bodyRows: number) {
  const { Box } = view.elements
  const largest = Math.max(bodyRows - MINIMUM_REGION_ROWS, MINIMUM_REGION_ROWS)
  const wanted = layout.boardRows ?? Math.round(bodyRows * BOARD_SHARE)
  const boardRows = Math.min(Math.max(wanted, MINIMUM_REGION_ROWS), largest)
  const bar = splitBar($, view, layout, boardRows)
  // Expanded, a region takes its full height and the pane's own scrolling reaches all of it.
  if (layout.expanded === 'board') {
    return (
      <Box flexDirection="column" backgroundColor={BRAND.canvas}>
        {bar}
        {boardRegion($, view)}
      </Box>
    )
  }
  if (layout.expanded === 'details') {
    return (
      <Box flexDirection="column" gap={1} backgroundColor={BRAND.canvas}>
        {bar}
        {detailView($, view)}
      </Box>
    )
  }
  return (
    <Box flexDirection="column" height={bodyRows} backgroundColor={BRAND.canvas}>
      <Box key="top" flexDirection="column" height={boardRows} flexShrink={0} overflow="hidden">
        {boardRegion($, view)}
      </Box>
      {bar}
      <Box key="bottom" flexDirection="column" flexGrow={1} overflow="hidden">
        {detailView($, view)}
      </Box>
    </Box>
  )
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'board', description: 'Show the CDD session board beside the chat' })
    await $.command.register({
      name: 'ticket',
      description: 'Move a ticket on the CDD session board',
      argumentHint: 'pull|close|switch <ticket>',
    })
    void $.ui.open({ id: PANE, title: 'Board' })
    await refresh($)
    return next(e)
  })

  on('command.run', { command: 'board' }, async $ => {
    await $.ui.open({ id: PANE, title: 'Board' })
    await refresh($)
    return { text: 'Board opened.' }
  })

  on('command.run', { command: 'ticket' }, async ($, e) => {
    const [verb = '', ticket] = e.args.trim().split(/\s+/)
    const action = TICKET_ACTIONS[verb]
    if (!action || !ticket) return { text: 'Usage: /ticket pull|close|switch <ticket>' }
    await act($, action.tool, { [action.argument]: ticket })
    return { text: `${verb} ${ticket}` }
  })

  // What a surface module posts is plain data from code, so only the shapes it sends are believed.
  on('ui.message', async ($, e, next) => {
    const { select, boardRows, move, ticket } = e.data as Record<string, unknown>
    if (typeof select === 'string') await update($, selected, () => select)
    if ((move === 'next' || move === 'previous') && typeof ticket === 'string') await act($, `kanban.move_${move}`, { ticket })
    if (typeof boardRows === 'number') await update($, splitLayout, now => ({ ...now, boardRows }))
    return next(e)
  })

  // A surface that cannot run a surface module still gets the board, with Buttons in place of them.
  on('ui.fault', async ($, e, next) => {
    await update($, surfaceModulesFailed, () => true)
    return next(e)
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
    const guidance = violations.map(guidanceSlug).join(' ')
    return (
      <Box flexDirection="row" gap={1} paddingX={1} backgroundColor={BRAND.raised}>
        <Text color={BRAND.warning}>
          {active.name} · {active.column} · violations: {violations.join(', ')}
        </Text>
        <Button key="show" label="Show" onPress={() => fillPrompt($, `Show the violations on ${guidance} for ticket ${active.name}.`)} />
        <Button key="satisfy" label="Satisfy" variant="primary" onPress={() => fillPrompt($, `/actions-satisfy ${guidance}`)} />
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const elements = $.ui.resolve(e)
    const { Text } = elements
    const shown = await read($, board)
    if (!shown) return <Text dimColor>No board yet: is the cdd MCP server connected?</Text>
    const view: View = {
      elements,
      shown,
      address: await read($, selected),
      now: await $.clock.now(),
      isWide: e.props.bodyColumns >= WIDE_PANE_COLUMNS,
      hasSurfaceModules: SURFACE_MODULE_SURFACES.includes(e.surface) && !(await read($, surfaceModulesFailed)),
      hasPictures: e.surface !== 'terminal',
    }
    return paneLayout($, view, await read($, splitLayout), e.props.scroll.bodyRows)
  })
}
