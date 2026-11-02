import type { ElementTable, EngineInterface } from 'claude-code'

import type { ColumnJson, SplitLayoutJson, TicketJson } from '../../types'
import { ActionButtonView, ExpandToggleView, PrimaryButtonView } from './action-button'
import { ActivationView } from './activation-view'
import { add, BacklogItemClient, cancelDraft, openDraft, start, typeDraftText, typeDraftTitle } from './backlog-item-client'
import { BOARD_SIDE_COLUMNS, boardColumnsOf, COLUMN_GAP, columnWidthOf, faceRowsOf, regionRowsOf } from './board-layout'
import { BRAND, CHEVRON, CHEVRON_PIXELS } from './brand'
import { cancelLimit, editLimit, refresh, select, setColumnOffset, setWipLimit, submitLimit, toggleRegion } from './board-client'
import { expandedPanel, SidePanelsView } from './side-panel-view'
import { StageHeadBoxView } from './stage-head'
import { openNewTicket, TicketClient } from './ticket-client'
import { CardExpansionView, DetailHeadView, OnlyActiveToggleView, TicketCardView, TicketDetailView } from './ticket-view'
import { ageOf, mainColumnsOf } from './view-context'
import type { ViewContext } from './view-context'

function HeaderView($: EngineInterface, view: ViewContext) {
  const { elements, board, layout } = view
  const { Box, Text } = elements
  const Svg = view.hasPictures ? (elements as ElementTable<'desktop'>).Svg : null
  return (
    <Box key="header" flexDirection="row" flexWrap="wrap" columnGap={2} alignItems="center" paddingX={2} paddingY={1} flexShrink={0} backgroundColor={BRAND.surface}>
      {Svg ? <Svg source={CHEVRON} alt="abd.works" width={CHEVRON_PIXELS} height={CHEVRON_PIXELS} /> : null}
      <Text mono weight="semibold" color={BRAND.text}>
        BOARD<Text color={BRAND.accent}>_</Text>
      </Text>
      <Box key="header-meta" flexGrow={1}>
        <Text mono size="footnote" color={BRAND.muted}>
          {board.project} · {board.ticketCount} tickets · active:{' '}
          <Text weight="semibold" color={BRAND.accentText}>
            {board.activeTicket?.title ?? 'none'}
          </Text>
        </Text>
      </Box>
      {OnlyActiveToggleView($, view)}
      {ActionButtonView(view, 'new-ticket', '+ Ticket', () => openNewTicket($))}
      {ActionButtonView(view, 'refresh', 'Refresh', () => refresh($))}
      {ExpandToggleView(view, 'expand-board', layout.expanded === 'board', () => toggleRegion($, 'board'))}
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
    <Box key="draft" flexDirection="column" flexShrink={0} rowGap={1} paddingX={1}>
      <Input key="draft-title" placeholder="Title" value={draft.title} onInput={value => typeDraftTitle($, value)} onSubmit={value => (value.trim() ? add($, { ...draft, title: value }) : undefined)} />
      <Input key="draft-text" placeholder="Text" rows={5} value={draft.text} onInput={value => typeDraftText($, value)} onSubmit={value => (draft.title.trim() ? add($, { ...draft, text: value }) : undefined)} />
      <Box key="draft-actions" flexDirection="row" justifyContent="space-between">
        {ActionButtonView(view, 'add-item', 'Add', addItem, true)}
        {ActionButtonView(view, 'cancel-item', 'Cancel', () => cancelDraft($))}
      </Box>
    </Box>
  )
}

function BacklogFaceView($: EngineInterface, view: ViewContext, column: ColumnJson, item: BacklogItemClient) {
  const { elements, hasSurfaceModules, now, board } = view
  const { Button, Text } = elements
  const Client = hasSurfaceModules ? (elements as ElementTable<'desktop'>).Client : null
  const age = ageOf(now, item.lastActivity)
  if (Client) {
    const card = { address: item.address, title: item.title, meta: age, titleColor: BRAND.text, hoverColor: BRAND.accentText, mutedColor: BRAND.muted }
    return <Client key={`face-${item.address}`} module="./ticket-card.tsx" props={card} width="100%" height={faceRowsOf(item.title, column, boardColumnsOf(mainColumnsOf(view)), board.columns.length)} />
  }
  return [
    <Button key={`item-${item.title}`} plain onPress={() => select($, item.address)}>
      <Text weight="semibold" color={BRAND.text}>
        {item.title}
      </Text>
    </Button>,
    <Text mono size="caption" color={BRAND.muted}>
      {age}
    </Text>,
  ]
}

