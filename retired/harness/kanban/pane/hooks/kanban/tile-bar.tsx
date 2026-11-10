import type { ElementTable, EngineInterface } from 'claude-code'

import type { ColumnJson, TileJson } from '../../types'
import { ActionButtonView, LinkButtonView } from './action-button'
import { ACTION_STANDINGS, BRAND, DIM_TEXT_LIGHT, faded, STEP_FAILED } from './brand'
import { openFiles, openReport } from './side-panel-client'
import { chooseAction, reviewTile, runTileAction, TicketClient, toggleFormats, validateTile } from './ticket-client'
import { countOf } from './ticket-summary'
import { chipDoneCount, chipOfferedCount, chipsOf, chosenFormats } from './tile-formats'
import type { FormatChip } from './tile-formats'
import { isLocked } from './view-context'
import type { ViewContext } from './view-context'

const TILE_ACTIONS = ['generate', 'render', 'sketch', 'iterate', 'document']

function chipWords(stage: ColumnJson, tile: TileJson, chip: FormatChip): { words: string; isDone: boolean } {
  const done = chipDoneCount(tile.files, tile.slugs, chip)
  const offered = chipOfferedCount(stage, tile.slugs, chip)
  if (!done) return { words: chip.glyph, isDone: false }
  return { words: done === offered ? `✓ ${chip.glyph}` : `${chip.glyph} ${done} of ${offered}`, isDone: true }
}

// Picked is solid orange, generated is green with a check, and a plain chip is neither. A Button holds only text, so
// a Box carries the chip's ground and edge; a terminal's border takes whole rows, so there the ground alone shows.
function FormatChipView($: EngineInterface, view: ViewContext, stage: ColumnJson, tile: TileJson, chip: FormatChip) {
  const { Box, Button, Text } = view.elements
  const locked = isLocked(view, tile.ticket)
  const isOn = tile.picked.includes(chip.label)
  const { words, isDone } = chipWords(stage, tile, chip)
  const color = isOn ? BRAND.onAccent : isDone ? BRAND.success : BRAND.muted
  const frame = view.hasPictures ? { borderStyle: 'single', borderColor: isOn ? BRAND.accent : isDone ? BRAND.success : BRAND.border } : {}
  return (
    <Box key={`format-box-${chip.label}`} flexShrink={0} paddingX={1} backgroundColor={isOn ? BRAND.accent : BRAND.raised} {...frame}>
      <Button key={`format-${chip.label}`} plain label={chip.label} onPress={locked ? () => undefined : () => toggleFormats($, chip.label)}>
        <Text mono size="footnote" color={locked ? faded(color, DIM_TEXT_LIGHT) : color}>
          {words}
        </Text>
      </Button>
    </Box>
  )
}

// A list box where the surface has one; mobile has no Select, so it gets a Button for each action. A Select cannot be
// disabled, so on a locked ticket its action is drawn as text instead.
function ActionChoiceView($: EngineInterface, view: ViewContext, tile: TileJson) {
  const { elements, hasInputs } = view
  const { Button, Text } = elements
  const locked = isLocked(view, tile.ticket)
  if (hasInputs && locked) {
    return (
      <Text key="action" mono size="footnote" color={BRAND.idle}>
        {tile.action}
      </Text>
    )
  }
  if (hasInputs) {
    const { Select } = elements as ElementTable<'desktop'>
    return <Select key="action" options={TILE_ACTIONS.map(action => ({ value: action }))} value={tile.action} onSelect={action => chooseAction($, action)} />
  }
  return TILE_ACTIONS.map(action => (
    <Button key={`action-${action}`} label={action} dimColor={locked} variant={tile.action === action ? 'primary' : 'secondary'} onPress={locked ? () => undefined : () => chooseAction($, action)} />
  ))
}

function canRun(view: ViewContext, stage: ColumnJson, tile: TileJson): boolean {
  if (isLocked(view, tile.ticket) || !tile.slugs.length) return false
  if (!chosenFormats(stage, tile.slugs, tile.picked).length) return false
  return tile.action !== 'render' || chipsOf(stage, tile.slugs).some(chip => chipDoneCount(tile.files, tile.slugs, chip) > 0)
}

const allow = (ticket: TicketClient, tile: TileJson, action: string): boolean => tile.slugs.length > 0 && tile.slugs.every(slug => ticket.allows(slug, action))

function StepMarkView({ elements: { Text } }: ViewContext, key: string, mark: string, color: string) {
  return (
    <Text key={key} mono weight="bold" color={color}>
      {mark}
    </Text>
  )
}

