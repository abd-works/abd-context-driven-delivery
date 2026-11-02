import type { ElementTable, EngineInterface } from 'claude-code'

import type { ColumnJson, TicketCardJson } from '../../types'
import { ActionButtonView, ColorBarView, ExpandToggleView, LinkButtonView, SwitchView } from './action-button'
import { boardColumnsOf, CARD_FRAME_ROWS, columnLeftOf, COLUMN_GAP, faceRowsOf, rowsAboveCards } from './board-layout'
import { ACTION_STANDINGS, BRAND, DIM_TEXT_LIGHT, faded, OFF_LABEL_LIGHT, OFF_TILE_LIGHT, practiceOf, PRACTICES, SEGMENT_LIGHT } from './brand'
import { select, toggleHiddenPractices, toggleOnlyActive, toggleRegion } from './board-client'
import { openHelp, openReport, openViolations } from './side-panel-client'
import { StageHeadBoxView } from './stage-head'
import { CardBarView, FileLinksView, TileBarView } from './tile-bar'
import {
  archive,
  cardScrollLimit,
  enablePractice,
  expandedCardRows,
  fillHandoff,
  fillSplit,
  moveNext,
  movePrevious,
  openActivation,
  runNext,
  TicketClient,
  toggleCard,
  toggleTile,
} from './ticket-client'
import { guidanceSlug } from './ticket-summary'
import { ageOf, isLocked, mainColumnsOf } from './view-context'
import type { ViewContext } from './view-context'

// The board's stages and the details' stages share these, so Discovery sits over Discovery all the way down. They come
// to 100%, and columns shrink by their share to make room for the gaps, as the canvas's fractions do.
export const EDGE_COLUMN_WIDTH = '14%'
export const STAGE_WIDTH = '24%'
const MAXIMUM_HOVER_SCOPE = 64
const FACE_LINES = 2
// The canvas's segment: 14px by 7px, with 3px under it.
const SEGMENT_WIDTH = 14
const SEGMENT_HEIGHT = 7
const SEGMENT_PITCH = 10
const SEGMENT_CORNER = 1
const CARD_MARK_ROOM = 3
const EXPANDED_CARD_SHARE = 0.48
const SMALLEST_EXPANDED_CARD = 48
const STAGE_MARK_COLUMNS = 3
const ACTION_ORDER = ['generate', 'validate', 'review'] as const

const fidelityName = (slug: string, prefix: string): string => slug.slice(prefix.length)

// The practice's skill for a fidelity: `clean_engineering-code` is /practices-clean-engineering-clean-engineering-code.
const skillOf = (slug: string): string => `/practices-${guidanceSlug(practiceOf(slug)?.prefix ?? '')}${guidanceSlug(slug)}`

type CardSegment = { color: string; skill: string; scope: string }

function cardSegments(view: ViewContext, ticket: TicketClient): CardSegment[] {
  const stage = view.board.stageOf(view.board.ticketNamed(ticket.name)!)
  if (!stage) return []
  return ticket.enabledSlugs(stage).map(slug => {
    const state = ticket.stateOf(slug)
    return {
      color: faded(state.key === 'violations' ? state.color : practiceOf(slug)?.color ?? BRAND.idle, SEGMENT_LIGHT[state.key] ?? 1),
      skill: skillOf(slug),
      // The ending keeps the part that tells a card's segments apart.
      scope: `skill-${ticket.address}-${slug}`.slice(-MAXIMUM_HOVER_SCOPE),
    }
  })
}

const borderOf = ({ board, address }: ViewContext, ticket: TicketClient): string =>
  ticket.name === board.active ? BRAND.accent : ticket.address === address ? BRAND.text : BRAND.border

function cardJson(view: ViewContext, ticket: TicketClient): TicketCardJson {
  return {
    address: ticket.address,
    title: ticket.title,
    meta: ageOf(view.now, ticket.lastActivity),
    titleColor: BRAND.text,
    hoverColor: BRAND.accentText,
    mutedColor: BRAND.muted,
  }
}

const segmentPicture = (color: string): string =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${SEGMENT_WIDTH} ${SEGMENT_PITCH}"><rect width="${SEGMENT_WIDTH}" height="${SEGMENT_HEIGHT}" rx="${SEGMENT_CORNER}" fill="${color}"/></svg>`

