import type { ElementTable, EngineInterface } from 'claude-code'

import type { ColumnJson, SplitLayoutJson, TicketJson } from '../../types'
import { ActionButtonView } from './action-button'
import { ActivationView } from './activation-view'
import { add, BacklogItemClient, cancelDraft, openDraft, start, typeDraftText, typeDraftTitle } from './backlog-item-client'
import { BRAND, CHEVRON, CHEVRON_PIXELS } from './brand'
import { refresh, scrollColumns, select, setWipLimit, showRegion } from './board-client'
import { expandedPanel, SidePanelsView } from './side-panel-view'
import { openNewTicket, TicketClient } from './ticket-client'
import { CardExpansionView, COLUMN_GAP, EDGE_COLUMN_WIDTH, LegendView, OnlyActiveToggleView, STAGE_WIDTH, TicketCardView, TicketDetailView } from './ticket-view'
import { ageOf } from './view-context'
import type { ViewContext } from './view-context'

const BOARD_SHARE = 0.6
const MINIMUM_REGION_ROWS = 6
const EDGE_COLUMN_SHARE = 0.14
const STAGE_SHARE = 0.23
const SPLIT_BUTTONS_WIDTH = 44
const SMALLEST_GRIP_WIDTH = 10

function HeaderView($: EngineInterface, view: ViewContext) {
  const { elements, board } = view
  const { Box, Text } = elements
  const Svg = view.hasPictures ? (elements as ElementTable<'desktop'>).Svg : null
  return (
    <Box key="header" flexDirection="row" flexWrap="wrap" gap={1} alignItems="center" paddingX={1} backgroundColor={BRAND.surface}>
      {Svg ? <Svg source={CHEVRON} alt="abd.works" width={CHEVRON_PIXELS} height={CHEVRON_PIXELS} /> : null}
      <Text bold color={BRAND.text}>
        BOARD<Text color={BRAND.accent}>_</Text>
      </Text>
      <Box key="header-meta" flexGrow={1}>
        <Text color={BRAND.muted}>
          {board.project} · {board.ticketCount} tickets
        </Text>
      </Box>
      {OnlyActiveToggleView($, view)}
      {ActionButtonView(view, 'new-ticket', '+ Ticket', () => openNewTicket($))}
      {ActionButtonView(view, 'refresh', 'Refresh', () => refresh($))}
    </Box>
  )
}

function DraftView($: EngineInterface, view: ViewContext) {
  const { elements, draft, hasInputs } = view
  const { Box, Text } = elements
  if (!hasInputs) return <Text color={BRAND.muted}>Add a backlog item from a desktop or terminal surface</Text>
  const { Input } = elements as ElementTable<'desktop'>
  const addItem = draft.title.trim() ? () => add($, draft) : null
  return (
    <Box key="draft" flexDirection="column" flexShrink={0} paddingX={1}>
      <Input key="draft-title" label="Title" value={draft.title} onInput={value => typeDraftTitle($, value)} onSubmit={value => (value.trim() ? add($, { ...draft, title: value }) : undefined)} />
      <Input key="draft-text" label="Text" rows={3} value={draft.text} onInput={value => typeDraftText($, value)} onSubmit={value => (draft.title.trim() ? add($, { ...draft, text: value }) : undefined)} />
      <Box key="draft-actions" flexDirection="row" columnGap={1}>
        {ActionButtonView(view, 'add-item', 'Add', addItem, true)}
        {ActionButtonView(view, 'cancel-item', 'Cancel', () => cancelDraft($))}
      </Box>
    </Box>
  )
}

function BacklogCardView($: EngineInterface, view: ViewContext, item: BacklogItemClient) {
  const { Box, Button, Text } = view.elements
  const { address, now } = view
  return (
    <Box
      key={`card-${item.address}`}
      flexDirection="column"
      borderStyle="single"
      borderColor={item.address === address ? BRAND.text : BRAND.border}
      hover={{ borderColor: BRAND.muted }}
      backgroundColor={BRAND.raised}
      paddingX={1}
    >
      <Button key={`item-${item.title}`} plain onPress={() => select($, item.address)}>
        <Text bold color={BRAND.text}>
          {item.title}
        </Text>
      </Button>
      <Text color={BRAND.muted}>{ageOf(now, item.lastActivity)}</Text>
      <Box key={`item-moves-${item.title}`} flexDirection="row" justifyContent="flex-end">
        <Button key={`start-${item.title}`} plain label="→" onPress={() => start($, item)} />
      </Box>
    </Box>
  )
}

function WipLimitView($: EngineInterface, view: ViewContext, column: ColumnJson, count: number) {
  const { Box, Text } = view.elements
  const limit = column.wip_limit ?? 0
  return (
    <Box key={`${column.name}-wip`} flexDirection="row" columnGap={1}>
      <Text color={column.is_over_limit ? BRAND.error : BRAND.muted} bold={column.is_over_limit}>
        {count}/{limit}
      </Text>
      {ActionButtonView(view, `wip-less-${column.name}`, '-', limit > 1 ? () => setWipLimit($, column.name, limit - 1) : null)}
      {ActionButtonView(view, `wip-more-${column.name}`, '+', () => setWipLimit($, column.name, limit + 1))}
    </Box>
  )
}

