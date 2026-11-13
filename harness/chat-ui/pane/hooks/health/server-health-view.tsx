import type { HealthViewJson, InstallJson, ServerHealthJson } from '../../types'
import type { AppName } from './open-app-client'
import { colourOf, detailsOf, headlineOf, installLineOf, partsOf } from './server-health-wording'
import type { Part } from './server-health-wording'
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
  openApp: (app: AppName) => unknown
}
type Band = {
  health: ServerHealthJson
  view: HealthViewJson
  install: InstallJson
  actions: Actions
}
const LOOKS = {
  connected: { glyph: '✓', color: BRAND.success, wash: BRAND.successWash },
  reconnecting: { glyph: '⟳', color: BRAND.warning, wash: BRAND.raised },
  disconnected: { glyph: '✕', color: BRAND.error, wash: BRAND.errorWash },
  'tools-missing': { glyph: '!', color: BRAND.warning, wash: BRAND.warningWash },
}


// The key of the see-through Button over an app's part, such as health-open-kanban-app.
export const openKeyOf = (app: AppName): string => `health-open-${app.toLowerCase().replace(/ /g, '-')}`

// The desktop draws everything inside a Button in its own colour and padding, so an app's icon and value are drawn as
// Text in the part's colour and a see-through Button as wide as them, laid over them, takes the press.
function OpenAppView({ Box, Button }: ElementTable, part: Part, openApp: Actions['openApp']) {
  if (!part.app) return null
  const app = part.app
  return (
    <Box position="absolute" top={0} left={0}>
      <Button key={openKeyOf(app)} plain label={' '.repeat(`${part.icon} ${part.value}`.length)} onPress={() => openApp(app)} />
    </Box>
  )
}

// The surface has no tooltip, so the part's name is a card revealed while the pointer is over its icon and value. A
// press on the Kanban app or the Graph app opens it, starting it first when it is not running.
function PartsView(elements: ElementTable, health: ServerHealthJson, openApp: Actions['openApp']) {
  const { Box, Text } = elements
  return (
    <Box flexDirection="row" columnGap={3}>
      {partsOf(health).map(part => (
        <Box key={part.label} flexDirection="row" gap={1}>
          <Text color={colourOf(part)}>{part.icon}</Text>
          <Text color={colourOf(part)}>{part.value}</Text>
          <Box position="absolute" top={-1} left={0} paddingX={1} backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
            <Text color={BRAND.text}>{part.label}</Text>
          </Box>
          {OpenAppView(elements, part, openApp)}
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

// Its border is drawn in its own background colour, so the panel has the round corners of the app's cards and no line.
function ExpandedView(elements: ElementTable, band: Band) {
  const { Box } = elements
  const { health, view, install } = band
  const look = LOOKS[health.connection]
  return (
    <Box
      key="card-health"
      flexDirection="column"
      paddingX={1}
      paddingY={1}
      borderStyle="round"
      borderColor={look.wash}
      backgroundColor={look.wash}
    >
      {HeadlineView(elements, health)}
      {InstallLineView(elements, install)}
      {health.connection === 'connected' ? PartsView(elements, health, band.actions.openApp) : null}
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
