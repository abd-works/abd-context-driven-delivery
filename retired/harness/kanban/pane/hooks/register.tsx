import type { EngineInterface, Register } from 'claude-code'

import type { ViewContext } from './kanban/view-context'
import { currentDraft } from './kanban/backlog-item-client'
import {
  arePracticesHidden,
  currentBoard,
  currentColumnOffset,
  currentEditingLimit,
  currentRegionOffsets,
  currentServerFailure,
  currentSplitLayout,
  haveSurfaceModulesFailed,
  isOnlyActive,
  noteSurfaceModulesFailed,
  refresh,
  select,
  selectedAddress,
  setBoardRows,
  scrollRegion,
  setColumnOffset,
} from './kanban/board-client'
import { BandView, PaneView } from './kanban/board-view'
import {
  currentHealthView,
  currentInstall,
  currentServerHealth,
  hideDetails,
  openDetails,
  reconnect,
  refreshHealth,
  refreshHealthSoon,
  runInstall,
  togglePin,
} from './health/server-health-client'
import { ServerHealthBandView } from './health/server-health-view'
import { currentPanels, reloadFiles, reloadFileText, reloadReport, setPanelWidth } from './kanban/side-panel-client'
import {
  activateNamed,
  activeTicket,
  closeNamed,
  currentActivation,
  currentCardOffset,
  currentOpenCard,
  currentTile,
  fillSatisfy,
  fillShowViolations,
  hoverTile,
  leaveTile,
  moveNext,
  movePrevious,
  reloadTile,
  scrollCard,
  toggleTile,
} from './kanban/ticket-client'

// Connects engine events to the clients and views in ./kanban; the board's rules live in the cdd MCP server.
const PLUGIN = 'cdd-board'
const PANE = 'cdd-board'
const SERVER = 'cdd'
const SURFACE_MODULE_SURFACES: string[] = ['terminal', 'desktop']
const SURFACE_WITHOUT_INPUTS = 'mobile'
const SURFACE_WITHOUT_PICTURES = 'terminal'

const TICKET_VERBS = ['next', 'previous', 'close', 'activate']

async function runTicketCommand($: EngineInterface, verb: string, ticket: string): Promise<void> {
  if (verb === 'next') await moveNext($, ticket)
  if (verb === 'previous') await movePrevious($, ticket)
  if (verb === 'close') await closeNamed($, ticket)
  if (verb === 'activate') await activateNamed($, ticket)
}

async function refreshAll($: EngineInterface): Promise<void> {
  await refresh($)
  await reloadReport($)
  await reloadTile($)
  await reloadFiles($)
  await reloadFileText($)
}

type TileAddress = { ticket: string; stage: string; place: string; slugs: string[]; menuSlugs?: string[] }

const isTileAddress = (value: unknown): value is TileAddress => typeof value === 'object' && value !== null && 'place' in value

