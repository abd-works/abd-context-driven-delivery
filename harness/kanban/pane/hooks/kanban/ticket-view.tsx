import type { ElementTable, EngineInterface } from 'claude-code'

import type { ColumnJson, TicketCardJson, TileJson } from '../../types'
import { ActionButtonView } from './action-button'
import { ACTION_MARKS, BRAND, PRACTICES, STATES } from './brand'
import { select, toggleOnlyActive } from './board-client'
import { openFiles, openHelp, openReport } from './side-panel-client'
import {
  archive,
  chooseAction,
  enablePractice,
  fillHandoff,
  fillRunNext,
  fillSplit,
  moveNext,
  movePrevious,
  openActivation,
  reviewTile,
  runTileAction,
  TicketClient,
  toggleCard,
  toggleFormat,
  toggleTile,
  validateTile,
} from './ticket-client'
import { ageOf, isLocked } from './view-context'
import type { ViewContext } from './view-context'

// The board's stages and the details' stages share these, so Discovery sits over Discovery all the way down.
export const EDGE_COLUMN_WIDTH = '14%'
export const STAGE_WIDTH = '23%'
export const COLUMN_GAP = 1
const MAXIMUM_HOVER_SCOPE = 64
const FACE_LINES = 3
const EXPANDED_CARD_TOP = 5
const CARD_TILE_WIDTH = 28
const TILE_ACTIONS = ['generate', 'sketch', 'iterate', 'document', 'render']
const TILE_ACTIONS_WITHOUT_FORMATS = ['sketch', 'iterate', 'document']

const fidelityName = (slug: string, prefix: string): string => slug.slice(prefix.length)

const guidanceSlug = (slug: string): string => slug.replaceAll('_', '-')

const practiceOf = (slug: string) => PRACTICES.find(candidate => slug.startsWith(candidate.prefix))

// The practice's skill for a fidelity: `clean_engineering-code` is /practices-clean-engineering-clean-engineering-code.
const skillOf = (slug: string): string => `/practices-${guidanceSlug(practiceOf(slug)?.prefix ?? '')}${guidanceSlug(slug)}`

function cardSegments(view: ViewContext, ticket: TicketClient): TicketCardJson['segments'] {
  const place = ticket.address
  const stage = view.board.stageOf(view.board.ticketNamed(ticket.name)!)
  return (stage?.work_required ?? [])
    .filter(slug => ticket.isEnabled(practiceOf(slug)?.key ?? ''))
    .map(slug => {
      const state = ticket.stateOf(slug)
      return {
        scope: `skill-${place}-${slug}`.slice(0, MAXIMUM_HOVER_SCOPE),
        color: state.key === 'violations' ? state.color : practiceOf(slug)?.color ?? BRAND.idle,
        isDim: state.key === 'not_started',
        skill: skillOf(slug),
      }
    })
}

function cardTail(ticket: TicketClient): TicketCardJson['tail'] {
  if (ticket.isDone) return { text: 'done', color: BRAND.success }
  return ticket.next ? { text: `next: ${ticket.next}`, color: BRAND.accent } : null
}

const borderOf = ({ board, address }: ViewContext, ticket: TicketClient): string =>
  ticket.name === board.active ? BRAND.accent : ticket.address === address ? BRAND.text : BRAND.border

function cardJson(view: ViewContext, ticket: TicketClient): TicketCardJson {
  return {
    address: ticket.address,
    title: ticket.title,
    meta: [ticket.scope, ageOf(view.now, ticket.lastActivity)].filter(Boolean).join(' · '),
    segments: cardSegments(view, ticket),
    tail: cardTail(ticket),
    titleColor: BRAND.text,
    mutedColor: BRAND.muted,
  }
}

function SegmentsView({ elements: { Text } }: ViewContext, segments: TicketCardJson['segments']) {
  return (
    <Text>
      {segments.map(segment => (
        <Text color={segment.color} dimColor={segment.isDim}>
          ▬▬{' '}
        </Text>
      ))}
    </Text>
  )
}

function ButtonFaceView($: EngineInterface, view: ViewContext, ticket: TicketClient) {
  const { Button, Text } = view.elements
  const card = cardJson(view, ticket)
  return [
    <Button key={`ticket-${ticket.address}`} plain onPress={() => select($, ticket.address)}>
      <Text bold color={BRAND.text}>
        {ticket.title}
      </Text>
    </Button>,
    <Text color={BRAND.muted}>{card.meta}</Text>,
    SegmentsView(view, card.segments),
    card.tail ? <Text color={card.tail.color}>{card.tail.text}</Text> : null,
  ]
}

