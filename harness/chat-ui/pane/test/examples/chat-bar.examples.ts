// The examples the chat bar's story tests share.
//
// Seed: state the cdd server owns, the TicketData and BoardData the Python Ticket and Board would report. A Given sets
// it on the stubbed server (cdd-stub.ts), never on the pane.
// Interaction: what a person types into the chat bar or reads from it, such as a new session's name.
import type { BoardData, ColumnData, FidelityGuidanceData, PracticeGuidanceData, StageScopeData } from '@cdd/space/kanban/board'
import type { ActionStatesData, FidelityProgressData } from '@cdd/space/kanban/fidelity-progress'
import type { TicketData } from '@cdd/space/kanban/ticket'
import type { PracticeSessionOutputData } from '@cdd/space/session/practice-session-output'
import type { SessionData } from '@cdd/space/session/session'

// Seed: server-health.report while every part runs.
export const HEALTHY = { kanban_app_port: 8778, graph_app_port: 5173, is_hook_server_running: false }

// Seed: each stage's fidelities, in the order the board's columns name them.
export const DISCOVERY = ['stories-story-map', 'ddd-bounded-context', 'ux-ia', 'clean-engineering-modules', 'bdd-behavior']
export const SPECIFICATION = ['stories-scenarios', 'ddd-model', 'ux-mockup', 'clean-engineering-model', 'bdd-realization']
export const IMPLEMENTATION = ['stories-acceptance-tests', 'ddd-tactics', 'ux-front-end-code', 'clean-engineering-code', 'bdd-development']
export const WORK_OF: Record<string, string[]> = { Discovery: DISCOVERY, Specification: SPECIFICATION, Implementation: IMPLEMENTATION }
export const STAGE_ORDER = ['Discovery', 'Specification', 'Implementation', 'Complete']
const NOT_DONE: ActionStatesData = { generate: 'to_do', validate: 'to_do', review: 'to_do' }
const STEPS: (keyof ActionStatesData)[] = ['generate', 'validate', 'review']
const EVERY_FIDELITY = [...DISCOVERY, ...SPECIFICATION, ...IMPLEMENTATION]
const PRACTICES = ['stories', 'ddd', 'ux', 'clean_engineering', 'bdd']
const ROOTS: Record<string, string> = { stories: 'harness/chat-ui/.context', ux: 'harness/chat-ui/design', clean_engineering: 'harness/chat-ui/pane' }

// Seed: the practice whose slug starts a fidelity's slug, such as clean_engineering for clean-engineering-model.
const practiceOf = (slug: string): string => PRACTICES.find(practice => slug.startsWith(`${practice.replace('_', '-')}-`)) ?? ''
// Seed: each practice as Board.practices reports it; a fidelity's slug begins with its practice's slug.
const SHORT_NAMES: Record<string, [string, string]> = { stories: ['Stories', '#6BCB77'], ddd: ['DDD', '#6C5CE7'], ux: ['UX', '#E84393'], clean_engineering: ['CE', '#4FC3F7'], bdd: ['BDD', '#00B894'] }
// The chat bar shows no guidance text, so the seed sends none.
const NO_TEXT = { overview: '', guidance: '', rules: [] }
const practiceData = (key: string): PracticeGuidanceData => ({ key, slug: key.replace('_', '-'), short_name: SHORT_NAMES[key][0], colour: SHORT_NAMES[key][1], fidelities: EVERY_FIDELITY.filter(slug => practiceOf(slug) === key), ...NO_TEXT })
// Seed: the stage that requires a fidelity.
const stageOf = (slug: string): string => STAGE_ORDER.find(stage => (WORK_OF[stage] ?? []).includes(slug)) ?? ''
// Seed: the fidelities this project writes in TypeScript by default; every other writes markdown.
const TYPESCRIPT_FIRST = ['stories-scenarios', 'clean-engineering-model']

// Seed: one fidelity as FidelityGuidance reports it: its name after its practice's slug, and its default format.
export function fidelityOf(slug: string): FidelityGuidanceData {
  const name = slug.slice(practiceOf(slug).length + 1).replace(/-/g, '_')
  const defaultFormat = TYPESCRIPT_FIRST.includes(slug) ? 'typescript' : 'markdown'
  return { name, outputs: { [defaultFormat]: `.context/${name}` }, default_format: defaultFormat, slug, ...NO_TEXT }
}

