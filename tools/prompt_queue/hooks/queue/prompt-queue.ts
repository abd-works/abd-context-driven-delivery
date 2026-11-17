import { atom, read, update } from 'claude-code'
import type { EngineInterface, McpToolResult, PromptSubmitAttachment } from 'claude-code'

import type { PromptStep, QueueFailure, QueueJson, QueuedPrompt, SubAgentTask } from '../../types'
import { finishedPlan, nextPlan, type PlanCall } from './plan-steps'
import { PromptQueue, listedItems, parseJsonArray, slashCommandOf } from './queue-order'

const GROUPING_MODEL = 'sonnet'
const GROUPING_TOKENS = 4096
// The cdd servers a chat may hold, first choice first: a dev-lane worktree's own .mcp.json names cdd, the dev lane's
// server, which outranks the cdd plugin's; elsewhere the plugin declares it, and Claude Code names a plugin's server
// plugin:{plugin}:{server}.
const SERVERS = ['cdd', 'plugin:cdd:cdd']
// What play sends when a turn ends: the queue itself rides beside it, in queueContext.
const ASK_FOR_NEXT = 'Take the next prompt on the queue.'
const QUEUE_INSTRUCTIONS = [
  "This chat's prompt queue: work the person queued for you, in order.",
  'Finish what you are doing now, then take the first prompt below and do it as if the person had just sent it.',
  "When it is done, call prompt-queue.done with its id, then take the next, until the queue is empty or the person stops you.",
  'prompt-queue.show reads the queue again. Mark a prompt done only once its work is done; never take one off that you have not done.',
  `A prompt whose text starts with ${'"[decision required]"'} waits for the person's answer; pass over it.`,
].join(' ')
// What marks a prompt put back on the queue to wait for the person's answer; play passes over it.
const DECISION_FLAG = '[decision required]'
// How long play waits for the person to answer a question the agent ended its turn with, before it moves on.
const DECISION_WAIT_MS = 60_000
// Until the mod has seen the agent's task list, the agent keeps a prompt's steps on the queue itself.
const KEEP_STEPS_YOURSELF =
  'Give the prompt you take its steps with prompt-queue.set_steps, and mark each one done with prompt-queue.step_done as you finish it.'

/** The chat's queue as prompt-queue's tools last answered it: the cdd server keeps the queue, so the mod, the agent in
 * the chat and a session starting in it all change the same one, and the mod draws what the server answered. */
const queue = atom({ plugin: 'prompt-queue', key: 'queue' } as const, { chat: '', prompts: [] } as QueueJson)
const isExpanded = atom({ plugin: 'prompt-queue', key: 'isExpanded' } as const, false)
const isSubAgentMode = atom({ plugin: 'prompt-queue', key: 'isSubAgentMode' } as const, false)
const tasks = atom({ plugin: 'prompt-queue', key: 'tasks' } as const, [] as SubAgentTask[])
const notice = atom({ plugin: 'prompt-queue', key: 'notice' } as const, '')
/** The queue's latest failure, which CDD's shared failure line above the chat bar shows with its Fix and ✕. */
const failure = atom({ plugin: 'prompt-queue', key: 'failure' } as const, null as QueueFailure | null)
/** Playing, the agent sees the queue and each finished turn asks it to take the next prompt; paused, the queue waits. */
const isPlaying = atom({ plugin: 'prompt-queue', key: 'isPlaying' } as const, false)
/** Whether the main chat is in a turn, so play sends at once only when nothing is running. */
const isTurnRunning = atom({ plugin: 'prompt-queue', key: 'isTurnRunning' } as const, false)
/** The draft Alt+Enter just queued: the desktop still submits it after the key, so that submission is dropped. */
const queuedByKey = atom({ plugin: 'prompt-queue', key: 'queuedByKey' } as const, '')
/** The prompt being edited in the prompt box: it keeps its place, shaded, and the next add puts the draft back there. */
const editingId = atom({ plugin: 'prompt-queue', key: 'editingId' } as const, '')
/** The prompt the agent was last asked to take: still first on the queue after that turn, the agent left it, so play pauses. */
const askedAbout = atom({ plugin: 'prompt-queue', key: 'askedAbout' } as const, '')
/** Whether the agent ended its turn asking the person something, so play waits a minute for the answer. */
const isAwaitingDecision = atom({ plugin: 'prompt-queue', key: 'isAwaitingDecision' } as const, false)
/** Which wait for an answer is the current one: each turn and each new wait moves it on, so an older wait ends quietly. */
const decisionWait = atom({ plugin: 'prompt-queue', key: 'decisionWait' } as const, 0)
/** The agent's task list for the prompt it works on, as its last `update_plan` call left it. */
const plan = atom({ plugin: 'prompt-queue', key: 'plan' } as const, [] as PromptStep[])
/** Whether the mod has seen the agent set its task list; until it has, the agent is told to keep the steps itself. */
const isPlanSeen = atom({ plugin: 'prompt-queue', key: 'isPlanSeen' } as const, false)
/** The cards whose steps are shown under them. */
const openSteps = atom({ plugin: 'prompt-queue', key: 'openSteps' } as const, [] as string[])