function CardControlView({ elements: { Button } }: ViewContext, key: string, label: string, onPress: (() => unknown) | null) {
  return <Button key={key} plain label={label} dimColor={!onPress} onPress={onPress ?? (() => undefined)} />
}

function CardControlsView($: EngineInterface, view: ViewContext, ticket: TicketClient) {
  const { Box } = view.elements
  const place = ticket.address
  const isActive = ticket.name === view.board.active
  const locked = isLocked(view, ticket.name)
  return (
    <Box key={`moves-${place}`} flexDirection="row" flexWrap="wrap" justifyContent="space-between" flexShrink={0}>
      {CardControlView(view, `previous-${place}`, '←', locked ? null : () => movePrevious($, ticket.name))}
      {CardControlView(view, `expand-${place}`, view.openCard === ticket.name ? '▴' : '▾', () => toggleCard($, ticket.name))}
      {CardControlView(view, `activate-${place}`, isActive ? 'Close' : 'Activate', ticket.isClosed ? null : () => openActivation($, ticket, isActive))}
      {CardControlView(view, `next-${place}`, '→', ticket.canMoveNext && !locked ? () => moveNext($, ticket.name) : null)}
    </Box>
  )
}

export function TicketCardView($: EngineInterface, view: ViewContext, ticket: TicketClient) {
  const { elements, hasSurfaceModules, board } = view
  const { Box } = elements
  const Client = hasSurfaceModules ? (elements as ElementTable<'desktop'>).Client : null
  const card = cardJson(view, ticket)
  return (
    <Box
      key={`card-${ticket.address}`}
      flexDirection="column"
      flexShrink={0}
      borderStyle={ticket.name === board.active ? 'bold' : 'single'}
      borderColor={borderOf(view, ticket)}
      hover={{ borderColor: BRAND.muted }}
      backgroundColor={BRAND.raised}
      paddingX={1}
    >
      {Client ? <Client key={`face-${ticket.address}`} module="./ticket-card.tsx" props={card} width="100%" height={Math.max(FACE_LINES, card.segments.length)} /> : ButtonFaceView($, view, ticket)}
      {CardControlsView($, view, ticket)}
    </Box>
  )
}

function formatsOf(column: ColumnJson, slugs: string[]): string[] {
  return [...new Set(slugs.flatMap(slug => column.formats?.[slug] ?? []))]
}

const hasMade = (tile: TileJson, format: string): boolean =>
  tile.slugs.some(slug => (tile.files[slug]?.[format] ?? []).some(entry => entry.exists))

function FormatChipsView($: EngineInterface, view: ViewContext, stage: ColumnJson, tile: TileJson) {
  const { Box, Button } = view.elements
  return (
    <Box key="formats" flexDirection="row" flexWrap="wrap" columnGap={1}>
      {formatsOf(stage, tile.slugs).map(format => (
        <Button
          key={`format-${format}`}
          label={`${hasMade(tile, format) ? '✓ ' : ''}${format}`}
          variant={tile.picked.includes(format) ? 'primary' : 'secondary'}
          onPress={() => toggleFormat($, format)}
        />
      ))}
    </Box>
  )
}

function ActionChoiceView($: EngineInterface, view: ViewContext, tile: TileJson) {
  const { Box, Button } = view.elements
  return (
    <Box key="actions" flexDirection="row" flexWrap="wrap" columnGap={1}>
      {TILE_ACTIONS.map(action => (
        <Button
          key={`action-${action}`}
          label={action}
          variant={tile.action === action ? 'primary' : 'secondary'}
          onPress={() => chooseAction($, action)}
        />
      ))}
    </Box>
  )
}

function canRun(view: ViewContext, tile: TileJson): boolean {
  if (isLocked(view, tile.ticket)) return false
  return TILE_ACTIONS_WITHOUT_FORMATS.includes(tile.action) || tile.picked.length > 0
}

const allow = (ticket: TicketClient, tile: TileJson, action: string): boolean => tile.slugs.every(slug => ticket.allows(slug, action))

