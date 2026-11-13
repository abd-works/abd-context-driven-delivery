import type { AppOpeningJson, HealthViewJson, InstallJson, ServerHealthJson } from '../../types'
import { appLineOf, colourOf, detailsOf, headlineOf, installLineOf, partsOf, type Part } from './server-health-wording'
import type { EngineInterface } from 'claude-code'

import { BRAND } from '../shared/brand'
import { GlyphButtonView } from '../shared/glyph-button-view'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

type Actions = {
  toggleCard: () => unknown
  openDetails: () => unknown
  hideDetails: () => unknown
  reconnect: () => unknown
  runInstall: () => unknown
  openApp: (label: string) => unknown
}
type Band = {
  health: ServerHealthJson
  view: HealthViewJson
  install: InstallJson
  opening: AppOpeningJson
  actions: Actions
}
const LOOKS = {
  connected: { glyph: '✓', color: BRAND.success, wash: BRAND.successWash, border: BRAND.success },
  reconnecting: { glyph: '⟳', color: BRAND.warning, wash: BRAND.raised, border: BRAND.border },
  disconnected: { glyph: '✕', color: BRAND.error, wash: BRAND.errorWash, border: BRAND.error },
  'tools-missing': { glyph: '!', color: BRAND.warning, wash: BRAND.warningWash, border: BRAND.warning },
}


// The surface has no tooltip, so the part's name is a card revealed while the pointer is over its icon and value. An
// app's icon and value are a Button, a press readying the app and opening it in the side panel; a Button holds only
// strings and Text, so the card sits beside it in the part's Box, never inside it.
function PartView({ Box, Button, Text }: ElementTable, part: Part, actions: Actions) {
  const { app } = part
  const icon = <Text color={colourOf(part)}>{part.icon}</Text>
  const value = <Text color={colourOf(part)}>{part.value}</Text>
  return (
    <Box key={part.label} flexDirection="row" gap={1}>
      {app === undefined ? <>{icon}{value}</> : (
        <Button key={`health-app-${app}`} plain onPress={() => actions.openApp(app)}>
          {icon} {value}
        </Button>
      )}
      <Box position="absolute" top={-1} left={0} paddingX={1} backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
        <Text color={BRAND.text}>{part.label}</Text>
      </Box>
    </Box>
  )
}

function PartsView(elements: ElementTable, health: ServerHealthJson, actions: Actions) {
  const { Box } = elements
  return (
    <Box flexDirection="row" columnGap={3}>
      {partsOf(health).map(part => PartView(elements, part, actions))}
    </Box>
  )
}

// Opening the Story UI., or why an app did not open and how to fix it, once a person pressed one.
function AppLineView({ Text }: ElementTable, opening: AppOpeningJson) {
  const line = appLineOf(opening)
  return line ? <Text color={opening.state === 'failed' ? BRAND.error : BRAND.text}>{line}</Text> : null
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

function ButtonsView(elements: ElementTable, { health, view, install, actions }: Band) {
  const { Box, Button } = elements
  const isDisconnected = health.connection === 'disconnected'
  if (!isDisconnected && health.connection !== 'tools-missing') return null
  const canInstall = install.state !== 'running' && install.state !== 'installed'
  return (
    <Box flexDirection="row" gap={1}>
      {view.areDetailsOpen ? <Button key="health-hide" label="Hide" onPress={actions.hideDetails} /> : <Button key="health-details" label="Details" onPress={actions.openDetails} />}
      {canInstall ? <Button key="health-install" label="Run install" onPress={actions.runInstall} /> : null}
      {isDisconnected ? <Button key="health-reconnect" label="Reconnect" variant="primary" onPress={actions.reconnect} /> : null}
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

function ExpandedView(elements: ElementTable, band: Band) {
  const { Box } = elements
  const { health, view, install } = band
  const look = LOOKS[health.connection]
  return (
    <Box
      key="card-health"
      flexDirection="column"
      paddingX={1}
      borderStyle="single"
      borderColor={look.border}
      backgroundColor={look.wash}
      alignSelf="flex-start"
    >
      {HeadlineView(elements, health)}
      {InstallLineView(elements, install)}
      {health.connection === 'connected' ? PartsView(elements, health, band.actions) : null}
      {AppLineView(elements, band.opening)}
      {view.areDetailsOpen && health.connection !== 'connected' ? DetailsView(elements, health, install) : null}
      {ButtonsView(elements, band)}
    </Box>
  )
}

// The band is one icon on the line. It opens no panel of its own: hovering it shows the session card with this panel on
// top, as hovering the session name does, and a press pins the card. hoverScope is the card's hover group.
export function ServerHealthBandView(elements: ElementTable, band: Band, hoverScope: string) {
  const { Box } = elements
  const look = LOOKS[band.health.connection]
  return (
    <Box key="server-health" flexDirection="row" hover={{ scope: hoverScope }}>
      {GlyphButtonView(elements, 'health-icon', look.glyph, look.color, band.actions.toggleCard)}
    </Box>
  )
}

// The panel stacked on top of the session card, as CDR 0001 has hovering the session name show it.
export function ServerHealthPanelView(elements: ElementTable, band: Band) {
  return ExpandedView(elements, band)
}