// Floats at the card's right under its mark, as on the canvas, so the card is as tall as its words and controls.
function SegmentsView(view: ViewContext, segments: CardSegment[]) {
  const { elements, hasPictures } = view
  const { Box, Text } = elements
  const Svg = hasPictures ? (elements as ElementTable<'desktop'>).Svg : null
  return (
    <Box key="segments" position="absolute" top={1} right={1} flexDirection="column">
      {segments.map(segment => (
        <Box key={segment.scope} hover={{ scope: segment.scope }}>
          {Svg ? <Svg source={segmentPicture(segment.color)} alt={segment.skill} width={SEGMENT_WIDTH} height={SEGMENT_PITCH} /> : <Text color={segment.color}>▬</Text>}
        </Box>
      ))}
    </Box>
  )
}

// The skill of the segment under the pointer, in the card's flow as on the canvas. The segments float, so they stay put.
function SegmentSkillsView({ elements: { Box, Text } }: ViewContext, segments: CardSegment[]) {
  return segments.map(segment => (
    <Box key={`shown-${segment.scope}`} display="none" hover={{ scope: segment.scope, display: 'flex' }}>
      <Text mono size="caption" color={BRAND.text}>
        {segment.skill}
      </Text>
    </Box>
  ))
}

const ticketFaceRows = (view: ViewContext, stage: ColumnJson, ticket: TicketClient): number =>
  faceRowsOf(ticket.title, stage, boardColumnsOf(mainColumnsOf(view)), view.board.columns.length)

function ButtonFaceView($: EngineInterface, view: ViewContext, ticket: TicketClient) {
  const { Button, Text } = view.elements
  const card = cardJson(view, ticket)
  return [
    <Button key={`ticket-${ticket.address}`} plain onPress={() => select($, ticket.address)}>
      <Text weight="semibold" color={BRAND.text}>
        {ticket.title}
      </Text>
    </Button>,
    <Text mono size="caption" color={BRAND.muted}>
      {card.meta}
    </Text>,
  ]
}

// The canvas's small outlined button. A Button's own look is the surface's, so a plain one sits in a bordered Box;
// a terminal's border takes whole rows, so there the surface's button stays.
function CardButtonView(view: ViewContext, key: string, label: string, onPress: (() => unknown) | null) {
  const { Box, Button } = view.elements
  if (!view.hasPictures) return ActionButtonView(view, key, label, onPress)
  return (
    <Box key={`box-${key}`} borderStyle="single" borderColor={BRAND.border} hover={{ backgroundColor: BRAND.raised }} paddingX={1} flexShrink={0}>
      <Button key={key} plain label={label} dimColor={!onPress} onPress={onPress ?? (() => undefined)} />
    </Box>
  )
}

function CardControlsView($: EngineInterface, view: ViewContext, ticket: TicketClient, prefix: string) {
  const { Box } = view.elements
  const place = ticket.address
  const isActive = ticket.name === view.board.active
  const locked = isLocked(view, ticket.name)
  return (
    <Box key={`${prefix}moves-${place}`} flexDirection="row" flexWrap="wrap" justifyContent="space-between" flexShrink={0} columnGap={1}>
      {CardButtonView(view, `${prefix}previous-${place}`, '←', locked ? null : () => movePrevious($, ticket.name))}
      {CardButtonView(view, `${prefix}activate-${place}`, isActive ? 'Close' : 'Activate', ticket.isClosed ? null : () => openActivation($, ticket, isActive))}
      {CardButtonView(view, `${prefix}next-${place}`, '→', ticket.canMoveNext && !locked ? () => moveNext($, ticket.name) : null)}
    </Box>
  )
}

function CardFilesView($: EngineInterface, view: ViewContext, ticket: TicketClient, stage: ColumnJson | undefined, prefix: string) {
  const { Box } = view.elements
  return (
    <Box key={`${prefix}card-files-${ticket.address}`} flexDirection="row" flexWrap="wrap" columnGap={1} flexShrink={0}>
      {FileLinksView($, view, ticket, stage ? ticket.enabledSlugs(stage) : [], `${prefix}card-${ticket.address}`)}
    </Box>
  )
}