function TileWorkView($: EngineInterface, view: ViewContext, ticket: TicketClient, tile: TileJson) {
  const { Box } = view.elements
  const locked = isLocked(view, ticket.name)
  const slug = tile.slugs[0] ?? ''
  return (
    <Box key="work" flexDirection="row" flexWrap="wrap" columnGap={1}>
      {ActionButtonView(view, 'run', 'Run', canRun(view, tile) ? () => runTileAction($, tile) : null, true)}
      {ActionButtonView(view, 'validate', 'Validate', !locked && allow(ticket, tile, 'validate') ? () => validateTile($, tile) : null)}
      {ActionButtonView(view, 'reviewed', 'Reviewed', !locked && allow(ticket, tile, 'review') ? () => reviewTile($, tile) : null)}
      {ActionButtonView(view, 'open-report', 'Report', ticket.reportOf(slug) ? () => openReport($, ticket.name, slug) : null)}
      {ActionButtonView(view, 'show-list', 'List', () => openFiles($, ticket.name, tile.slugs, 'list'))}
      {ActionButtonView(view, 'show-folder', 'Folder', () => openFiles($, ticket.name, tile.slugs, 'folder'))}
      {ActionButtonView(view, 'show-files', 'Files', () => openFiles($, ticket.name, tile.slugs, 'files'))}
    </Box>
  )
}

// What a person does on an open tile: pick an action and formats, run it, validate, review, and look at the files.
function TileBarView($: EngineInterface, view: ViewContext, ticket: TicketClient, stage: ColumnJson, tile: TileJson) {
  const { Box } = view.elements
  return (
    <Box key="tile-bar" flexDirection="column" borderStyle="single" borderColor={BRAND.accent} backgroundColor={BRAND.surface} paddingX={1}>
      {ActionChoiceView($, view, tile)}
      {FormatChipsView($, view, stage, tile)}
      {TileWorkView($, view, ticket, tile)}
    </Box>
  )
}

function ActionStatesView({ elements: { Text } }: ViewContext, ticket: TicketClient, slug: string) {
  const actions = ticket.actionsOf(slug)
  return (
    <Text color={BRAND.muted}>
      G{ACTION_MARKS[actions.generate]} V{ACTION_MARKS[actions.validate]} R{ACTION_MARKS[actions.review]}
    </Text>
  )
}

function TileHeadingView($: EngineInterface, view: ViewContext, ticket: TicketClient, stage: ColumnJson, slug: string, prefix: string, place: string) {
  const { elements, hasSurfaceModules, tile } = view
  const { Box, Button, Text } = elements
  const label = fidelityName(slug, prefix).replaceAll('_', '-')
  const mark = tile?.place === place ? '▴' : '▾'
  const color = practiceOf(slug)?.color ?? BRAND.muted
  const Client = hasSurfaceModules ? (elements as ElementTable<'desktop'>).Client : null
  const hover = { place, ticket: ticket.name, stage: stage.name, slugs: [slug], label, mark, color }
  return (
    <Box key={`heading-${slug}`} flexDirection="row" columnGap={1} flexShrink={0}>
      <Box key="name" flexGrow={1}>
        {Client ? (
          <Client key={`tile-${place}`} module="./tile-hover.tsx" props={hover} flexGrow={1} height={1} />
        ) : (
          <Button key={`toggle-${place}`} plain label={`${label} ${mark}`} onPress={() => toggleTile($, ticket.name, stage.name, place, [slug])} />
        )}
      </Box>
      <Button key={`help-${place}`} plain label="?" onPress={() => openHelp($, practiceOf(slug)?.key ?? '', fidelityName(slug, prefix))} />
      {ticket.stateOf(slug).key === 'violations' ? <Text color={BRAND.error}>!</Text> : null}
    </Box>
  )
}

// `place` says where this tile is drawn, because the details and an opened card can show the same fidelity at once.
function TileView($: EngineInterface, view: ViewContext, ticket: TicketClient, stage: ColumnJson, slug: string, place: string) {
  const { Box, Text } = view.elements
  const prefix = practiceOf(slug)?.prefix ?? ''
  const state = ticket.stateOf(slug)
  const isNext = stage.name === ticket.column && ticket.next === slug
  return (
    <Box key={`tile-box-${place}`} flexDirection="column" flexShrink={0} borderStyle="single" borderColor={state.key === 'violations' ? BRAND.error : isNext ? BRAND.accent : BRAND.border} paddingX={1}>
      {TileHeadingView($, view, ticket, stage, slug, prefix, place)}
      <Box key={`standing-${slug}`} flexDirection="row" flexWrap="wrap" columnGap={1} flexShrink={0}>
        <Text backgroundColor={state.color} color={BRAND.canvas} dimColor={state.key === 'not_started' && !isNext}>
          {' '}
          {state.label}{' '}
        </Text>
        {ActionStatesView(view, ticket, slug)}
      </Box>
      <Box display="none" hover={{ display: 'flex' }}>
        <Text color={BRAND.text}>{skillOf(slug)}</Text>
      </Box>
    </Box>
  )
}

