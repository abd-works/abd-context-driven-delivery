import type { HealthViewJson, InstallJson, ServerHealthJson } from '../../types'
import { RECONNECT_TRIES, REPORT_TOOL, SERVER, ServerHealthClient } from './server-health-client'
import type { EngineInterface } from 'claude-code'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// The abd.works engineering colours, which hold on either Claude Code theme.
const BRAND = {
  raised: '#1B1B20',
  border: '#2A2A2A',
  text: '#E8E8ED',
  muted: '#9B9BA8',
  success: '#22C55E',
  warning: '#F59E0B',
  error: '#EF4444',
  errorWash: '#2F1414',
}

// Wide enough for an icon and the longest value, `▦ running :5173`; the columns wrap when the band is narrower than five of them.
const PART_WIDTH = 16
const SUCCESS_WASH = '#12261A'
const WARNING_WASH = '#2B2110'

type Part = { icon: string; label: string; value: string; isUp: boolean }
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

const LOOKS = {
  connected: { glyph: '✓', color: BRAND.success, wash: SUCCESS_WASH, border: BRAND.success },
  reconnecting: { glyph: '⟳', color: BRAND.warning, wash: BRAND.raised, border: BRAND.border },
  disconnected: { glyph: '✕', color: BRAND.error, wash: BRAND.errorWash, border: BRAND.error },
  'tools-missing': { glyph: '!', color: BRAND.warning, wash: WARNING_WASH, border: BRAND.warning },
}

const colourOf = (part: Part): string => (part.isUp ? BRAND.success : BRAND.muted)

const runningOn =(port: number | null): string => (port === null ? 'not running' : `running :${port}`)

function partsOf({ report, toolCount }: ServerHealthJson): Part[] {
  const { kanbanAppPort, graphAppPort, isHookServerRunning: isHookRunning } = new ServerHealthClient(report)
  return [
    { icon: '⬢', label: 'MCP host', value: 'running', isUp: true },
    { icon: '⚒', label: 'Tools', value: `${toolCount} loaded`, isUp: true },
    { icon: '▦', label: 'Kanban app', value: runningOn(kanbanAppPort), isUp: kanbanAppPort !== null },
    { icon: '◈', label: 'Graph app', value: runningOn(graphAppPort), isUp: graphAppPort !== null },
    { icon: '↪', label: 'Hook server', value: isHookRunning ? 'running' : 'not installed', isUp: isHookRunning },
  ]
}

function headlineOf({ connection, attempt, toolCount }: ServerHealthJson): { title: string; detail: string } {
  if (connection === 'connected') return { title: '', detail: '' }
  if (connection === 'disconnected') return { title: 'Disconnected', detail: `${SERVER} stopped.` }
  if (connection === 'tools-missing') return { title: 'Tools missing', detail: `${toolCount} loaded, ${REPORT_TOOL} is not one of them.` }
  if (attempt === 0) return { title: 'Connecting', detail: `Waiting for ${SERVER} to answer.` }
  return { title: 'Reconnecting', detail: `Waiting for ${SERVER} to answer. Try ${attempt} of ${RECONNECT_TRIES}.` }
}

function detailsOf({ connection, problem }: ServerHealthJson, install: InstallJson): [string, string][] {
  const fix = connection === 'tools-missing' ? 'Press Run install, then open a new session.' : 'Press Reconnect. If that fails, press Run install.'
  return [
    ['tool', REPORT_TOOL],
    ['error', install.error ?? problem ?? ''],
    ['server', SERVER],
    ['fix', fix],
  ]
}

function installLineOf({ state }: InstallJson): string {
  if (state === 'running') return 'Installing.'
  if (state === 'installed') return 'Installed. Open a new session to pick it up.'
  return state === 'failed' ? 'Install failed. See the error in Details.' : ''
}

// The surface has no tooltip, so the part's name is a card revealed while the pointer is over its icon and value.
function PartsView({ Box, Text }: ElementTable, health: ServerHealthJson) {
  return (
    <Box flexDirection="row" flexWrap="wrap" columnGap={2}>
      {partsOf(health).map(part => (
        <Box key={part.label} flexDirection="row" gap={1} width={PART_WIDTH}>
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

function ButtonsView(elements: ElementTable, { health, view, install, actions }: Band) {
  const { Box, Button } = elements
  const isDisconnected = health.connection === 'disconnected'
  if (!isDisconnected && health.connection !== 'tools-missing') return null
  const canInstall = install.state !== 'running' && install.state !== 'installed'
  return (
    <Box flexDirection="row" gap={1}>
      {view.areDetailsOpen ? <Button key="health-hide" label="Hide" onPress={actions.hideDetails} /> : <Button key="health-details" label="Details" onPress={actions.openDetails} />}
      {canInstall && (view.areDetailsOpen || !isDisconnected) ? <Button key="health-install" label="Run install" onPress={actions.runInstall} /> : null}
      {isDisconnected ? <Button key="health-reconnect" label="Reconnect" variant="primary" onPress={actions.reconnect} /> : null}
    </Box>
  )
}

function ExpandedView(elements: ElementTable, band: Band) {
  const { Box, Text } = elements
  const { health, view, install } = band
  const look = LOOKS[health.connection]
  const { title, detail } = headlineOf(health)
  const installLine = installLineOf(install)
  return (
    <Box
      flexDirection="column"
      paddingX={1}
      borderStyle="single"
      borderColor={look.border}
      backgroundColor={look.wash}
      {...(view.isPinned ? {} : { display: 'none' as const, hover: { display: 'flex' as const } })}
    >
      {title ? (
        <Box flexDirection="row" gap={1}>
          <Text weight="semibold" color={look.color}>{title}</Text>
          {detail ? <Text color={BRAND.text}>{detail}</Text> : null}
        </Box>
      ) : null}
      {installLine ? <Text color={BRAND.text}>{installLine}</Text> : null}
      {health.connection === 'connected' ? PartsView(elements, health) : null}
      {view.areDetailsOpen ? DetailsView(elements, health, install) : null}
      {ButtonsView(elements, band)}
    </Box>
  )
}

// The band is one icon until the pointer is over it or a click pins it, so it stays out of the way. The icon
// sits beside what it expands, so the pointer stays on it as the panel opens.
export function ServerHealthBandView(elements: ElementTable, band: Band) {
  const { Box, Button, Text } = elements
  const look = LOOKS[band.health.connection]
  return (
    <Box key="server-health" flexDirection="row" gap={1}>
      {ExpandedView(elements, band)}
      <Button key="health-icon" plain label={look.glyph} onPress={band.actions.togglePin}>
        <Text color={look.color}>{look.glyph}</Text>
      </Button>
    </Box>
  )
}