function TicketListView($: EngineInterface, view: ViewContext, column: ColumnJson, label: string, tickets: TicketJson[]) {
  const { Box, Text } = view.elements
  return (
    <Box key={`${column.name}-${label}`} flexDirection="column" gap={1} width={view.isWide ? '50%' : '100%'}>
      <Text color={BRAND.muted}>{label}</Text>
      {tickets.map(ticket => TicketCardView($, view, new TicketClient(ticket)))}
    </Box>
  )
}

function StageBodyView($: EngineInterface, view: ViewContext, column: ColumnJson) {
  const { Box } = view.elements
  return (
    <Box key={`${column.name}-body`} flexDirection={view.isWide ? 'row' : 'column'} gap={1} padding={1}>
      {TicketListView($, view, column, 'IN PROGRESS', column.in_progress ?? [])}
      {TicketListView($, view, column, 'DONE', column.done ?? [])}
    </Box>
  )
}

function EdgeBodyView($: EngineInterface, view: ViewContext, column: ColumnJson) {
  const { Box } = view.elements
  return (
    <Box key={`${column.name}-body`} flexDirection="column" gap={1} padding={1}>
      {(column.items ?? []).map(item => BacklogCardView($, view, new BacklogItemClient(item)))}
      {(column.tickets ?? []).map(ticket => TicketCardView($, view, new TicketClient(ticket)))}
    </Box>
  )
}

function ColumnHeadingView($: EngineInterface, view: ViewContext, column: ColumnJson) {
  const { Box, Text } = view.elements
  const count = view.board.countOf(column)
  return (
    <Box key={`${column.name}-heading`} flexDirection="row" flexWrap="wrap" justifyContent="space-between" paddingX={1}>
      <Text bold color={BRAND.text}>
        {column.name.toUpperCase()}
      </Text>
      {column.work_required ? WipLimitView($, view, column, count) : <Text color={BRAND.muted}>{count}</Text>}
      {column.items ? ActionButtonView(view, 'add-to-backlog', '+', () => openDraft($)) : null}
    </Box>
  )
}

function ColumnView($: EngineInterface, view: ViewContext, column: ColumnJson, width: string | number) {
  const { Box } = view.elements
  return (
    <Box key={`column-${column.name}`} flexDirection="column" width={width} flexShrink={0} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.surface}>
      {ColumnHeadingView($, view, column)}
      {column.work_required ? StageBodyView($, view, column) : EdgeBodyView($, view, column)}
    </Box>
  )
}

const shareOf = (column: ColumnJson): number => (column.work_required ? STAGE_SHARE : EDGE_COLUMN_SHARE)

// Columns keep their width when a panel opens, so the ones that no longer fit are reached sideways.
function fittingColumns(view: ViewContext): { shown: ColumnJson[]; firstShown: number; canScrollRight: boolean } {
  const { board, bodyColumns, panels, columnOffset } = view
  const room = bodyColumns - panels.reduce((total, panel) => total + panel.width, 0)
  const firstShown = Math.min(columnOffset, board.columns.length - 1)
  const shown: ColumnJson[] = []
  let used = 0
  for (const column of board.columns.slice(firstShown)) {
    used += Math.round(bodyColumns * shareOf(column)) + COLUMN_GAP
    if (used > room && shown.length) break
    shown.push(column)
  }
  return { shown, firstShown, canScrollRight: firstShown + shown.length < board.columns.length }
}

function ColumnsView($: EngineInterface, view: ViewContext) {
  const { elements, board, panels, bodyColumns } = view
  const { Box } = elements
  if (!panels.length) {
    return (
      <Box key="columns" flexDirection="row" columnGap={COLUMN_GAP} paddingX={1}>
        {board.columns.map(column => ColumnView($, view, column, column.work_required ? STAGE_WIDTH : EDGE_COLUMN_WIDTH))}
      </Box>
    )
  }
  const { shown, firstShown, canScrollRight } = fittingColumns(view)
  return (
    <Box key="columns-area" flexDirection="column">
      <Box key="columns-scroll" flexDirection="row" justifyContent="flex-end" columnGap={1} paddingX={1}>
        {ActionButtonView(view, 'columns-left', '◀', firstShown > 0 ? () => scrollColumns($, -1) : null)}
        {ActionButtonView(view, 'columns-right', '▶', canScrollRight ? () => scrollColumns($, 1) : null)}
      </Box>
      <Box key="columns" flexDirection="row" columnGap={COLUMN_GAP} paddingX={1}>
        {shown.map(column => ColumnView($, view, column, Math.round(bodyColumns * shareOf(column))))}
      </Box>
    </Box>
  )
}

function BoardRegionView($: EngineInterface, view: ViewContext) {
  const { Box } = view.elements
  return (
    <Box key="board-region" flexDirection="column" gap={1}>
      {HeaderView($, view)}
      {LegendView(view)}
      {ColumnsView($, view)}
    </Box>
  )
}