function BacklogCardView($: EngineInterface, view: ViewContext, column: ColumnJson, item: BacklogItemClient) {
  const { Box } = view.elements
  const { address } = view
  return (
    <Box
      key={`card-${item.address}`}
      flexDirection="column"
      borderStyle="single"
      borderColor={item.address === address ? BRAND.text : BRAND.border}
      hover={{ borderColor: BRAND.muted, backgroundColor: BRAND.raised }}
      backgroundColor={BRAND.surface}
      paddingX={1}
    >
      {BacklogFaceView($, view, column, item)}
      <Box key={`item-moves-${item.title}`} flexDirection="row" justifyContent="flex-end">
        {ActionButtonView(view, `start-${item.title}`, '→', () => start($, item))}
      </Box>
    </Box>
  )
}

// A person types the limit where the surface has a field; mobile has no Input, so it steps instead.
function WipLimitControlView($: EngineInterface, view: ViewContext, column: ColumnJson, limit: number, color: string) {
  const { elements, editingLimit, hasInputs } = view
  const { Button, Text } = elements
  if (!hasInputs) {
    return [
      ActionButtonView(view, `wip-less-${column.name}`, '-', limit > 1 ? () => setWipLimit($, column.name, limit - 1) : null),
      ActionButtonView(view, `wip-more-${column.name}`, '+', () => setWipLimit($, column.name, limit + 1)),
    ]
  }
  if (editingLimit === column.name) {
    const { Input } = elements as ElementTable<'desktop'>
    return [
      <Input key={`wip-input-${column.name}`} autoFocus value={String(limit)} onSubmit={value => submitLimit($, column.name, value)} />,
      ActionButtonView(view, `wip-cancel-${column.name}`, '×', () => cancelLimit($)),
    ]
  }
  return (
    <Button key={`wip-limit-${column.name}`} plain onPress={() => editLimit($, column.name)}>
      <Text mono size="footnote" underline color={color}>
        {limit}
      </Text>
    </Button>
  )
}

function WipLimitView($: EngineInterface, view: ViewContext, column: ColumnJson, count: number) {
  const { Box, Text } = view.elements
  const limit = column.wip_limit ?? 0
  const color = column.is_over_limit ? BRAND.error : BRAND.muted
  return (
    <Box key={`${column.name}-wip`} flexDirection="row" columnGap={1} alignItems="center" flexShrink={0}>
      <Text mono size="footnote" color={color} weight={column.is_over_limit ? 'bold' : 'regular'}>
        {count} /
      </Text>
      {WipLimitControlView($, view, column, limit, color)}
    </Box>
  )
}

function ListLabelView({ elements: { Text } }: ViewContext, label: string) {
  return (
    <Text mono size="caption" color={BRAND.muted}>
      {label}
    </Text>
  )
}

function TicketListView($: EngineInterface, view: ViewContext, column: ColumnJson, label: string, tickets: TicketJson[]) {
  const { Box } = view.elements
  return (
    <Box key={`${column.name}-${label}`} flexDirection="column" gap={1} width="50%" minWidth={0} flexShrink={1}>
      {ListLabelView(view, label)}
      {tickets.map(ticket => TicketCardView($, view, new TicketClient(ticket)))}
    </Box>
  )
}

function StageBodyView($: EngineInterface, view: ViewContext, column: ColumnJson) {
  const { Box } = view.elements
  return (
    <Box key={`${column.name}-body`} flexDirection="row" gap={1} padding={1}>
      {TicketListView($, view, column, 'IN PROGRESS', column.in_progress ?? [])}
      {TicketListView($, view, column, 'DONE', column.done ?? [])}
    </Box>
  )
}

function EdgeBodyView($: EngineInterface, view: ViewContext, column: ColumnJson) {
  const { Box } = view.elements
  return (
    <Box key={`${column.name}-body`} flexDirection="column" gap={1} padding={1}>
      {(column.items ?? []).map(item => BacklogCardView($, view, column, new BacklogItemClient(item)))}
      {(column.tickets ?? []).map(ticket => TicketCardView($, view, new TicketClient(ticket)))}
    </Box>
  )
}

function EdgeHeadingView($: EngineInterface, view: ViewContext, column: ColumnJson) {
  const { Box, Button, Text } = view.elements
  return (
    <Box key={`${column.name}-heading`} flexDirection="row" justifyContent="space-between" alignItems="center" padding={1}>
      <Text mono size="footnote" weight="bold" color={BRAND.text}>
        {column.name.toUpperCase()}
      </Text>
      <Box key={`${column.name}-count`} flexDirection="row" columnGap={1} alignItems="center">
        <Text mono size="caption" color={BRAND.muted}>
          {view.board.countOf(column)}
        </Text>
        {column.items ? <Button key="add-to-backlog" plain dimColor label="+" onPress={() => openDraft($)} /> : null}
      </Box>
    </Box>
  )
}