function CardMarkView($: EngineInterface, view: ViewContext, ticket: TicketClient, stage: ColumnJson, prefix: string) {
  const { Box, Button } = view.elements
  const place = ticket.address
  return (
    <Box key={`${prefix}mark-${place}`} position="absolute" top={0} right={1}>
      <Button key={`${prefix}expand-${place}`} plain label={view.openCard === ticket.name ? '▴' : '▾'} onPress={() => toggleCard($, ticket.name, stage.name, place, ticket.enabledSlugs(stage))} />
    </Box>
  )
}

export function TicketCardView($: EngineInterface, view: ViewContext, ticket: TicketClient) {
  const { elements, hasSurfaceModules, board } = view
  const { Box } = elements
  const Client = hasSurfaceModules ? (elements as ElementTable<'desktop'>).Client : null
  const stage = board.stageOf(board.ticketNamed(ticket.name)!)
  const segments = cardSegments(view, ticket)
  const place = ticket.address
  return (
    <Box
      key={`card-${place}`}
      flexDirection="column"
      flexShrink={0}
      minWidth={0}
      overflow="hidden"
      borderStyle={ticket.name === board.active ? 'bold' : 'single'}
      borderColor={borderOf(view, ticket)}
      hover={{ borderColor: BRAND.muted, backgroundColor: BRAND.raised }}
      backgroundColor={BRAND.surface}
      paddingLeft={1}
      paddingRight={CARD_MARK_ROOM}
    >
      {Client ? <Client key={`face-${place}`} module="./ticket-card.tsx" props={cardJson(view, ticket)} width="100%" height={stage ? ticketFaceRows(view, stage, ticket) : FACE_LINES} /> : ButtonFaceView($, view, ticket)}
      {SegmentSkillsView(view, segments)}
      {ticket.violations[0] ? LinkButtonView(view, `violations-${place}`, 'violations', BRAND.error, () => openViolations($, ticket.name)) : null}
      {CardFilesView($, view, ticket, stage, '')}
      {CardControlsView($, view, ticket, '')}
      {stage ? CardMarkView($, view, ticket, stage, '') : null}
      {SegmentsView(view, segments)}
    </Box>
  )
}

function TileNameView($: EngineInterface, view: ViewContext, ticket: TicketClient, stage: ColumnJson, slug: string, place: string, color: string) {
  const { elements, hasSurfaceModules, tile } = view
  const { Button, Text } = elements
  const prefix = practiceOf(slug)?.prefix ?? ''
  const label = fidelityName(slug, prefix).replaceAll('_', '-')
  const Client = hasSurfaceModules ? (elements as ElementTable<'desktop'>).Client : null
  const isOnCard = place.startsWith('card/')
  const menuSlugs = isOnCard ? ticket.enabledSlugs(stage) : []
  const hover = { place, ticket: ticket.name, stage: stage.name, slugs: [slug], label, color, opensOnHover: !isOnCard, menuSlugs }
  if (!ticket.isEnabled(practiceOf(slug)?.key ?? '')) {
    return (
      <Text key={`tile-off-${place}`} size="footnote" weight="semibold" wrap="truncate-end" color={color}>
        {label}
      </Text>
    )
  }
  return Client ? (
    <Client key={`tile-${place}`} module="./tile-hover.tsx" props={hover} flexGrow={1} height={1} />
  ) : (
    <Button key={`toggle-${place}`} plain label={`${label} ${tile?.place === place ? '▴' : '▾'}`} dimColor={color !== BRAND.text} onPress={() => toggleTile($, ticket.name, stage.name, place, [slug], menuSlugs)} />
  )
}

// Generate, Validate, and Review on one fidelity, each to do, in progress, or done.
function ActionMarksView({ elements: { Box, Text } }: ViewContext, ticket: TicketClient, slug: string, place: string, ink: (color: string) => string) {
  const actions = ticket.actionsOf(slug)
  return (
    <Box key={`marks-${place}`} flexDirection="row" columnGap={1} flexShrink={0}>
      {ACTION_ORDER.map(action => {
        const standing = ACTION_STANDINGS[actions[action]] ?? ACTION_STANDINGS.to_do!
        return (
          <Text key={action} mono size="caption" color={ink(standing.color)}>
            {standing.mark}
          </Text>
        )
      })}
    </Box>
  )
}

