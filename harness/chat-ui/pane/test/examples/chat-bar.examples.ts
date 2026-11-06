// The examples the chat bar's story tests share.
//
// Seed: state the cdd server owns, the TicketData and BoardData the Python Ticket and Board would report. A Given sets
// it on the stubbed server (cdd-stub.ts), never on the pane.
// Interaction: what a person types into the chat bar or reads from it, such as a new session's name.
import type { BoardData, ColumnData } from '@cdd/harness/kanban/board'
import type { ActionStatesData, FidelityProgressData } from '@cdd/harness/kanban/fidelity-progress'
import type { SessionData, TicketData } from '@cdd/harness/kanban/ticket'
import type { PracticeSessionOutputData } from '@cdd/space/session/practice-session-output'

// Seed: server-health.report while every part runs.
export const HEALTHY = { kanban_app_port: 8778, graph_app_port: 5173, is_hook_server_running: false }

// Seed: each stage's fidelities, in the order the board's columns name them.
export const DISCOVERY = ['stories-story_map', 'ddd-bounded_context', 'ux-ia', 'clean_engineering-modules', 'bdd-behavior']
export const SPECIFICATION = ['stories-scenarios', 'ddd-model', 'ux-mockup', 'clean_engineering-model', 'bdd-realization']
export const IMPLEMENTATION = ['stories-acceptance_tests', 'ddd-tactics', 'ux-front_end_code', 'clean_engineering-code', 'bdd-development']
export const WORK_OF: Record<string, string[]> = { Discovery: DISCOVERY, Specification: SPECIFICATION, Implementation: IMPLEMENTATION }
export const STAGE_ORDER = ['Discovery', 'Specification', 'Implementation', 'Complete']
const NOT_DONE: ActionStatesData = { generate: 'to_do', validate: 'to_do', review: 'to_do' }
const STEPS: (keyof ActionStatesData)[] = ['generate', 'validate', 'review']
const EVERY_FIDELITY = [...DISCOVERY, ...SPECIFICATION, ...IMPLEMENTATION]
const PRACTICES = ['stories', 'ddd', 'ux', 'clean_engineering', 'bdd']
const ROOTS: Record<string, string> = { stories: 'harness/chat-ui/.context', ux: 'harness/chat-ui/design', clean_engineering: 'harness/chat-ui/pane' }

const practiceOf = (slug: string): string => slug.slice(0, slug.indexOf('-'))

// Seed: one fidelity's progress as the Python FidelityProgress reports it. Its next action is satisfy while it has
// violations, else the first of generate, validate and review not done, nothing once it is done.
export function progressOf(ticket: string, slug: string, state = 'not_started', actions: ActionStatesData = NOT_DONE, violations = 0): FidelityProgressData {
  const nextAction = state === 'violations' ? 'satisfy' : (STEPS.find(step => actions[step] !== 'done') ?? '')
  return { ticket, slug, practice: practiceOf(slug), is_enabled: true, next_action: nextAction, allowed_actions: [], state, actions, report_file: '', violation_count: violations }
}

// Seed: a ticket's session with the practices Stories, UX and Clean Engineering turned on, each on its chosen root.
function sessionOf(name: string, title: string): SessionData {
  const sessionFile = `.sessions/${name}/session.json`
  const practiceData = (practice: string): PracticeSessionOutputData => ({ name: practice, session_file: sessionFile, enabled: practice in ROOTS, root: ROOTS[practice] ?? '', is_root_chosen: practice in ROOTS })
  return { name, session_file: sessionFile, workpath: '', handoff: '', title, scope: '', parent: '', practices: Object.fromEntries(PRACTICES.map(practice => [practice, practiceData(practice)])) }
}

// Seed: checkout-flow, In progress in Specification with the practices Stories, UX and Clean Engineering, nothing yet done.
export function checkoutFlow(overrides: Partial<TicketData> = {}): TicketData {
  const name = overrides.name ?? 'checkout-flow'
  const title = overrides.title ?? 'Checkout flow'
  return {
    title,
    last_activity: '2026-11-05T06:00:00Z',
    name,
    session: sessionOf(name, title),
    progress: Object.fromEntries(EVERY_FIDELITY.map(slug => [slug, progressOf(name, slug)])),
    column: 'Specification',
    is_done: false,
    next: 'stories-scenarios',
    worktree: '',
    ...overrides,
  }
}

type FidelityState = { progress: string; actions?: Partial<ActionStatesData>; violations?: number }
export const GENERATED: FidelityState = { progress: 'in_progress', actions: { generate: 'done' } }
export const VALIDATED: FidelityState = { progress: 'in_progress', actions: { generate: 'done', validate: 'done' } }
export const DONE: FidelityState = { progress: 'done', actions: { generate: 'done', validate: 'done', review: 'done' } }

// Seed: checkout-flow with these fidelities' progress, actions and violation counts as the Python Ticket would report them.
export function checkoutFlowWith(fidelities: Record<string, FidelityState>, overrides: Partial<TicketData> = {}): TicketData {
  const plain = checkoutFlow(overrides)
  const changed = Object.entries(fidelities).map(([slug, state]) => [slug, progressOf(plain.name, slug, state.progress, { ...NOT_DONE, ...state.actions }, state.violations ?? 0)])
  return { ...plain, progress: { ...plain.progress, ...Object.fromEntries(changed) } }
}

// Seed: payment-retry, In progress in Discovery.
export function paymentRetry(): TicketData {
  return checkoutFlow({ title: 'Payment retry', name: 'payment-retry', column: 'Discovery', next: 'stories-story_map' })
}

const column = (name: string, tickets: TicketData[]): ColumnData => {
  const work = WORK_OF[name] ?? []
  return {
    name,
    in_progress: tickets.filter(ticket => ticket.column === name),
    ...(work.length ? { work_required: work, default_formats: { 'stories-scenarios': 'typescript', 'clean_engineering-model': 'typescript' } } : {}),
  }
}

// Seed: the board as board.show returns it, each ticket in the column it names.
export function boardOf(active: string | null, ...tickets: TicketData[]): BoardData {
  return { project: 'abd-context-driven-delivery', active, columns: [{ name: 'Backlog', items: [] }, ...STAGE_ORDER.map(name => column(name, tickets))] }
}

// Interaction: the name a person types in the session list's field.
export const NEW_SESSION_NAME = 'payment-retry'