// What a surface module posts is plain data from code, so only the shapes it sends are believed.
async function answerSurfaceModule($: EngineInterface, data: Record<string, unknown>): Promise<void> {
  const { select: address, boardRows, columnOffset, panel, width, hoverTile: hovered, leaveTile: left, pressTile } = data
  if (typeof address === 'string') await select($, address)
  if (typeof boardRows === 'number') await setBoardRows($, boardRows)
  if (typeof columnOffset === 'number') await setColumnOffset($, columnOffset)
  if (typeof panel === 'string' && typeof width === 'number') await setPanelWidth($, panel, width)
  if (isTileAddress(hovered)) await hoverTile($, hovered.ticket, hovered.stage, hovered.place, hovered.slugs)
  if (typeof left === 'string') await leaveTile($, left)
  if (isTileAddress(pressTile)) await toggleTile($, pressTile.ticket, pressTile.stage, pressTile.place, pressTile.slugs, pressTile.menuSlugs)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'board', description: 'Show the CDD session board beside the chat' })
    await $.command.register({
      name: 'ticket',
      description: 'Move a ticket on the CDD session board',
      argumentHint: 'next|previous|close|activate <ticket>',
    })
    void $.ui.open({ id: PANE, title: 'Board' })
    await refresh($)
    refreshHealthSoon($)
    return next(e)
  })

  on('command.run', { command: 'board' }, async $ => {
    const opened = await $.ui.open({ id: PANE, title: 'Board' })
    await refresh($)
    return { text: opened.isPlaced ? 'Board opened.' : `Board not drawn: ${opened.reason}` }
  })

  on('command.run', { command: 'ticket' }, async ($, e) => {
    const [verb = '', ticket] = e.args.trim().split(/\s+/)
    if (!TICKET_VERBS.includes(verb) || !ticket) return { text: 'Usage: /ticket next|previous|close|activate <ticket>' }
    await runTicketCommand($, verb, ticket)
    return { text: `${verb} ${ticket}` }
  })

  on('ui.message', async ($, e, next) => {
    await answerSurfaceModule($, e.data as Record<string, unknown>)
    return next(e)
  })

  // A surface that cannot run a surface module still gets the board, with Buttons in place of them.
  on('ui.fault', async ($, e, next) => {
    await noteSurfaceModulesFailed($)
    return next(e)
  })

  // The cdd server can still be connecting at session start; by the first prompt it answers.
  on('prompt.submit', async ($, e, next) => {
    await Promise.all([refresh($), refreshHealth($)])
    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    if (e.tool.startsWith(`mcp__${SERVER}__`)) await Promise.all([refreshAll($), refreshHealth($)])
    return ran
  })

  // A skill writes its files after its cdd tool call, so what the tiles and panels show is read again as its turn ends.
  on('turn.complete', async ($, e, next) => {
    await refreshAll($)
    return next(e)
  })

  on('prompt.compose', async ($, e, next) => {
    const composed = await next(e)
    // The first prompt is composed before the first prompt.submit; read the board here if it is still empty.
    if (!(await currentBoard($))) await refresh($)
    const active = await activeTicket($)
    if (!active) return composed
    const text =
      `CDD session board: you are working on ticket ${active.name} ("${active.title}"), in ${active.column}. ` +
      (active.next ? `Its next guidance is ${active.next}. ` : 'Its stage is done and waits for a person to move it. ') +
      'Each fidelity goes through generate, validate, then /review by a person.'
    return { sections: [...composed.sections, { id: `${PLUGIN}:ticket`, text, scope: 'session' as const }] }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)
    const active = await activeTicket($)
    const elements = $.ui.resolve(e)
    const violations = active && active.violations.length > 0 ? BandView($, elements, e.surface !== SURFACE_WITHOUT_PICTURES, active, () => fillShowViolations($, active), () => fillSatisfy($, active)) : null
    const actions = {
      togglePin: () => togglePin($),
      openDetails: () => openDetails($),
      hideDetails: () => hideDetails($),
      reconnect: () => reconnect($, () => refreshAll($)),
      runInstall: () => runInstall($),
    }
    const band = {
      health: await currentServerHealth($),
      view: await currentHealthView($),
      install: await currentInstall($),
      hasPictures: e.surface !== SURFACE_WITHOUT_PICTURES,
      columns: e.props.bodyColumns,
      actions,
    }
    return ServerHealthBandView(elements, band, violations)
  })

  // A region clips its rows, so the engine's window cannot reach them: the pane moves them itself. With a panel beside
  // it, the tree is as tall as it needs and the engine's window moves it.
  on('ui.scroll', { requestId: PANE }, async ($, e, next) => {
    if (await scrollCard($, e.by, e.bodyRows)) return {}
    if ((await currentPanels($)).length) return next(e)
    await scrollRegion($, e.pointer?.row ?? 0, e.by, e.bodyRows)
    return {}
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const elements = $.ui.resolve(e)
    const { Text } = elements
    const board = await currentBoard($)
    if (!board) return <Text dimColor>No board yet: is the cdd MCP server connected?</Text>
    const view: ViewContext = {
      elements,
      board,
      address: await selectedAddress($),
      now: await $.clock.now(),
      bodyColumns: e.props.bodyColumns,
      bodyRows: e.props.scroll.bodyRows,
      hasSurfaceModules: SURFACE_MODULE_SURFACES.includes(e.surface) && !(await haveSurfaceModulesFailed($)),
      hasPictures: e.surface !== SURFACE_WITHOUT_PICTURES,
      hasInputs: e.surface !== SURFACE_WITHOUT_INPUTS,
      onlyActive: await isOnlyActive($),
      openCard: await currentOpenCard($),
      tile: await currentTile($),
      activation: await currentActivation($),
      draft: await currentDraft($),
      panels: await currentPanels($),
      columnOffset: await currentColumnOffset($),
      editingLimit: await currentEditingLimit($),
      hidesDisabled: await arePracticesHidden($),
      serverFailure: await currentServerFailure($),
      cardOffset: await currentCardOffset($),
      layout: await currentSplitLayout($),
      regionOffsets: await currentRegionOffsets($),
    }
    return PaneView($, view)
  })
}