// `place` says where this tile is drawn, because the details and an opened card can show the same fidelity at once.
function TileView($: EngineInterface, view: ViewContext, ticket: TicketClient, stage: ColumnJson, slug: string, place: string, hasChip: boolean) {
  const { Box, Button, Text } = view.elements
  const practice = practiceOf(slug)
  const state = ticket.stateOf(slug)
  const isNext = stage.name === ticket.column && ticket.next === slug
  const isDim = state.key === 'not_started' && !isNext
  const isOn = ticket.isEnabled(practice?.key ?? '')
  // A Box has no opacity, so a practice turned off fades each colour on the tile.
  const ink = (color: string): string => (isOn ? color : faded(color, OFF_TILE_LIGHT))
  const nameColor = isDim && isOn ? faded(BRAND.text, DIM_TEXT_LIGHT) : ink(BRAND.text)
  return (
    <Box key={`tile-box-${place}`} flexDirection="row" flexShrink={0} borderStyle="single" borderColor={state.key === 'violations' ? ink(BRAND.error) : isNext ? BRAND.accent : BRAND.border} backgroundColor={BRAND.raised}>
      {ColorBarView(view, ink(practice?.color ?? BRAND.idle))}
      <Box key={`tile-line-${place}`} flexDirection="column" flexGrow={1} paddingX={1}>
        <Box key={`tile-heading-${place}`} flexDirection="row" columnGap={1} alignItems="center" flexShrink={0}>
          {hasChip ? (
            <Text mono size="caption" weight="semibold" color={ink(BRAND.text)}>
              {practice?.name}
            </Text>
          ) : null}
          <Box key={`tile-name-${place}`} flexGrow={1}>
            {TileNameView($, view, ticket, stage, slug, place, nameColor)}
          </Box>
          {ActionMarksView(view, ticket, slug, place, ink)}
          {state.key === 'violations' ? LinkButtonView(view, `violations-${place}`, 'violations', ink(BRAND.error), () => openReport($, ticket.name, slug)) : null}
          <Button key={`help-${place}`} plain label="?" dimColor onPress={() => openHelp($, practice?.key ?? '', fidelityName(slug, practice?.prefix ?? ''))}>
            <Text color={ink(BRAND.muted)}>?</Text>
          </Button>
        </Box>
        <Box display="none" hover={{ display: 'flex' }}>
          <Text mono size="caption" color={ink(BRAND.text)}>
            {skillOf(slug)}
          </Text>
        </Box>
      </Box>
    </Box>
  )
}

function ExpandedCardHeadView(view: ViewContext, ticket: TicketClient) {
  const { Box, Text } = view.elements
  return (
    <Box key="card-tiles-words" flexDirection="column" paddingRight={CARD_MARK_ROOM} flexShrink={0}>
      <Text weight="semibold" color={BRAND.text}>
        {ticket.title}
      </Text>
      <Text mono size="caption" color={BRAND.muted}>
        {ageOf(view.now, ticket.lastActivity)}
      </Text>
    </Box>
  )
}

// Starts over the ticket's own column, wherever the board has scrolled to, and stays within the pane.
function expandedCardLeft(view: ViewContext, stage: ColumnJson, width: number): number {
  const { board, bodyColumns, columnOffset } = view
  const wanted = columnLeftOf(board.columns, stage, boardColumnsOf(mainColumnsOf(view))) - columnOffset
  return Math.max(Math.min(wanted, bodyColumns - width - 1), 1)
}

function ticketsAbove(stage: ColumnJson, ticket: TicketClient): TicketClient[] {
  const lists = [stage.in_progress ?? [], stage.done ?? [], stage.tickets ?? []]
  const list = lists.find(tickets => tickets.some(shown => shown.name === ticket.name)) ?? []
  return list.slice(0, list.findIndex(shown => shown.name === ticket.name)).map(shown => new TicketClient(shown))
}