// An opened card sits over the board and shows the same tiles as the details, so a ticket can be worked from either
// place. It is drawn last from the pane's root, because a Box paints over only what was drawn before it.
export function CardExpansionView($: EngineInterface, view: ViewContext) {
  const { elements, board, openCard, bodyColumns } = view
  const { Box, Text } = elements
  const json = openCard ? board.ticketNamed(openCard) : undefined
  const stage = json ? board.stageOf(json) : undefined
  if (!json || !stage) return null
  const ticket = new TicketClient(json)
  const slugs = (stage.work_required ?? []).filter(slug => ticket.isEnabled(practiceOf(slug)?.key ?? ''))
  const open = view.tile?.place.startsWith(`card/${ticket.address}/`) ? view.tile : null
  return (
    <Box
      key="card-tiles"
      position="absolute"
      top={EXPANDED_CARD_TOP}
      left={1}
      width={Math.max(bodyColumns - 2, 1)}
      flexDirection="column"
      borderStyle="bold"
      borderColor={BRAND.accent}
      backgroundColor={BRAND.raised}
      paddingX={1}
    >
      <Box key="card-tiles-head" flexDirection="row" justifyContent="space-between">
        <Text bold color={BRAND.text}>
          {ticket.title} <Text color={BRAND.muted}>{ticket.place}</Text>
        </Text>
        {ActionButtonView(view, `collapse-${ticket.address}`, '▴', () => toggleCard($, ticket.name))}
      </Box>
      <Box key="card-tiles-row" flexDirection="row" flexWrap="wrap" columnGap={1}>
        {slugs.map(slug => (
          <Box key={`card-tile-${slug}`} width={CARD_TILE_WIDTH}>
            {TileView($, view, ticket, stage, slug, `card/${ticket.address}/${slug}`)}
          </Box>
        ))}
      </Box>
      {open ? TileBarView($, view, ticket, stage, open) : null}
    </Box>
  )
}

function GridCellView($: EngineInterface, view: ViewContext, ticket: TicketClient, stage: ColumnJson, practice: (typeof PRACTICES)[number]) {
  const { Box, Text } = view.elements
  const slug = (stage.work_required ?? []).find(required => required.startsWith(practice.prefix))
  return (
    <Box key={`cell-${stage.name}-${practice.prefix}`} flexDirection="column" flexShrink={0} width={STAGE_WIDTH}>
      {slug ? TileView($, view, ticket, stage, slug, `${ticket.address}/${slug}`) : <Text color={BRAND.muted}>—</Text>}
    </Box>
  )
}

function StageHeadView($: EngineInterface, view: ViewContext, ticket: TicketClient, stage: ColumnJson) {
  const { Box, Button, Text } = view.elements
  const place = `${ticket.address}/${stage.name}`
  const slugs = (stage.work_required ?? []).filter(slug => ticket.isEnabled(practiceOf(slug)?.key ?? ''))
  return (
    <Box key={`stage-${stage.name}`} flexDirection="column" width={STAGE_WIDTH} paddingX={1}>
      <Box key="stage-name" flexDirection="row" justifyContent="space-between">
        <Text color={BRAND.muted}>{stage.name}</Text>
        <Button key={`stage-menu-${stage.name}`} plain label={view.tile?.place === place ? '▴' : '▾'} onPress={() => toggleTile($, ticket.name, stage.name, place, slugs)} />
      </Box>
    </Box>
  )
}

function PracticeHeadingView($: EngineInterface, view: ViewContext, ticket: TicketClient, practice: (typeof PRACTICES)[number]) {
  const { Box, Button } = view.elements
  const isOn = ticket.isEnabled(practice.key)
  const onToggle = isLocked(view, ticket.name) ? null : () => enablePractice($, ticket, practice.key, !isOn)
  return (
    <Box key={`heading-${practice.name}`} flexDirection="column" width={EDGE_COLUMN_WIDTH} paddingX={1}>
      <Button key={`practice-help-${practice.key}`} plain label={practice.name} onPress={() => openHelp($, practice.key, '')} />
      {ActionButtonView(view, `practice-${practice.key}`, isOn ? 'on' : 'off', onToggle)}
    </Box>
  )
}