export type QueueState = {
  queue: PromptQueue
  isExpanded: boolean
  isSubAgentMode: boolean
  isPlaying: boolean
  editingId: string
  workingId: string
  openSteps: string[]
  tasks: SubAgentTask[]
  notice: string
}

export async function currentQueue($: EngineInterface): Promise<QueueState> {
  return {
    queue: new PromptQueue((await read($, queue)).prompts),
    isExpanded: await read($, isExpanded),
    isSubAgentMode: await read($, isSubAgentMode),
    isPlaying: await read($, isPlaying),
    editingId: await read($, editingId),
    workingId: await read($, askedAbout),
    openSteps: await read($, openSteps),
    tasks: await read($, tasks),
    notice: await read($, notice),
  }
}

/** A prompt-queue tool the queue failed on; the message is the server's own text. */
class QueueCallFailed extends Error {}

/** The one place the mod calls the cdd server: a prompt-queue operation on this chat's queue, its answer read as JSON.
 * A reply flagged isError, or one that is not JSON, is a QueueCallFailed carrying the server's own text. */
async function callQueue<T>($: EngineInterface, operation: string, args: Record<string, unknown> = {}): Promise<T> {
  const chat = await $.session.id()
  const result = await callCddServer($, `prompt-queue.${operation}`, { chat, ...args, chat_folder: await $.session.root(), conversation_id: chat })
  const text = result.content[0]?.text ?? ''
  if (result.isError) {
    throw new QueueCallFailed(text || `prompt-queue.${operation} failed`)
  }
  try {
    return JSON.parse(text) as T
  } catch {
    throw new QueueCallFailed(text || `prompt-queue.${operation} sent back nothing`)
  }
}

// The cdd server that answered last, asked first next time; a reload starts over.
let answeringServer: string | undefined

/** Call tool on the first cdd server the chat holds that answers, the one that answered last first. */
async function callCddServer($: EngineInterface, tool: string, args: Record<string, unknown>): Promise<McpToolResult> {
  let failure: unknown = new QueueCallFailed('this chat holds no cdd server')
  for (const server of answeringServer ? [answeringServer, ...SERVERS.filter(other => other !== answeringServer)] : SERVERS) {
    try {
      const result = await $.mcp.call(server, tool, args)
      answeringServer = server
      return result
    } catch (unreached) {
      failure = unreached
    }
  }
  throw failure
}

/** Run an operation that answers the queue and draw what it answered; a failure shows in the queue box, and the queue
 * stays as the server last answered it. */
async function changeQueue($: EngineInterface, operation: string, args: Record<string, unknown> = {}): Promise<boolean> {
  try {
    const answered = await callQueue<QueueJson>($, operation, args)
    await update($, queue, () => answered)
    await update($, notice, () => '')
    return true
  } catch (thrown) {
    await showFailure($, `The queue did not change: ${reasonOf(thrown)}`, `Calling prompt-queue.${operation} on the cdd server, tried as ${SERVERS.join(' then ')}`)
    return false
  }
}

/** Read the queue again, as the agent or a starting session may have queued prompts the mod has not drawn yet. */
export async function refreshQueue($: EngineInterface): Promise<void> {
  await changeQueue($, 'show')
}

export async function queuePrompt($: EngineInterface, text: string): Promise<boolean> {
  if (text.trim() === '') {
    return false
  }
  const edited = await read($, editingId)
  const isEditing = (await read($, queue)).prompts.some(prompt => prompt.id === edited)
  const isChanged = await changeQueue($, isEditing ? 'edit' : 'add', isEditing ? { prompt: edited, text } : { text })
  await update($, editingId, () => '')
  await update($, tasks, () => [])

  return isChanged
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
  if (queued === '' || sameDraft(queued) !== sameDraft(text)) {
    return false
  }
  await update($, queuedByKey, () => '')

  return true
}

