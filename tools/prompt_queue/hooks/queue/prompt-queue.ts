import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { QueuedPrompt, SubAgentTask } from '../../types'
import { PromptQueue, listedItems, parseJsonArray, slashCommandOf } from './queue-order'

const GROUPING_MODEL = 'sonnet'
const GROUPING_TOKENS = 4096

const prompts = atom({ plugin: 'prompt-queue', key: 'prompts' } as const, [] as QueuedPrompt[])
const isExpanded = atom({ plugin: 'prompt-queue', key: 'isExpanded' } as const, false)
const isSubAgentMode = atom({ plugin: 'prompt-queue', key: 'isSubAgentMode' } as const, false)
const tasks = atom({ plugin: 'prompt-queue', key: 'tasks' } as const, [] as SubAgentTask[])
const notice = atom({ plugin: 'prompt-queue', key: 'notice' } as const, '')
/** Playing, each finished turn sends the next prompt; paused, the queue waits. */
const isPlaying = atom({ plugin: 'prompt-queue', key: 'isPlaying' } as const, false)
/** Whether the main chat is in a turn, so play sends at once only when nothing is running. */
const isTurnRunning = atom({ plugin: 'prompt-queue', key: 'isTurnRunning' } as const, false)
/** The draft Alt+Enter just queued: the desktop still submits it after the key, so that submission is dropped. */
const queuedByKey = atom({ plugin: 'prompt-queue', key: 'queuedByKey' } as const, '')
/** The prompt being edited in the prompt box: it keeps its place, shaded, and the next add puts the draft back there. */
const editingId = atom({ plugin: 'prompt-queue', key: 'editingId' } as const, '')

export type QueueState = {
  queue: PromptQueue
  isExpanded: boolean
  isSubAgentMode: boolean
  isPlaying: boolean
  editingId: string
  tasks: SubAgentTask[]
  notice: string
}

export async function currentQueue($: EngineInterface): Promise<QueueState> {
  return {
    queue: new PromptQueue(await read($, prompts)),
    isExpanded: await read($, isExpanded),
    isSubAgentMode: await read($, isSubAgentMode),
    isPlaying: await read($, isPlaying),
    editingId: await read($, editingId),
    tasks: await read($, tasks),
    notice: await read($, notice),
  }
}

export async function queuePrompt($: EngineInterface, text: string): Promise<boolean> {
  if (text.trim() === '') {
    return false
  }
  const edited = await read($, editingId)
  await update($, prompts, list => {
    const queue = new PromptQueue(list)
    return (queue.has(edited) ? queue.withText(edited, text) : queue.withAdded(text)).prompts
  })
  await update($, editingId, () => '')
  await update($, tasks, () => [])

  return true
}

/** Alt+Enter: the draft goes to the bottom of the queue instead of being sent, or back in its place when edited. */
export async function queueByKey($: EngineInterface, text: string): Promise<void> {
  if (await queuePrompt($, text)) {
    await update($, queuedByKey, () => text)
  }
}

/** Whether a submitted prompt is the draft Alt+Enter just queued, which is then no longer awaited. */
export async function isQueuedByKey($: EngineInterface, text: string): Promise<boolean> {
  const queued = await read($, queuedByKey)
  if (queued === '' || queued !== text) {
    return false
  }
  await update($, queuedByKey, () => '')

  return true
}

/** The `+` button: what the person typed so far moves to the bottom of the queue, or back in its place when edited. */
export async function queueDraft($: EngineInterface): Promise<void> {
  const { text } = await $.prompt.read()
  if (await queuePrompt($, text)) {
    await $.prompt.fill({ text: '', mode: 'replace' })
  }
}

export async function movePrompt($: EngineInterface, from: number, to: number): Promise<void> {
  await update($, prompts, list => new PromptQueue(list).withMoved(from, to).prompts)
  await update($, tasks, () => [])
}

export async function removePrompt($: EngineInterface, id: string): Promise<void> {
  await update($, prompts, list => new PromptQueue(list).without(id).prompts)
  await update($, tasks, () => [])
}

/** The pencil on a card: the prompt goes to the prompt box to be changed, and keeps its place in the queue, shaded,
 * until the next add puts the changed text back there. */
export async function editPrompt($: EngineInterface, prompt: QueuedPrompt): Promise<void> {
  await $.prompt.fill({ text: prompt.text, mode: 'replace' })
  await update($, editingId, () => prompt.id)
}

export async function clearQueue($: EngineInterface): Promise<void> {
  await update($, prompts, () => [])
  await update($, tasks, () => [])
}

export async function toggleExpanded($: EngineInterface): Promise<void> {
  await update($, isExpanded, open => !open)
}

export async function toggleSubAgentMode($: EngineInterface): Promise<void> {
  await update($, isSubAgentMode, on => !on)
  if (await read($, isSubAgentMode)) {
    await groupIntoTasks($)
  }
}

/** The play and pause button: playing starts with the next prompt at once when no turn is running. */
export async function togglePlaying($: EngineInterface): Promise<void> {
  await update($, isPlaying, playing => !playing)
  if ((await read($, isPlaying)) && !(await read($, isTurnRunning))) {
    await sendNext($)
  }
}

/** A main-chat turn started: play waits for it to finish. */
export async function startTurn($: EngineInterface): Promise<void> {
  await update($, isTurnRunning, () => true)
}