function PracticeGridView($: EngineInterface, view: ViewContext, ticket: TicketClient) {
  const { Box } = view.elements
  const { stages } = view.board
  return (
    <Box key="practices" flexDirection="column" flexShrink={0}>
      <Box key="stage-names" flexDirection="row" columnGap={COLUMN_GAP} flexShrink={0}>
        <Box key="heading-corner" width={EDGE_COLUMN_WIDTH} />
        {stages.map(stage => StageHeadView($, view, ticket, stage))}
      </Box>
      {PRACTICES.map(practice => (
        <Box key={`practice-${practice.name}`} flexDirection="row" columnGap={COLUMN_GAP} flexShrink={0}>
          {PracticeHeadingView($, view, ticket, practice)}
          {stages.map(stage => GridCellView($, view, ticket, stage, practice))}
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
  const runNext = isHeld ? () => openReport($, ticket.name, ticket.next ?? '') : () => fillRunNext($, ticket)
  return (
    <Box key="actions" flexDirection="row" flexWrap="wrap" gap={1} flexShrink={0}>
      {ActionButtonView(view, 'run-next', ticket.runNextLabel, ticket.next && !isLocked(view, ticket.name) ? runNext : null)}
      {ActionButtonView(view, 'split', 'Split', isOff ? null : () => fillSplit($, ticket))}
      {ActionButtonView(view, 'switch-to', 'Activate', ticket.name === active || ticket.isClosed ? null : () => openActivation($, ticket, false))}
      {ActionButtonView(view, 'handoff', 'Handoff', isOff ? null : () => fillHandoff($, ticket))}
      {ActionButtonView(view, 'close', 'Close', ticket.name === active && !ticket.isClosed ? () => openActivation($, ticket, true) : null)}
      {ActionButtonView(view, 'archive', 'Archive', isLocked(view, ticket.name) && !ticket.isClosed ? null : () => archive($, ticket))}
      {ActionButtonView(view, 'files', 'Files', () => openFiles($, ticket.name, view.board.allSlugs(), 'list'))}
      {ActionButtonView(view, 'report', 'Report', ticket.firstReport ? () => openReport($, ticket.name, ticket.firstReport) : null)}
    </Box>
  )
}

// Above the grid and at full width, because a tile low in the grid would have its bar clipped by the details region.
function DetailTileBarView($: EngineInterface, view: ViewContext, ticket: TicketClient) {
  const { tile, board } = view
  if (tile?.ticket !== ticket.name || tile.place.startsWith('card/')) return null
  const stage = board.stages.find(entry => entry.name === tile.stage)
  return stage ? TileBarView($, view, ticket, stage, tile) : null
}

export function TicketDetailView($: EngineInterface, view: ViewContext, ticket: TicketClient) {
  const { Box, Text } = view.elements
  const locked = isLocked(view, ticket.name)
  return (
    <Box key="detail" flexDirection="column" flexShrink={0} gap={1} paddingX={1}>
      <Text bold color={BRAND.text}>
        {ticket.title} <Text color={BRAND.muted}>{ticket.place}</Text>
      </Text>
      <Text color={BRAND.muted}>
        {ticket.handoff ? `Latest handoff: ${ticket.handoff}` : 'No handoff yet'}
        {ticket.next ? ` · Next: ${ticket.next}, ${ticket.nextAction}` : ''}
        {locked ? ' · Activate this session to run actions' : ''}
      </Text>
      {TicketActionsView($, view, ticket)}
      {DetailTileBarView($, view, ticket)}
      {PracticeGridView($, view, ticket)}
    </Box>
  )
}

export function OnlyActiveToggleView($: EngineInterface, view: ViewContext) {
  return ActionButtonView(view, 'only-active', `Active only: ${view.onlyActive ? 'on' : 'off'}`, () => toggleOnlyActive($))
}

export function LegendView({ elements: { Box, Text } }: ViewContext) {
  return (
    <Box key="legend" flexDirection="row" flexWrap="wrap" columnGap={2} paddingX={1}>
      {Object.values(STATES).map(state => (
        <Text color={BRAND.muted}>
          <Text color={state.color}>■</Text> {state.label}
        </Text>
      ))}
      <Text color={BRAND.muted}>blocks: {PRACTICES.map(practice => practice.name).join(' · ')}</Text>
    </Box>
  )
}