function StageHeadingView($: EngineInterface, view: ViewContext, column: ColumnJson) {
  const { Box } = view.elements
  const wip = WipLimitView($, view, column, view.board.countOf(column))
  return (
    <Box key={`${column.name}-heading`} flexDirection="column" padding={1}>
      {StageHeadBoxView(view, column, `board/${column.name}`, column.is_over_limit ? BRAND.error : BRAND.border, wip)}
    </Box>
  )
}

function ColumnView($: EngineInterface, view: ViewContext, column: ColumnJson) {
  const { Box } = view.elements
  const width = columnWidthOf(column, boardColumnsOf(mainColumnsOf(view)), view.board.columns.length)
  return (
    <Box key={`column-${column.name}`} flexDirection="column" width={width} flexShrink={0} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.surface}>
      {column.work_required ? StageHeadingView($, view, column) : EdgeHeadingView($, view, column)}
      {column.items && view.draft.isOpen ? DraftView($, view) : null}
      {column.work_required ? StageBodyView($, view, column) : EdgeBodyView($, view, column)}
    </Box>
  )
}

const sideLimitOf = (view: ViewContext): number => boardColumnsOf(mainColumnsOf(view)) - mainColumnsOf(view)

const sideOffsetOf = (view: ViewContext): number => Math.min(view.columnOffset, sideLimitOf(view))

function ColumnsView($: EngineInterface, view: ViewContext) {
  const { Box } = view.elements
  return (
    <Box key="columns" flexDirection="row" columnGap={COLUMN_GAP} paddingX={BOARD_SIDE_COLUMNS} paddingY={1} flexShrink={0}>
      {view.board.columns.map(column => ColumnView($, view, column))}
    </Box>
  )
}

// The columns never squeeze to fit, so what the pane cannot show is reached sideways: by a bar where a Client can
// hear a drag, and by a column's width at a time elsewhere.
function SideScrollView($: EngineInterface, view: ViewContext) {
  const { elements, hasSurfaceModules, board } = view
  const { Box } = elements
  const limit = sideLimitOf(view)
  if (!limit) return null
  const offset = sideOffsetOf(view)
  if (hasSurfaceModules) {
    const { Client } = elements as ElementTable<'desktop'>
    const props = { offset, limit, shownShare: mainColumnsOf(view) / boardColumnsOf(mainColumnsOf(view)), trackColor: BRAND.surface, thumbColor: BRAND.idle, hoverColor: BRAND.muted }
    return <Client key="board-scrollbar" module="./board-scrollbar.tsx" props={props} width="100%" height={1} />
  }
  const step = columnWidthOf(board.columns[1]!, boardColumnsOf(mainColumnsOf(view)), board.columns.length)
  return (
    <Box key="columns-scroll" flexDirection="row" justifyContent="flex-end" columnGap={1} paddingX={2} flexShrink={0}>
      {ActionButtonView(view, 'columns-left', '◀', offset > 0 ? () => setColumnOffset($, offset - step) : null)}
      {ActionButtonView(view, 'columns-right', '▶', offset < limit ? () => setColumnOffset($, Math.min(offset + step, limit)) : null)}
    </Box>
  )
}

function WideRowsView(view: ViewContext, key: string, marginTop: number, rows: unknown) {
  const { Box } = view.elements
  return (
    <Box key={key} flexDirection="column" flexShrink={0} width={boardColumnsOf(mainColumnsOf(view))} marginLeft={-sideOffsetOf(view)} marginTop={-marginTop}>
      {rows}
    </Box>
  )
}

function BacklogDetailView($: EngineInterface, view: ViewContext, item: BacklogItemClient) {
  const { Box, Text } = view.elements
  const words = [
    <Text size="heading" weight="semibold" color={BRAND.text}>
      {item.title}{' '}
      <Text mono size="footnote" weight="regular" color={BRAND.muted}>
        {item.path}
      </Text>
    </Text>,
    item.text ? <Text color={BRAND.text}>{item.text}</Text> : null,
  ]
  return (
    <Box key="detail" flexDirection="column">
      {DetailHeadView($, view, words, ActionButtonView(view, 'start', 'Start', () => start($, item), true))}
    </Box>
  )
}

function DetailView($: EngineInterface, view: ViewContext) {
  const { board, address } = view
  const item = board.itemAt(address)
  if (item) return BacklogDetailView($, view, new BacklogItemClient(item))
  const chosen = board.ticketAt(address) ?? board.activeTicket ?? board.latestTicket
  return chosen ? TicketDetailView($, view, new TicketClient(chosen)) : DetailHeadView($, view, null, null)
}

