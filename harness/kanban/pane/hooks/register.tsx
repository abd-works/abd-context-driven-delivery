import type { EngineInterface, Register } from 'claude-code'

import type { ViewContext } from './kanban/view-context'
import { currentDraft } from './kanban/backlog-item-client'
import {
  currentBoard,
  currentColumnOffset,
  currentSplitLayout,
  haveSurfaceModulesFailed,
  isOnlyActive,
  noteSurfaceModulesFailed,
  refresh,
  select,
  selectedAddress,
  setBoardRows,
} from './kanban/board-client'
import { BandView, PaneView } from './kanban/board-view'
import { currentPanels, reloadReport, setPanelWidth } from './kanban/side-panel-client'
import {
  activateNamed,
  activeTicket,
  closeNamed,
  currentActivation,
  currentOpenCard,
  currentTile,
  fillSatisfy,
  fillShowViolations,
  leaveTile,
  moveNext,
  movePrevious,
  openTile,
  toggleTile,
} from './kanban/ticket-client'

// Connects engine events to the clients and views in ./kanban; the board's rules live in the cdd MCP server.
const PLUGIN = 'cdd-board'
const PANE = 'cdd-board'
const SERVER = 'cdd'
const WIDE_PANE_COLUMNS = 140
const SURFACE_MODULE_SURFACES: string[] = ['terminal', 'desktop']
const SURFACE_WITHOUT_INPUTS = 'mobile'

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
}

type TileAddress = { ticket: string; stage: string; place: string; slugs: string[] }

const isTileAddress = (value: unknown): value is TileAddress => typeof value === 'object' && value !== null && 'place' in value

// What a surface module posts is plain data from code, so only the shapes it sends are believed.
async function answerSurfaceModule($: EngineInterface, data: Record<string, unknown>): Promise<void> {
  const { select: address, boardRows, panel, width, hoverTile, leaveTile: left, pressTile } = data
  if (typeof address === 'string') await select($, address)
  if (typeof boardRows === 'number') await setBoardRows($, boardRows)
  if (typeof panel === 'string' && typeof width === 'number') await setPanelWidth($, panel, width)
  if (isTileAddress(hoverTile)) await openTile($, hoverTile.ticket, hoverTile.stage, hoverTile.place, hoverTile.slugs, false)
  if (typeof left === 'string') await leaveTile($, left)
  if (isTileAddress(pressTile)) await toggleTile($, pressTile.ticket, pressTile.stage, pressTile.place, pressTile.slugs)
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
    return next(e)
  })

  on('command.run', { command: 'board' }, async $ => {
    await $.ui.open({ id: PANE, title: 'Board' })
    await refresh($)
    return { text: 'Board opened.' }
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
    await refresh($)
    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    if (e.tool.startsWith(`mcp__${SERVER}__`)) await refreshAll($)
    return ran
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
    const active = await activeTicket($)
    if (!active || active.violations.length === 0) return next(e)
    return BandView($, $.ui.resolve(e), active, () => fillShowViolations($, active), () => fillSatisfy($, active))
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
      isWide: e.props.bodyColumns >= WIDE_PANE_COLUMNS,
      hasSurfaceModules: SURFACE_MODULE_SURFACES.includes(e.surface) && !(await haveSurfaceModulesFailed($)),
      hasPictures: e.surface !== 'terminal',
      hasInputs: e.surface !== SURFACE_WITHOUT_INPUTS,
      onlyActive: await isOnlyActive($),
      openCard: await currentOpenCard($),
      tile: await currentTile($),
      activation: await currentActivation($),
      draft: await currentDraft($),
      panels: await currentPanels($),
      columnOffset: await currentColumnOffset($),
      layout: await currentSplitLayout($),
    }
    return PaneView($, view, e.props.scroll.bodyRows)
  })
}