// Seed: one fidelity's progress as the Python FidelityProgress reports it, on a practice the session has turned on or
// off. Its next action is review while it has violations, else the first of generate, validate and review not done,
// nothing once it is done.
export function progressOf(ticket: string, slug: string, state = 'not_started', actions: ActionStatesData = NOT_DONE, violations = 0): FidelityProgressData {
  const nextAction = state === 'violations' ? 'review' : (STEPS.find(step => actions[step] !== 'done') ?? '')
  const practice = practiceOf(slug)
  return {
    ticket: { name: ticket },
    fidelity: fidelityOf(slug),
    stage: { name: stageOf(slug) },
    practice: { key: practice },
    is_enabled: practice in ROOTS,
    next_action: nextAction,
    commands: Object.fromEntries(STAGE_ACTIONS.map(action => [action, `/actions-${action} ${slug} session=${sessionFileOf(ticket)}`])),
    allowed_actions: [],
    has_violations: state === 'violations',
    state,
    actions,
    report_file: '',
    violation_count: violations,
  }
}

// Seed: a ticket's session.json as a path from the project, which every command a ticket's progress gives names.
const sessionFileOf = (ticket: string): string => `.sessions/${ticket}/session.json`

// Seed: a ticket's session with the practices Stories, UX and Clean Engineering turned on, each on its chosen root.
function sessionOf(name: string, title: string): SessionData {
  const sessionFile = sessionFileOf(name)
  const practiceData = (practice: string): PracticeSessionOutputData => ({ name: practice, session_file: sessionFile, enabled: practice in ROOTS, root: ROOTS[practice] ?? '', is_root_chosen: practice in ROOTS })
  return { name, session_file: sessionFile, workpath: '', handoff: '', title, scope: '', parent: '', practices: Object.fromEntries(PRACTICES.map(practice => [practice, practiceData(practice)])) }
}

// Seed: what a story says about a ticket: its name and title, the stage it is in, the slug of its next fidelity (none
// once its stage is done), and whether it is done in its stage.
export type TicketSeed = { name?: string; title?: string; column?: string; next?: string | null; is_done?: boolean }

// Seed: checkout-flow, In progress in Specification with the practices Stories, UX and Clean Engineering, nothing yet done.
export function checkoutFlow(seed: TicketSeed = {}): TicketData {
  const name = seed.name ?? 'checkout-flow'
  const title = seed.title ?? 'Checkout flow'
  const next = seed.next === undefined ? 'stories-scenarios' : seed.next
  return {
    title,
    last_activity: '2026-11-05T06:00:00Z',
    name,
    session: sessionOf(name, title),
    progress: EVERY_FIDELITY.map(slug => progressOf(name, slug)),
    column: { name: seed.column ?? 'Specification' },
    is_closed: false,
    is_active: false,
    drop_targets: ['Backlog'],
    is_done: seed.is_done ?? false,
    next: next ? { ticket: { name }, fidelity: { slug: next } } : null,
    agent_context: `CDD session board: you are working on ticket ${name} ("${title}"), in ${seed.column ?? 'Specification'}.`,
    leave_choices: ['handoff', 'commit', 'push', 'merge'],
    first_leave_choices: ['handoff', 'commit', 'push'],
    open_choices: ['branch', 'worktree'],
    worktree: '',
    working_chat: null,
    stage_work: [],
  }
}

type FidelityState = { progress: string; actions?: Partial<ActionStatesData>; violations?: number }
export const GENERATED: FidelityState = { progress: 'in_progress', actions: { generate: 'done' } }
export const VALIDATED: FidelityState = { progress: 'in_progress', actions: { generate: 'done', validate: 'done' } }
export const DONE: FidelityState = { progress: 'done', actions: { generate: 'done', validate: 'done', review: 'done' } }

// Seed: checkout-flow with these fidelities' progress, actions and violation counts as the Python Ticket would report them.
export function checkoutFlowWith(fidelities: Record<string, FidelityState>, seed: TicketSeed = {}): TicketData {
  const plain = checkoutFlow(seed)
  const changedOf = (progress: FidelityProgressData): FidelityProgressData => {
    const state = fidelities[progress.fidelity.slug]
    return state ? progressOf(plain.name, progress.fidelity.slug, state.progress, { ...NOT_DONE, ...state.actions }, state.violations ?? 0) : progress
  }
  return { ...plain, progress: plain.progress.map(changedOf) }
}