function SplitGripView(view: ViewContext, layout: SplitLayoutJson, boardRows: number) {
  const { elements, bodyColumns } = view
  const { Box } = elements
  const Client = view.hasSurfaceModules ? (elements as ElementTable<'desktop'>).Client : null
  if (!Client) return null
  return (
    <Box key="split-bar" flexDirection="row" justifyContent="center" flexShrink={0} backgroundColor={BRAND.surface}>
      <Client key="split-grip" module="./split-grip.tsx" props={{ boardRows, color: BRAND.idle, hoverColor: BRAND.accent }} width={bodyColumns} height={1} />
    </Box>
  )
}

function SplitView($: EngineInterface, view: ViewContext) {
  const { Box } = view.elements
  const { bodyRows, layout, regionOffsets } = view
  const header = HeaderView($, view)
  const width = mainColumnsOf(view)
  // Expanded, a region takes its full height and the pane's own scrolling reaches all of it.
  if (layout.expanded === 'board') {
    return (
      <Box key="main" flexDirection="column" width={width} minHeight={bodyRows} overflow="hidden">
        {header}
        {WideRowsView(view, 'board-rows', 0, ColumnsView($, view))}
        {SideScrollView($, view)}
      </Box>
    )
  }
  if (layout.expanded === 'details') {
    return (
      <Box key="main" flexDirection="column" width={width} minHeight={bodyRows} overflow="hidden">
        {header}
        {WideRowsView(view, 'details-rows', 0, DetailView($, view))}
        {SideScrollView($, view)}
      </Box>
    )
  }
  const { boardRows } = regionRowsOf(bodyRows, layout)
  return (
    <Box key="main" flexDirection="column" width={width} height={bodyRows} overflow="hidden">
      {header}
      <Box key="top" flexDirection="column" height={boardRows} flexShrink={0} overflow="hidden">
        {WideRowsView(view, 'board-rows', regionOffsets.board, ColumnsView($, view))}
      </Box>
      {SideScrollView($, view)}
      {SplitGripView(view, layout, boardRows)}
      <Box key="bottom" flexDirection="column" flexGrow={1} overflow="hidden">
        {WideRowsView(view, 'details-rows', regionOffsets.details, DetailView($, view))}
      </Box>
    </Box>
  )
}

// Across the top of the pane, over the header's top edge, so the board it warns about stays where it is.
function ServerBandView({ elements: { Box, Text }, bodyColumns }: ViewContext, failure: string) {
  return (
    <Box key="server-band" position="absolute" top={0} left={0} width={bodyColumns} paddingX={1} backgroundColor={BRAND.errorWash}>
      <Text mono size="footnote" wrap="truncate-end" color={BRAND.error}>
        {`cdd server lost, so this board may be out of date. Reconnect it with /mcp, then press Refresh · ${failure}`}
      </Text>
    </Box>
  )
}

// A see-through color reaches only surfaces that draw a browser's colors; the terminal reads six digits.
function BackdropView({ elements: { Box }, hasPictures, bodyColumns, bodyRows }: ViewContext) {
  return hasPictures ? <Box key="backdrop" position="absolute" top={0} left={0} width={bodyColumns} height={bodyRows} backgroundColor={BRAND.backdrop} /> : null
}

export function PaneView($: EngineInterface, view: ViewContext) {
  const { Box } = view.elements
  const covers = expandedPanel(view)
  return (
    <Box key="pane" flexDirection="column" width={view.bodyColumns} minHeight={view.bodyRows} backgroundColor={BRAND.canvas}>
      <Box key="pane-row" flexDirection="row" flexGrow={1}>
        {covers ? null : SplitView($, view)}
        {SidePanelsView($, view)}
      </Box>
      {CardExpansionView($, view)}
      {view.activation ? BackdropView(view) : null}
      {view.activation ? ActivationView($, view, view.activation) : null}
      {view.serverFailure ? ServerBandView(view, view.serverFailure) : null}
    </Box>
  )
}

export function BandView($: EngineInterface, elements: ElementTable, hasPictures: boolean, ticket: TicketClient, onShow: () => unknown, onSatisfy: () => unknown) {
  const { Box, Button, Text } = elements
  return (
    <Box flexDirection="row" gap={1} paddingX={1} backgroundColor={BRAND.raised}>
      <Text color={BRAND.warning}>
        {ticket.name} · {ticket.column} · violations: {ticket.violations.join(', ')}
      </Text>
      <Button key="show" label="Show" onPress={onShow} />
      {hasPictures ? PrimaryButtonView(elements, 'satisfy', 'Satisfy', onSatisfy) : <Button key="satisfy" label="Satisfy" variant="primary" onPress={onSatisfy} />}
    </Box>
  )
}