function RunLineView($: EngineInterface, view: ViewContext, ticket: TicketClient, stage: ColumnJson, tile: TileJson) {
  const { Box } = view.elements
  const standing = ACTION_STANDINGS[ticket.standingOf(tile.slugs, 'generate')]!
  return (
    <Box key="run-line" flexDirection="row" flexWrap="wrap" alignItems="center" columnGap={1}>
      {ActionChoiceView($, view, tile)}
      {chipsOf(stage, tile.slugs).map(chip => FormatChipView($, view, stage, tile, chip))}
      <Box key="run-space" flexGrow={1} />
      {ActionButtonView(view, 'run', 'Run', canRun(view, stage, tile) ? () => runTileAction($, tile, stage) : null, true)}
      {StepMarkView(view, 'generate-mark', standing.mark, standing.color)}
    </Box>
  )
}

function validateStanding(ticket: TicketClient, tile: TileJson) {
  if (tile.slugs.some(slug => ticket.stateOf(slug).key === 'violations')) {
    const count = ticket.violationCountOf(tile.slugs)
    return { mark: STEP_FAILED, color: BRAND.error, text: count ? countOf(count, 'violation') : 'violations' }
  }
  return { ...ACTION_STANDINGS[ticket.standingOf(tile.slugs, 'validate')]!, text: '' }
}

function ValidateLineView($: EngineInterface, view: ViewContext, ticket: TicketClient, tile: TileJson) {
  const { Box, Text } = view.elements
  const locked = isLocked(view, ticket.name)
  const standing = validateStanding(ticket, tile)
  const reported = tile.slugs.find(slug => ticket.reportOf(slug))
  return (
    <Box key="validate-line" flexDirection="row" flexWrap="wrap" alignItems="center" columnGap={1}>
      {ActionButtonView(view, 'validate', 'validate', !locked && allow(ticket, tile, 'validate') ? () => validateTile($, tile) : null)}
      {StepMarkView(view, 'validate-mark', standing.mark, standing.color)}
      {standing.text ? (
        <Text mono size="caption" color={standing.color}>
          {standing.text}
        </Text>
      ) : null}
      {reported ? LinkButtonView(view, 'open-report', 'report', standing.text ? BRAND.error : BRAND.muted, () => openReport($, ticket.name, reported)) : null}
    </Box>
  )
}

function ReviewLineView($: EngineInterface, view: ViewContext, ticket: TicketClient, tile: TileJson, hasFileLinks: boolean) {
  const { Box } = view.elements
  const locked = isLocked(view, ticket.name)
  const standing = ACTION_STANDINGS[ticket.standingOf(tile.slugs, 'review')]!
  return (
    <Box key="review-line" flexDirection="row" flexWrap="wrap" alignItems="center" columnGap={1}>
      {ActionButtonView(view, 'reviewed', 'review', !locked && allow(ticket, tile, 'review') ? () => reviewTile($, tile) : null)}
      {StepMarkView(view, 'review-mark', standing.mark, standing.color)}
      <Box key="review-space" flexGrow={1} />
      {hasFileLinks ? FileLinksView($, view, ticket, tile.slugs, 'show') : null}
    </Box>
  )
}

export function FileLinksView($: EngineInterface, view: ViewContext, ticket: TicketClient, slugs: string[], prefix: string) {
  return ['list', 'folder', 'files'].map(mode => LinkButtonView(view, `${prefix}-${mode}`, mode, BRAND.text, () => openFiles($, ticket.name, slugs, mode)))
}

// What a person does on an open tile: pick an action and formats, run it, validate, review, and look at the files.
export function TileBarView($: EngineInterface, view: ViewContext, ticket: TicketClient, stage: ColumnJson, tile: TileJson) {
  const { Box } = view.elements
  return (
    <Box key="tile-bar" flexDirection="column" flexShrink={0} rowGap={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.canvas} paddingX={1}>
      {RunLineView($, view, ticket, stage, tile)}
      {ValidateLineView($, view, ticket, tile)}
      {ReviewLineView($, view, ticket, tile, true)}
    </Box>
  )
}

// The same bar on an opened card, which already has an edge and its file links.
export function CardBarView($: EngineInterface, view: ViewContext, ticket: TicketClient, stage: ColumnJson, tile: TileJson) {
  const { Box } = view.elements
  return (
    <Box key="card-bar" flexDirection="column" flexShrink={0} rowGap={1}>
      {RunLineView($, view, ticket, stage, tile)}
      {ValidateLineView($, view, ticket, tile)}
      {ReviewLineView($, view, ticket, tile, false)}
    </Box>
  )
}