// Seed: checkout-flow In progress in Discovery with all five practices turned on, every one writing under harness, as
// a session on the whole repository chooses them.
export function checkoutFlowOnOneFolder(folder = 'harness'): TicketData {
  const plain = checkoutFlow({ column: 'Discovery', next: 'stories-story-map' })
  const practices = Object.fromEntries(Object.entries(plain.session.practices).map(([key, practice]) => [key, { ...practice, enabled: true, root: folder, is_root_chosen: true }]))
  return { ...plain, session: { ...plain.session, practices }, progress: plain.progress.map(progress => ({ ...progress, is_enabled: true })) }
}

// Seed: payment-retry, In progress in Discovery.
export function paymentRetry(): TicketData {
  return checkoutFlow({ title: 'Payment retry', name: 'payment-retry', column: 'Discovery', next: 'stories-story-map' })
}

// Seed: what every stage reports beside its fidelities, as ApproachStage does: its scope and the actions run on a fidelity.
const STAGE_ACTIONS = ['generate', 'validate', 'review', 'iterate', 'sketch', 'render', 'document']
const SCOPES: Record<string, StageScopeData> = {
  Discovery: { shape: 'solution', name: 'Whole solution', reach: 'wide / shallow', covers: 'outcomes · scope · boundaries' },
  Specification: { shape: 'sprint', name: 'Sprint', reach: 'narrow / deeper', covers: 'behaviour · design · logic' },
  Implementation: { shape: 'story', name: 'Story', reach: 'narrowest / deep', covers: 'tests · code · interface' },
}

const column = (name: string, tickets: TicketData[]): ColumnData => {
  const work = WORK_OF[name] ?? []
  const stage = work.length
    ? { scope: SCOPES[name], actions: STAGE_ACTIONS, producing_actions: STAGE_ACTIONS.filter(action => action !== 'validate' && action !== 'review'), actions_with_formats: ['generate', 'render'], work_required: work.map(fidelityOf) }
    : {}
  return { name, kind: work.length ? 'stage' : 'complete', in_progress: tickets.filter(ticket => ticket.column.name === name), ...stage }
}

// Seed: the board as board.show returns it, each ticket in the column it names, the tickets in a stage named as open in
// column order, and the active one named.
export function boardOf(active: string | null, ...tickets: TicketData[]): BoardData {
  const activeTicket = tickets.some(ticket => ticket.name === active) ? { name: active! } : null
  const openTickets = STAGE_ORDER.filter(name => name in WORK_OF).flatMap(name => tickets.filter(ticket => ticket.column.name === name).map(ticket => ({ name: ticket.name })))
  return { project: 'abd-context-driven-delivery', practices: PRACTICES.map(practiceData), open_tickets: openTickets, active: activeTicket, columns: [{ name: 'Backlog', kind: 'backlog', items: [] }, ...STAGE_ORDER.map(name => column(name, tickets))], format_groups: [] }
}

// Interaction: the name a person types in the session list's field.
export const NEW_SESSION_NAME = 'payment-retry'

// Seed: the TypeScript files clean-engineering-model declares in checkout-flow's session, as FidelityProgress.files
// lists them by format.
export const MODEL_FILES = { typescript: [{ path: 'pane/hooks/chat-bar/chat-bar-client.ts', exists: true }, { path: 'pane/hooks/chat-bar/fidelity-progress-client.ts', exists: true }] }

// Seed: clean-engineering-model declares its class diagram beside the model's markdown.
export const MODEL_DIAGRAM_FILES = { markdown: [{ path: 'pane/.context/chat-bar-model.md', exists: true }], drawio: [{ path: 'pane/.context/chat-bar-model.drawio', exists: true }] }

// Seed: the text of chat-bar-client.ts under checkout-flow's Clean Engineering root.
export const CHAT_BAR_CLIENT_TEXT = { 'pane/hooks/chat-bar/chat-bar-client.ts': '// Model shell for the chat bar\nexport class ChatBarClient {}' }

// Seed: clean-engineering-model's latest validation report, failing no-legacy-api-after-refactor.
export const MODEL_REPORT = {
  path: '.sessions/checkout-flow/validation-reports/clean-engineering-model.md',
  text: '# Validation\n\n## no-legacy-api-after-refactor\n\nFail',
  rules: [],
  has_saved_graph: false,
  violation_count: 1,
  is_out_of_date: false,
}