// The draft as the person wrote it, whatever line endings and trailing spaces the desktop sends it with: a long pasted
// draft came back with other endings, so the send after Alt+Enter was not recognised and went to the chat.
function sameDraft(text: string): string {
  return text.split(/\r?\n/).map(line => line.trimEnd()).join('\n').trim()
}

/** The `+` button: what the person typed so far moves to the bottom of the queue, or back in its place when edited. */
export async function queueDraft($: EngineInterface): Promise<void> {
  const { text } = await $.prompt.read()
  if (await queuePrompt($, text)) {
    await $.prompt.fill({ text: '', mode: 'replace' })
  }
}

export async function movePrompt($: EngineInterface, from: number, to: number): Promise<void> {
  const moving = (await read($, queue)).prompts[from]
  if (!moving || from === to) {
    return
  }
  await changeQueue($, 'move', { prompt: moving.id, to })
  await update($, tasks, () => [])
}

export async function removePrompt($: EngineInterface, id: string): Promise<void> {
  await changeQueue($, 'remove', { prompt: id })
  await update($, tasks, () => [])
}

/** The pencil on a card: the prompt goes to the prompt box to be changed, and keeps its place in the queue, shaded,
 * until the next add puts the changed text back there. */
export async function editPrompt($: EngineInterface, prompt: QueuedPrompt): Promise<void> {
  await $.prompt.fill({ text: prompt.text, mode: 'replace' })
  await update($, editingId, () => prompt.id)
}

export async function clearQueue($: EngineInterface): Promise<void> {
  await changeQueue($, 'clear')
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
  await update($, askedAbout, () => '')
  if ((await read($, isPlaying)) && !(await read($, isTurnRunning))) {
    await sendNext($)
  }
}

/** A main-chat turn started: play waits for it to finish. */
export async function startTurn($: EngineInterface): Promise<void> {
  await update($, isTurnRunning, () => true)
  await update($, isAwaitingDecision, () => false)
  await update($, decisionWait, wait => wait + 1)
}

/** A main-chat turn ended: the queue is read again, since the agent may have queued or finished work in the turn, and,
 * playing, the agent is asked to take the next prompt, unless the turn was stopped or failed. */
export async function finishTurn($: EngineInterface, isAnswered: boolean): Promise<void> {
  await update($, isTurnRunning, () => false)
  await refreshQueue($)
  if (!isAnswered || !(await read($, isPlaying))) {
    return
  }
  if (await read($, isAwaitingDecision)) {
    await waitForDecision($)
    return
  }
  await sendNext($)
}

/** The agent's wrap-up asked the person something: play waits for the answer before it moves on. */
export async function noteDecisionAsked($: EngineInterface, wrapUp: Record<string, unknown>): Promise<void> {
  const isAsking = wrapUp.blocked === true || (typeof wrapUp.ask === 'string' && wrapUp.ask.trim() !== '')
  await update($, isAwaitingDecision, () => isAsking)
}

/** Waits a minute for the person's answer; a turn starting meanwhile, the answer, ends the wait. */
async function waitForDecision($: EngineInterface): Promise<void> {
  const wait = (await read($, decisionWait)) + 1
  await update($, decisionWait, () => wait)
  $.clock.after(DECISION_WAIT_MS, () => void decisionTimedOut($, wait))
}

/** No answer came within the minute: the agent puts the prompt back as needing a decision and takes the next. */
async function decisionTimedOut($: EngineInterface, wait: number): Promise<void> {
  if (wait !== (await read($, decisionWait)) || (await read($, isTurnRunning)) || !(await read($, isPlaying))) {
    return
  }
  await update($, isAwaitingDecision, () => false)
  const asked = await read($, askedAbout)
  const text = `No answer came within a minute. Put prompt [${asked}] back on the queue as unfinished: give it with ` +
    `prompt-queue.edit a text that starts with "${DECISION_FLAG}", then the question and your recommendation. Then take the next prompt on the queue.`
  $.prompt.submit({ text, asUser: true }).catch(thrown =>
    showFailure($, `Not sent: ${reasonOf(thrown)}`, 'Waiting a minute for an answer, then moving play on'))
}

/** Asks the agent to take the next prompt on the queue: the agent does it and marks it done itself, so nothing leaves
 * the queue here. A queued slash command, which the agent cannot type, runs as the command and is marked done. When the
 * agent left the prompt it was last asked about on the queue, play pauses rather than asking again and again. */