function BacklogDetailView($: EngineInterface, view: ViewContext, item: BacklogItemClient) {
  const { Box, Text } = view.elements
  return (
    <Box key="detail" flexDirection="column" gap={1} paddingX={1}>
      <Text bold color={BRAND.text}>
        {item.title} <Text color={BRAND.muted}>{item.path}</Text>
      </Text>
      {item.text ? <Text color={BRAND.muted}>{item.text}</Text> : null}
      <Box key="actions" flexDirection="row">
        {ActionButtonView(view, 'start', 'Start', () => start($, item), true)}
      </Box>
    </Box>
  )
}

function DetailView($: EngineInterface, view: ViewContext) {
  const { board, address } = view
  // The form opens here, because the Backlog column is too narrow to type in.
  if (view.draft.isOpen) return DraftView($, view)
  const item = board.itemAt(address)
  if (item) return BacklogDetailView($, view, new BacklogItemClient(item))
  const chosen = board.ticketAt(address) ?? board.activeTicket ?? board.latestTicket
  return chosen ? TicketDetailView($, view, new TicketClient(chosen)) : null
}

function SplitBarView($: EngineInterface, view: ViewContext, layout: SplitLayoutJson, boardRows: number) {
  const { elements } = view
  const { Box, Button, Text } = elements
  const Client = view.hasSurfaceModules && !layout.expanded ? (elements as ElementTable<'desktop'>).Client : null
  return (
    <Box key="split-bar" flexDirection="row" gap={1} alignItems="center" flexShrink={0} paddingX={1}>
      {Client ? (
        <Client
          key="split-grip"
          module="./split-grip.tsx"
          props={{ boardRows, color: BRAND.idle, hoverColor: BRAND.accent }}
          width={Math.max(view.bodyColumns - SPLIT_BUTTONS_WIDTH, SMALLEST_GRIP_WIDTH)}
          height={1}
        />
      ) : (
        <Box key="split-space" flexGrow={1}>
          <Text color={BRAND.idle}> </Text>
        </Box>
      )}
      {layout.expanded === 'board' ? null : <Button key="expand-board" label="Expand board" onPress={() => showRegion($, 'board')} />}
      {layout.expanded === 'details' ? null : <Button key="expand-details" label="Expand details" onPress={() => showRegion($, 'details')} />}
      {layout.expanded ? <Button key="show-both" label="Show both" onPress={() => showRegion($, null)} /> : null}
    </Box>
  )
}

function SplitView($: EngineInterface, view: ViewContext, bodyRows: number) {
  const { Box } = view.elements
  const { layout } = view
  const largest = Math.max(bodyRows - MINIMUM_REGION_ROWS, MINIMUM_REGION_ROWS)
  const wanted = layout.boardRows ?? Math.round(bodyRows * BOARD_SHARE)
  const boardRows = Math.min(Math.max(wanted, MINIMUM_REGION_ROWS), largest)
  const bar = SplitBarView($, view, layout, boardRows)
  // Expanded, a region takes its full height and the pane's own scrolling reaches all of it.
  if (layout.expanded === 'board') {
    return (
      <Box key="main" flexDirection="column" flexGrow={1}>
        {bar}
        {BoardRegionView($, view)}
      </Box>
    )
  }
  if (layout.expanded === 'details') {
    return (
      <Box key="main" flexDirection="column" flexGrow={1} gap={1}>
        {bar}
        {DetailView($, view)}
      </Box>
    )
  }
  return (
    <Box key="main" flexDirection="column" flexGrow={1} height={bodyRows}>
      <Box key="top" flexDirection="column" height={boardRows} flexShrink={0} overflow="hidden">
        {BoardRegionView($, view)}
      </Box>
      {bar}
      <Box key="bottom" flexDirection="column" flexGrow={1} overflow="hidden">
        {DetailView($, view)}
      </Box>
    </Box>
  )
}

export function PaneView($: EngineInterface, view: ViewContext, bodyRows: number) {
  const { Box } = view.elements
  const covers = expandedPanel(view)
  return (
    <Box flexDirection="column" backgroundColor={BRAND.canvas}>
      {view.activation ? ActivationView($, view, view.activation) : null}
      <Box key="pane-row" flexDirection="row">
        {covers ? null : SplitView($, view, bodyRows)}
        {SidePanelsView($, view)}
      </Box>
      {CardExpansionView($, view)}
    </Box>
  )
}

export function BandView($: EngineInterface, elements: ElementTable, ticket: TicketClient, onShow: () => unknown, onSatisfy: () => unknown) {
  const { Box, Button, Text } = elements
  return (
    <Box flexDirection="row" gap={1} paddingX={1} backgroundColor={BRAND.raised}>
      <Text color={BRAND.warning}>
        {ticket.name} · {ticket.column} · violations: {ticket.violations.join(', ')}
      </Text>
      <Button key="show" label="Show" onPress={onShow} />
      <Button key="satisfy" label="Satisfy" variant="primary" onPress={onSatisfy} />
    </Box>
  )
}