/** A main-chat turn ended: playing, the next prompt goes now, unless the turn was stopped or failed. */
export async function finishTurn($: EngineInterface, isAnswered: boolean): Promise<void> {
  await update($, isTurnRunning, () => false)
  if (isAnswered && (await read($, isPlaying))) {
    await sendNext($)
  }
}

/** Sends the prompt at the top of the queue as the person's next prompt, passing over one being edited. */
export async function sendNextPrompt($: EngineInterface): Promise<void> {
  const queue = new PromptQueue(await read($, prompts))
  const next = queue.firstExcept(await read($, editingId))
  if (!next) {
    return
  }
  await update($, prompts, list => new PromptQueue(list).without(next.id).prompts)
  await update($, notice, () => '')
  const command = slashCommandOf(next.text)
  const sent = command ? $.command.run(command) : $.prompt.submit({ text: next.text, asUser: true })
  sent.catch(failure => putBackUnsent($, next, failure))
}

/** A prompt the engine would not submit goes back to the top of the queue, and the box says why. */
async function putBackUnsent($: EngineInterface, unsent: QueuedPrompt, failure: unknown): Promise<void> {
  await update($, prompts, list => [unsent, ...list])
  await update($, notice, () => `Not sent: ${failure instanceof Error ? failure.message : String(failure)}`)
}

/** What a finished turn sends: the next prompt, or every task to its own sub-agent. */
export async function sendNext($: EngineInterface): Promise<void> {
  if (await read($, isSubAgentMode)) {
    await sendTasksToSubAgents($)
    return
  }
  await sendNextPrompt($)
}

export async function groupIntoTasks($: EngineInterface): Promise<void> {
  const queue = new PromptQueue(await read($, prompts))
  if (queue.isEmpty) {
    return
  }
  await update($, notice, () => 'Grouping the queue into sub-agent tasks…')
  const reply = await $.model.complete({
    model: GROUPING_MODEL,
    maxTokens: GROUPING_TOKENS,
    system: GROUPING_INSTRUCTIONS,
    prompt: JSON.stringify(queue.texts),
  })
  if (!reply.isAnswered) {
    await update($, notice, () => `Grouping failed: ${reply.reason}`)
    return
  }
  await update($, tasks, () => parseJsonArray(reply.text) as SubAgentTask[])
  await update($, notice, () => '')
}

export async function sendTasksToSubAgents($: EngineInterface): Promise<void> {
  if ((await read($, tasks)).length === 0) {
    await groupIntoTasks($)
  }
  const grouped = await read($, tasks)
  for (const task of grouped) {
    const started = await $.agent.spawn({
      prompt: task.prompts.join('\n\n'),
      description: task.description,
      subagentType: 'general-purpose',
    })
    if (started.deny) {
      await update($, notice, () => `Sub-agent refused: ${started.deny}`)
      return
    }
  }
  await clearQueue($)
  await update($, notice, () => `Sent ${grouped.length} task(s) to sub-agents.`)
}

/**
 * `/queue [list or focus]`: a pasted list queues each of its items in order; otherwise the model reads this
 * conversation and proposes the ordered prompts to queue, with the focus given. Answers what it queued, and why it
 * queued nothing when it did not.
 */
export async function queueFromCommand($: EngineInterface, args: string): Promise<string> {
  const listed = listedItems(args)
  if (listed.length > 0) {
    await queueAll($, listed)
    return `Queued ${listed.length} prompt(s).`
  }

  return planFromConversation($, args)
}

async function planFromConversation($: EngineInterface, focus: string): Promise<string> {
  const reply = await $.model.fork({ prompt: planningPrompt(focus) })
  if (!reply.isAnswered) {
    await update($, notice, () => `/queue could not read the conversation: ${reply.reason}`)
    return `Queued 0 prompt(s): the conversation could not be read. ${reply.reason}`
  }
  const planned = parseJsonArray(reply.text).filter((one): one is string => typeof one === 'string')
  if (planned.length === 0) {
    return `Queued 0 prompt(s): the model proposed none. It answered: ${reply.text.trim()}`
  }
  await queueAll($, planned)

  return `Queued ${planned.length} prompt(s) from this conversation.`
}

async function queueAll($: EngineInterface, texts: string[]): Promise<void> {
  for (const text of texts) {
    await queuePrompt($, text)
  }
  await update($, isExpanded, () => true)
}

function planningPrompt(focus: string): string {
  const about = focus.trim() === '' ? '' : `Focus on: ${focus.trim()}\n`
  return `${about}${PLANNING_INSTRUCTIONS}`
}

const PLANNING_INSTRUCTIONS =
  'Do not answer or do any of the work. From this conversation so far, list the next prompts the person ' +
  'should send, in the order they should run, each one a self-contained instruction a new turn can act on. ' +
  'Answer with only a JSON array of strings.'

const GROUPING_INSTRUCTIONS =
  'You are given a JSON array of prompts a person queued for a coding agent. Group them into tasks that ' +
  'independent sub-agents can run at the same time: prompts that depend on each other or touch the same ' +
  'work go in one task, kept in their order. Answer with only a JSON array of ' +
  '{"description": "<3 to 5 words>", "prompts": ["<prompt>", ...]}, using every prompt exactly once.'