export async function sendNextPrompt($: EngineInterface): Promise<void> {
  const next = await nextToDo($)
  if (!next) {
    return
  }
  if (next.id === (await read($, askedAbout))) {
    await update($, isPlaying, () => false)
    await update($, notice, () => `Paused: the agent left "${next.text}" on the queue. Press play to ask again.`)
    return
  }
  await workOn($, next.id)
  const command = slashCommandOf(next.text)
  const sent = command ? $.command.run(command).then(() => changeQueue($, 'done', { prompt: next.id })) : $.prompt.submit({ text: ASK_FOR_NEXT, asUser: true })
  sent.catch(thrown => showFailure($, `Not sent: ${reasonOf(thrown)}`, command ? `Playing the queue, running /${command.command} from it` : 'Playing the queue, asking the agent to take the next prompt'))
}

/** The prompts the agent is to do, in order: every queued prompt not done but one the person is editing, which waits in
 * its place. */
async function promptsToDo($: EngineInterface): Promise<QueuedPrompt[]> {
  const edited = await read($, editingId)
  return (await read($, queue)).prompts.filter(prompt => prompt.id !== edited && !prompt.is_done && !prompt.text.startsWith(DECISION_FLAG))
}

async function nextToDo($: EngineInterface): Promise<QueuedPrompt | undefined> {
  return (await promptsToDo($))[0]
}

/** What the agent reads beside each prompt while the queue plays: the queue, in order, and how to work through it; none
 * while paused or empty, so a paused queue never pulls the agent away from what the person asked. */
export async function queueContext($: EngineInterface, sentId = ''): Promise<string | undefined> {
  if (!(await read($, isPlaying))) {
    return undefined
  }
  const prompts = (await promptsToDo($)).filter(prompt => prompt.id !== sentId)
  if (prompts.length === 0) {
    return undefined
  }
  const instructions = (await read($, isPlanSeen)) ? QUEUE_INSTRUCTIONS : `${QUEUE_INSTRUCTIONS} ${KEEP_STEPS_YOURSELF}`
  return [instructions, '', ...prompts.map((prompt, place) => `${place + 1}. [${prompt.id}] ${prompt.text}${attachedNote(prompt)}`)].join('\n')
}

/** The files queued with a prompt, as the agent reads them beside it, to open when it takes the prompt. */
function attachedNote(prompt: QueuedPrompt): string {
  const attached = prompt.attachments ?? []
  return attached.length === 0 ? '' : ` (attached, open each: ${attached.join(', ')})`
}

/** The images and documents pasted in a draft Alt+Enter queued: the engine sends them with the submission it drops, and
 * a plugin cannot send them with a prompt later, so each is kept as a file beside the queued prompt. */
export async function keepQueuedAttachments($: EngineInterface, text: string, attachments: readonly PromptSubmitAttachment[]): Promise<void> {
  const queued = (await read($, queue)).prompts.filter(prompt => sameDraft(prompt.text) === sameDraft(text)).at(-1)
  if (!queued) {
    return
  }
  for (const attachment of attachments) {
    const data = attachment.id ? await mediaOf($, attachment.id) : undefined
    if (data) {
      await changeQueue($, 'attach', { prompt: queued.id, filename: attachment.filename ?? '', media_type: data.mediaType, data: data.base64 })
    }
  }
}

/** One attached item's bytes, base64, read slice by slice; none for an item the engine will not give. */
async function mediaOf($: EngineInterface, id: string): Promise<{ mediaType: string; base64: string } | undefined> {
  const slices: string[] = []
  let mediaType = ''
  let offset: number | undefined = 0
  while (offset !== undefined) {
    const slice = await $.prompt.media({ id, offset })
    if (slice.base64 === undefined) {
      await showFailure($, `An attachment was not queued: ${slice.unreadable ?? slice.deny}`, 'Queuing a draft with Alt+Enter, reading its pasted item')
      return undefined
    }
    slices.push(slice.base64)
    mediaType = slice.mediaType
    offset = slice.next
  }
  return { mediaType, base64: slices.join('') }
}

/** The prompt the agent works on now: the one play asked it to take, or one sent straight to the chat. Its task list
 * starts empty. */
async function workOn($: EngineInterface, id: string): Promise<void> {
  await update($, askedAbout, () => id)
  await update($, plan, () => [])
}

/** A prompt sent straight to the chat, as the queue holds it: its id, and what the agent is told about it. */
export type SentPrompt = { id: string; note: string }

