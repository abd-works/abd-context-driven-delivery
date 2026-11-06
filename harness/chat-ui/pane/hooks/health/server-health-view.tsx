import type { HealthViewJson, InstallJson, ServerHealthJson } from '../../types'
import { colourOf, detailsOf, headlineOf, installLineOf, partsOf } from './server-health-wording'
import type { EngineInterface } from 'claude-code'

import { BRAND } from '../brand'
import { GlyphButtonView } from '../glyph-button-view'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// Wide enough for an icon and the longest value, `▦ running :5173`; the columns wrap when the band is narrower than five of them.
const PART_WIDTH = 16

type Actions = {
  togglePin: () => unknown
  openDetails: () => unknown
  hideDetails: () => unknown
  reconnect: () => unknown
  runInstall: () => unknown
}
type Band = {
  health: ServerHealthJson
  view: HealthViewJson
  install: InstallJson
  actions: Actions
}
// The hover group of the health mark and its panel above the line: the pointer on either keeps the panel shown.
export const HEALTH_SCOPE = 'server-health'

// Where the panel is drawn: above the line over the health mark, revealed on hover or pinned, or on top of the session
// card, shown whenever the card is. The card's copy prefixes its keys, so a press finds the Button it means. The panel at the mark
// has no key of its own, so hovering the mark's keyed Box reveals it.
type Placement = { isRevealed: boolean; keyOf: (name: string) => string; panel: { key?: string } }
const AT_THE_MARK = (view: HealthViewJson): Placement => ({ isRevealed: view.isPinned, keyOf: name => name, panel: {} })
const ON_THE_CARD: Placement = { isRevealed: true, keyOf: name => `card-${name}`, panel: { key: 'card-health' } }

const LOOKS = {
  connected: { glyph: '✓', color: BRAND.success, wash: BRAND.successWash, border: BRAND.success },
  reconnecting: { glyph: '⟳', color: BRAND.warning, wash: BRAND.raised, border: BRAND.border },
  disconnected: { glyph: '✕', color: BRAND.error, wash: BRAND.errorWash, border: BRAND.error },
  'tools-missing': { glyph: '!', color: BRAND.warning, wash: BRAND.warningWash, border: BRAND.warning },
}


// The surface has no tooltip, so the part's name is a card revealed while the pointer is over its icon and value.
function PartsView({ Box, Text }: ElementTable, health: ServerHealthJson, placement: Placement) {
  return (
    <Box flexDirection="row" flexWrap="wrap" columnGap={2}>
      {partsOf(health).map(part => (
        <Box key={placement.keyOf(part.label)} flexDirection="row" gap={1} width={PART_WIDTH}>
          <Text size="heading" color={colourOf(part)}>{part.icon}</Text>
          <Text color={colourOf(part)}>{part.value}</Text>
          <Box position="absolute" top={-1} left={0} paddingX={1} backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
            <Text color={BRAND.text}>{part.label}</Text>
          </Box>
        </Box>
      ))}
    </Box>
  )
}

function DetailsView({ Box, Text }: ElementTable, health: ServerHealthJson, install: InstallJson) {
  return (
    <Box flexDirection="column">
      {detailsOf(health, install).map(([name, value]) => (
        <Box key={name} flexDirection="row" gap={1}>
          <Text color={BRAND.muted}>{name}</Text>
          <Text color={BRAND.text}>{value}</Text>
        </Box>
      ))}
    </Box>
  )
}

function ButtonsView(elements: ElementTable, { health, view, install, actions }: Band, { keyOf }: Placement) {
  const { Box, Button } = elements
  const isDisconnected = health.connection === 'disconnected'
  if (!isDisconnected && health.connection !== 'tools-missing') return null
  const canInstall = install.state !== 'running' && install.state !== 'installed'
  return (
    <Box flexDirection="row" gap={1}>
      {view.areDetailsOpen ? <Button key={keyOf('health-hide')} label="Hide" onPress={actions.hideDetails} /> : <Button key={keyOf('health-details')} label="Details" onPress={actions.openDetails} />}
      {canInstall ? <Button key={keyOf('health-install')} label="Run install" onPress={actions.runInstall} /> : null}
      {isDisconnected ? <Button key={keyOf('health-reconnect')} label="Reconnect" variant="primary" onPress={actions.reconnect} /> : null}
    </Box>
  )
}

// What is wrong, in one line: Disconnected, Tools missing, Connecting or Reconnecting, and nothing while connected.
function HeadlineView({ Box, Text }: ElementTable, health: ServerHealthJson) {
  const { title, detail } = headlineOf(health)
  if (!title) return null
  return (
    <Box flexDirection="row" gap={1}>
      <Text weight="semibold" color={LOOKS[health.connection].color}>{title}</Text>
      {detail ? <Text color={BRAND.text}>{detail}</Text> : null}
    </Box>
  )
}

// Installing., Installed. or Install failed., once a person has run the install.
function InstallLineView({ Text }: ElementTable, install: InstallJson) {
  const line = installLineOf(install)
  return line ? <Text color={BRAND.text}>{line}</Text> : null
}

function ExpandedView(elements: ElementTable, band: Band, placement: Placement) {
  const { Box } = elements
  const { health, view, install } = band
  const look = LOOKS[health.connection]
  return (
    <Box
      {...placement.panel}
      flexDirection="column"
      paddingX={1}
      borderStyle="single"
      borderColor={look.border}
      backgroundColor={look.wash}
      alignSelf="flex-start"
      {...(placement.isRevealed ? {} : { display: 'none' as const, hover: { display: 'flex' as const, scope: HEALTH_SCOPE } })}
    >
      {HeadlineView(elements, health)}
      {InstallLineView(elements, install)}
      {health.connection === 'connected' ? PartsView(elements, health, placement) : null}
      {view.areDetailsOpen ? DetailsView(elements, health, install) : null}
      {ButtonsView(elements, band, placement)}
    </Box>
  )
}

// The band is one icon on the line; its panel opens above the line while the pointer is on the icon or the panel, or
// once a click pins it, so it stays out of the way.
export function ServerHealthBandView(elements: ElementTable, band: Band) {
  const { Box } = elements
  const look = LOOKS[band.health.connection]
  return (
    <Box key="server-health" flexDirection="row" hover={{ scope: HEALTH_SCOPE }}>
      {GlyphButtonView(elements, 'health-icon', look.glyph, look.color, band.actions.togglePin)}
    </Box>
  )
}

// The panel over the health mark, drawn above the line.
export function ServerHealthMarkPanelView(elements: ElementTable, band: Band) {
  const { Box } = elements
  return <Box key="health-panel" flexDirection="column">{ExpandedView(elements, band, AT_THE_MARK(band.view))}</Box>
}

// The same panel stacked on top of the session card, as CDR 0001 has hovering the session name show it.
export function ServerHealthPanelView(elements: ElementTable, band: Band) {
  return ExpandedView(elements, band, ON_THE_CARD)
}