// Level with the card it came from, as near as the rows above it can be counted, and high enough to fit in the pane.
// A card taller than the pane starts at its top and the wheel moves it, because the card floats and the engine's
// window does not reach what floats past the pane's end.
function expandedCardTop(view: ViewContext, stage: ColumnJson, ticket: TicketClient): number {
  const above = ticketsAbove(stage, ticket).reduce((rows, shown) => rows + ticketFaceRows(view, stage, shown) + CARD_FRAME_ROWS, 0)
  const wanted = rowsAboveCards() + above - view.regionOffsets.board
  const cardRows = expandedCardRows(ticket, stage, view.tile)
  const shifted = Math.min(view.cardOffset, cardScrollLimit(cardRows, view.bodyRows))
  return Math.max(Math.min(wanted, view.bodyRows - cardRows - 1), 1) - shifted
}

// An opened card sits over the board and shows the same tiles as the details, so a ticket can be worked from either
// place. It is drawn last from the pane's root, because a Box paints over only what was drawn before it.
export function CardExpansionView($: EngineInterface, view: ViewContext) {
  const { elements, board, openCard, bodyColumns, tile } = view
  const { Box } = elements
  const json = openCard ? board.ticketNamed(openCard) : undefined
  const stage = json ? board.stageOf(json) : undefined
  if (!json || !stage) return null
  const ticket = new TicketClient(json)
  const width = Math.min(Math.max(Math.round(bodyColumns * EXPANDED_CARD_SHARE), SMALLEST_EXPANDED_CARD), Math.max(bodyColumns - 2, 1))
  const open = tile?.place.startsWith(`card/${ticket.address}/`) ? tile : null
  const isWhole = open?.place.endsWith('/menu') ?? false
  const slugs = ticket.enabledSlugs(stage)
  const segments = cardSegments(view, ticket)
  return (
    <Box
      key="card-tiles"
      position="absolute"
      top={expandedCardTop(view, stage, ticket)}
      left={expandedCardLeft(view, stage, width)}
      width={width}
      flexDirection="column"
      rowGap={1}
      borderStyle="bold"
      borderColor={borderOf(view, ticket)}
      backgroundColor={BRAND.surface}
      paddingX={1}
    >
      {ExpandedCardHeadView(view, ticket)}
      {SegmentSkillsView(view, segments)}
      {CardFilesView($, view, ticket, stage, 'open-')}
      {open && isWhole && slugs.length > 1 ? CardBarView($, view, ticket, stage, open) : null}
      {slugs.map(slug => {
        const place = `card/${ticket.address}/${slug}`
        return (
          <Box key={`card-tile-${slug}`} flexDirection="column" flexShrink={0}>
            {TileView($, view, ticket, stage, slug, place, true)}
            {open && (open.place === place || (isWhole && slugs.length === 1)) ? CardBarView($, view, ticket, stage, open) : null}
          </Box>
        )
      })}
      {CardControlsView($, view, ticket, 'open-')}
      {CardMarkView($, view, ticket, stage, 'open-')}
      {SegmentsView(view, segments)}
    </Box>
  )
}

function GridCellView($: EngineInterface, view: ViewContext, ticket: TicketClient, stage: ColumnJson, practice: (typeof PRACTICES)[number]) {
  const { Box } = view.elements
  const slug = (stage.work_required ?? []).find(required => required.startsWith(practice.prefix))
  return (
    <Box key={`cell-${stage.name}-${practice.prefix}`} flexDirection="column" width={STAGE_WIDTH}>
      {slug ? TileView($, view, ticket, stage, slug, `${ticket.address}/${slug}`, false) : null}
    </Box>
  )
}