/** A prompt the person sent straight to the chat goes on the queue first, as the prompt being worked, so the steps the
 * agent plans for it sit under it; the agent is told its id, to mark it done when it is finished. */
export async function queueSentPrompt($: EngineInterface, text: string): Promise<SentPrompt | undefined> {
  if (text.trim() === '' || text.trim() === ASK_FOR_NEXT || !(await changeQueue($, 'add', { text }))) {
    return undefined
  }
  const sent = (await read($, queue)).prompts.at(-1)
  if (!sent) {
    return undefined
  }
  await changeQueue($, 'move', { prompt: sent.id, to: 0 })
  await workOn($, sent.id)
  return { id: sent.id, note: `This prompt is first on this chat's prompt queue as [${sent.id}]. When its work is done, call prompt-queue.done with that id.` }
}

/** One `update_plan` call: the agent's task list follows it and is copied whole onto the prompt being worked. */
export async function followPlan($: EngineInterface, call: PlanCall): Promise<void> {
  await update($, isPlanSeen, () => true)
  await update($, plan, steps => nextPlan(steps, call))
  await copyPlanOntoWorkingPrompt($)
}

/** A wrapped-up turn finished its task list: every step of the prompt being worked is done. */
export async function finishPlan($: EngineInterface): Promise<void> {
  if ((await read($, plan)).length === 0) {
    return
  }
  await update($, plan, finishedPlan)
  await copyPlanOntoWorkingPrompt($)
}

async function copyPlanOntoWorkingPrompt($: EngineInterface): Promise<void> {
  const working = await read($, askedAbout)
  if (!(await read($, queue)).prompts.some(prompt => prompt.id === working)) {
    return
  }
  await changeQueue($, 'set_steps', { prompt: working, steps: await read($, plan) })
}

/** The send-now button on a card: the prompt moves to the top of the queue and goes to the chat at once, as the prompt
 * being worked, whether the queue plays or not. The message names its id, since a plugin's own prompt carries no
 * context, so the agent can mark it done. */
export async function sendNow($: EngineInterface, prompt: QueuedPrompt): Promise<void> {
  await changeQueue($, 'move', { prompt: prompt.id, to: 0 })
  await workOn($, prompt.id)
  $.prompt.submit({ text: `Take prompt [${prompt.id}] on the queue now: ${prompt.text}`, asUser: true }).catch(thrown =>
    showFailure($, `Not sent: ${reasonOf(thrown)}`, `Pressing send now on "${prompt.text}"`))
}

/** The steps toggle on a card: its steps show under it, or fold away again. */
export async function toggleSteps($: EngineInterface, id: string): Promise<void> {
  await update($, openSteps, open => (open.includes(id) ? open.filter(shown => shown !== id) : [...open, id]))
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
  const queued = new PromptQueue((await read($, queue)).prompts)
  if (queued.isEmpty) {
    return
  }
  await update($, notice, () => 'Grouping the queue into sub-agent tasks…')
  const reply = await $.model.complete({
    model: GROUPING_MODEL,
    maxTokens: GROUPING_TOKENS,
    system: GROUPING_INSTRUCTIONS,
    prompt: JSON.stringify(queued.texts),
  })
  if (!reply.isAnswered) {
    await update($, notice, () => '')
    await showFailure($, `Grouping failed: ${reply.reason}`, `Grouping the queue into sub-agent tasks with ${GROUPING_MODEL}`)
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
      await showFailure($, `Sub-agent refused: ${started.deny}`, `Sending the task "${task.description}" to a sub-agent`)
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
    await showFailure($, `/queue could not read the conversation: ${reply.reason}`, 'Running /queue, asking the model to plan prompts from this conversation')
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
  await changeQueue($, 'add_all', { texts })
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

/** Keeps the queue's latest failure, what failed with the reason it gave and what the queue was doing, for CDD's shared
 * failure line above the chat bar to show with its Fix and ✕. Only a value's owner writes it, so the board reads it from
 * here; each failure takes the next id, so a newer one shows again after Fix or ✕ handled an older one. */
async function showFailure($: EngineInterface, failed: string, context: string): Promise<void> {
  await update($, failure, kept => ({ id: (kept?.id ?? 0) + 1, failure: failed, context }))
}

/** The words a failure carries: a thrown error's message, or the value itself. */
function reasonOf(thrown: unknown): string {
  return thrown instanceof Error ? thrown.message : String(thrown)
}
