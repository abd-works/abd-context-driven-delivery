import type { PromptStep, StepState } from '../../types'

/** One item of the desktop app's task list as `update_plan` sends it. */
type PlanItem = { content?: unknown; status?: unknown }

/** What one `update_plan` call says: the whole list, or a move along the list already set. */
export type PlanCall = { items?: unknown; advance?: unknown; done?: unknown; start?: unknown }

/** The tool the desktop app's task list is set and advanced with, under whatever server name the app gives it. */
export const PLAN_TOOL = /^mcp__.*__update_plan$/
/** The tool that closes a turn's task list: every step it held is finished. */
export const WRAP_UP_TOOL = /^mcp__.*__wrap_up$/
/** The cdd server's tool the agent gives a queued prompt its steps with, which names the prompt it takes. */
export const SET_STEPS_TOOL = /^mcp__.*__prompt-queue_set_steps$/

/** Every prompt-queue tool, whose answer is the queue as the server now holds it. */
export const PROMPT_QUEUE_TOOL = /^mcp__.*__prompt-queue_/

/** The agent's steps after one `update_plan` call: a call with items replaces the list; advance finishes the step being
 * worked and starts the next pending one; done finishes the steps it numbers, from 1; start works the step it numbers. */
export function nextPlan(steps: PromptStep[], call: PlanCall): PromptStep[] {
  if (Array.isArray(call.items)) {
    return (call.items as PlanItem[]).map(item => ({ text: String(item.content ?? '').trim(), state: stateOf(item.status) }))
  }
  let next = steps.map(step => ({ ...step }))
  if (call.advance === true) {
    next = advanced(next)
  }
  for (const number of Array.isArray(call.done) ? call.done : []) {
    next = withState(next, Number(number), 'done')
  }
  if (typeof call.start === 'number') {
    next = withState(next.map(step => (step.state === 'in_progress' ? { ...step, state: 'pending' } : step)), call.start, 'in_progress')
  }
  return next
}

/** Every step finished, as a wrapped-up turn leaves its task list. */
export function finishedPlan(steps: PromptStep[]): PromptStep[] {
  return steps.map(step => ({ ...step, state: 'done' }))
}

/** How many of the steps are done, as a card shows it: `1/3`; nothing for a prompt with no steps. */
export function progressOf(steps: PromptStep[] | undefined): string {
  return steps && steps.length > 0 ? `${steps.filter(step => step.state === 'done').length}/${steps.length}` : ''
}

function advanced(steps: PromptStep[]): PromptStep[] {
  const working = steps.findIndex(step => step.state === 'in_progress')
  const finished = working < 0 ? steps : withState(steps, working + 1, 'done')
  const pending = finished.findIndex(step => step.state === 'pending')
  return pending < 0 ? finished : withState(finished, pending + 1, 'in_progress')
}

function withState(steps: PromptStep[], number: number, state: StepState): PromptStep[] {
  return steps.map((step, index) => (index + 1 === number ? { ...step, state } : step))
}

function stateOf(status: unknown): StepState {
  if (status === 'completed' || status === 'done') {
    return 'done'
  }
  return status === 'in_progress' ? 'in_progress' : 'pending'
}