function StageHeadView($: EngineInterface, view: ViewContext, ticket: TicketClient, stage: ColumnJson) {
  const { elements, hasSurfaceModules } = view
  const { Box, Button } = elements
  const Client = hasSurfaceModules ? (elements as ElementTable<'desktop'>).Client : null
  const place = `${ticket.address}/${stage.name}`
  const slugs = ticket.enabledSlugs(stage)
  const mark = view.tile?.place === place ? '▴' : '▾'
  const hover = { place, ticket: ticket.name, stage: stage.name, slugs, label: mark, color: BRAND.text, opensOnHover: true, menuSlugs: [] }
  const toggle = Client ? (
    <Client key={`stage-menu-${stage.name}`} module="./tile-hover.tsx" props={hover} width={STAGE_MARK_COLUMNS} height={1} />
  ) : (
    <Button key={`stage-menu-${stage.name}`} plain label={mark} onPress={() => toggleTile($, ticket.name, stage.name, place, slugs)} />
  )
  return (
    <Box key={`stage-${stage.name}`} flexDirection="column" width={STAGE_WIDTH}>
      {StageHeadBoxView(view, stage, place, BRAND.border, toggle)}
    </Box>
  )
}

function PracticeHeadingView($: EngineInterface, view: ViewContext, ticket: TicketClient, practice: (typeof PRACTICES)[number]) {
  const { Box, Button, Text } = view.elements
  const isOn = ticket.isEnabled(practice.key)
  const onToggle = isLocked(view, ticket.name) ? null : () => enablePractice($, ticket, practice.key, !isOn)
  return (
    <Box key={`heading-${practice.name}`} flexDirection="row" width={EDGE_COLUMN_WIDTH} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {ColorBarView(view, practice.color)}
      <Box key={`heading-line-${practice.name}`} flexDirection="row" justifyContent="space-between" alignItems="center" flexGrow={1} paddingX={1}>
        <Button key={`practice-help-${practice.key}`} plain onPress={() => openHelp($, practice.key, '')}>
          <Text mono size="caption" weight="semibold" color={isOn ? BRAND.text : faded(BRAND.text, OFF_LABEL_LIGHT)}>
            {practice.name}
          </Text>
        </Button>
        {SwitchView(view, `practice-${practice.key}`, isOn, onToggle)}
      </Box>
    </Box>
  )
}

function GridCornerView($: EngineInterface, view: ViewContext) {
  const { Box, Button, Text } = view.elements
  return (
    <Box key="heading-corner" flexDirection="row" width={EDGE_COLUMN_WIDTH} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {ColorBarView(view, BRAND.accent)}
      <Box key="corner-line" flexDirection="row" justifyContent="space-between" alignItems="center" flexGrow={1} paddingX={1}>
        <Text mono size="caption" weight="semibold" color={BRAND.accentText}>
          context-driven-delivery
        </Text>
        <Button key="toggle-hidden" plain dimColor label={view.hidesDisabled ? '▸' : '▾'} onPress={() => toggleHiddenPractices($)} />
      </Box>
    </Box>
  )
}

// Under the stage heads, in the stage's own column. A bar inside a low cell would be clipped: the details region has no
// scrolling of its own while the board shares the pane.
function GridBarView($: EngineInterface, view: ViewContext, ticket: TicketClient) {
  const { elements, tile, board } = view
  const { Box } = elements
  if (tile?.ticket !== ticket.name || tile.place.startsWith('card/')) return null
  return (
    <Box key="grid-bar" flexDirection="row" columnGap={COLUMN_GAP} flexShrink={0}>
      <Box key="grid-bar-corner" width={EDGE_COLUMN_WIDTH} />
      {board.stages.map(stage => (
        <Box key={`grid-bar-${stage.name}`} flexDirection="column" width={STAGE_WIDTH}>
          {stage.name === tile.stage ? TileBarView($, view, ticket, stage, tile) : null}
        </Box>
      ))}
      <Box key="grid-bar-end" width={EDGE_COLUMN_WIDTH} />
    </Box>
  )
}

function PracticeGridView($: EngineInterface, view: ViewContext, ticket: TicketClient) {
  const { Box } = view.elements
  const { stages } = view.board
  const shown = PRACTICES.filter(practice => ticket.isEnabled(practice.key) || !view.hidesDisabled)
  return (
    <Box key="practices" flexDirection="column" flexShrink={0} rowGap={1} padding={1}>
      <Box key="stage-names" flexDirection="row" columnGap={COLUMN_GAP} flexShrink={0}>
        {GridCornerView($, view)}
        {stages.map(stage => StageHeadView($, view, ticket, stage))}
        <Box key="heading-end" width={EDGE_COLUMN_WIDTH} />
      </Box>
      {GridBarView($, view, ticket)}
      {shown.map(practice => (
        <Box key={`practice-${practice.name}`} flexDirection="row" columnGap={COLUMN_GAP} flexShrink={0}>
          {PracticeHeadingView($, view, ticket, practice)}
          {stages.map(stage => GridCellView($, view, ticket, stage, practice))}
          <Box key={`practice-end-${practice.name}`} width={EDGE_COLUMN_WIDTH} />
        </Box>
      ))}
    </Box>
  )
}

function TicketActionsView($: EngineInterface, view: ViewContext, ticket: TicketClient) {
  const { Box } = view.elements
  const { active } = view.board
  const isOff = ticket.isClosed || isLocked(view, ticket.name)
  const isHeld = ticket.nextAction === 'satisfy'
  const pressRunNext = isHeld ? () => openReport($, ticket.name, ticket.next ?? '') : () => runNext($, ticket)
  return (
    <Box key="actions" flexDirection="row" flexWrap="wrap" gap={1} flexShrink={0} alignItems="center">
      {ActionButtonView(view, 'run-next', ticket.runNextLabel, ticket.next && !isLocked(view, ticket.name) ? pressRunNext : null)}
      {ActionButtonView(view, 'split', 'Split', isOff ? null : () => fillSplit($, ticket))}
      {ActionButtonView(view, 'switch-to', 'Switch to', ticket.name === active || ticket.isClosed ? null : () => openActivation($, ticket, false))}
      {ActionButtonView(view, 'handoff', 'Handoff', isOff ? null : () => fillHandoff($, ticket))}
      {ActionButtonView(view, 'close', 'Close session', ticket.name === active && !ticket.isClosed ? () => openActivation($, ticket, true) : null)}
      {ActionButtonView(view, 'archive', 'Archive', isLocked(view, ticket.name) && !ticket.isClosed ? null : () => archive($, ticket))}
    </Box>
  )
}

// The fixed bar over the details, shared by a ticket and a backlog item.
export function DetailHeadView($: EngineInterface, view: ViewContext, words: unknown, actions: unknown) {
  const { Box } = view.elements
  return (
    <Box key="detail-head" flexDirection="row" flexWrap="wrap" alignItems="center" columnGap={2} paddingX={2} paddingY={1} flexShrink={0} backgroundColor={BRAND.surface}>
      <Box key="detail-words" flexDirection="column" flexGrow={1} flexShrink={1}>
        {words}
      </Box>
      {actions}
      {ExpandToggleView(view, 'expand-details', view.layout.expanded === 'details', () => toggleRegion($, 'details'))}
    </Box>
  )
}

export function TicketDetailView($: EngineInterface, view: ViewContext, ticket: TicketClient) {
  const { Box, Text } = view.elements
  const locked = isLocked(view, ticket.name)
  const words = [
    <Text size="heading" weight="semibold" color={BRAND.text}>
      {ticket.title}{' '}
      <Text mono size="footnote" weight="regular" color={BRAND.muted}>
        {ticket.place}
      </Text>
    </Text>,
    <Text mono size="footnote" color={BRAND.muted}>
      {ticket.handoff ? `Latest handoff: ${ticket.handoff}` : 'No handoff yet'}
      {ticket.next ? ` · Next: ${ticket.next}, ${ticket.nextStepName}` : ''}
      {locked ? ' · Activate this session to run actions' : ''}
    </Text>,
  ]
  return (
    <Box key="detail" flexDirection="column" flexShrink={0}>
      {DetailHeadView($, view, words, TicketActionsView($, view, ticket))}
      {PracticeGridView($, view, ticket)}
    </Box>
  )
}

export function OnlyActiveToggleView($: EngineInterface, view: ViewContext) {
  const { Box, Text } = view.elements
  return (
    <Box key="only-active-box" flexDirection="row" columnGap={1} alignItems="center">
      <Text mono size="caption" color={BRAND.muted}>
        Active session only
      </Text>
      {SwitchView(view, 'only-active', view.onlyActive, () => toggleOnlyActive($))}
    </Box>
  )
}
