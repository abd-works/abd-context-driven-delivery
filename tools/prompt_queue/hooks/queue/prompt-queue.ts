import { atom, read, update } from 'claude-code'
import type { AgentSpawnInput, AgentSpawnResult, EngineInterface, McpToolResult, PromptSubmitAttachment } from 'claude-code'

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
  'When you take a prompt, first call prompt-queue.set_steps with its id and the steps you plan for it, so the queue shows your work on the prompt you took.',
  'Keep one card for each goal: when a message the person sends belongs to a goal already on the queue, make it a task of that goal with prompt-queue.set_steps',
  'and take its own card off with prompt-queue.remove; gather related [interruption] cards under one goal card the same way, written as a short title of the goal.',
  'Keep the order done, then being worked, then not started.',
  'After you add, assign, move or take off cards, call prompt-queue.show and check what you placed: each card stands once, on the goal or robot you meant,',
  'with no card left over that is only talk or a copy of another; fix what is wrong before you answer the person, so they never have to point it out.',
].join(' ')
// What marks a prompt put back on the queue to wait for the person's answer; play passes over it.
const DECISION_FLAG = '[decision required]'
// How long play waits for the person to answer a question the agent ended its turn with, before it moves on.
const DECISION_WAIT_MS = 60_000
// How long after a robot's sub-agent stops the queue first checks its card, so this chat can mark a finished card done.
const ROBOT_FIRST_CHECK_MS = 60_000
// How often the queue checks again on a robot that stays stopped with its card not done.
const ROBOT_CHECK_MS = 600_000
// A notice the chat gives the agent, such as a background task finishing, which arrives as a prompt but is not the
// person's: it is never queued.
const SYSTEM_NOTICE = /^\s*<(task-notification|system-reminder)>/
// How much of each goal's text the note on a filed message lists, enough to tell the goals apart.
const GOAL_TITLE_COLUMNS = 100
// How a card queued for a robot by name starts: [for Bolt] ...
const ROBOT_MARK_OPEN = '[for '
// What marks a step that came from a message the person sent while the agent worked.
const INTERRUPTION_MARK = '[interruption]'
// Until the mod has seen the agent's task list, the agent keeps a prompt's steps on the queue itself.
const KEEP_STEPS_YOURSELF = 'Mark each step done with prompt-queue.step_done as you finish it.'

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
/** The card each robot was last handed, so a robot that stops without marking it done is not handed it again. */
const sentCards = atom({ plugin: 'prompt-queue', key: 'sentCards' } as const, {} as Record<string, string>)
/** Each robot's sub-agent id, from this chat's Agent call that started it, so its next card is sent to that sub-agent. */
const robotAgents = atom({ plugin: 'prompt-queue', key: 'robotAgents' } as const, {} as Record<string, string>)
/** The sub-agents in a turn now, so a robot that stopped is told from one still working. */
const workingAgents = atom({ plugin: 'prompt-queue', key: 'workingAgents' } as const, [] as string[])
/** Which check on each sub-agent is the current one: each turn it starts or ends moves it on, so an older check ends quietly. */
const robotChecks = atom({ plugin: 'prompt-queue', key: 'robotChecks' } as const, {} as Record<string, number>)
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
/** The cards whose finished steps are shown rather than folded into one line. */
const shownDoneSteps = atom({ plugin: 'prompt-queue', key: 'shownDoneSteps' } as const, [] as string[])
/** The places of the robots whose queues are collapsed to the robot alone, so the other queues take the room. */
const expandedAgents = atom({ plugin: 'prompt-queue', key: 'expandedAgents' } as const, [] as number[])

export type QueueState = {
  queue: PromptQueue
  isOn: boolean
  isExpanded: boolean
  isSubAgentMode: boolean
  isPlaying: boolean
  editingId: string
  openSteps: string[]
  shownDoneSteps: string[]
  expandedAgents: number[]
  tasks: SubAgentTask[]
  /** Each robot's theme, one sentence, by its name as the queue spells it: shown beside a robot whose cards are closed. */
  themes: Record<string, string>
  notice: string
}

export async function currentQueue($: EngineInterface): Promise<QueueState> {
  return {
    queue: new PromptQueue((await read($, queue)).prompts),
    isOn: await isQueueOn($),
    isExpanded: await read($, isExpanded),
    isSubAgentMode: await read($, isSubAgentMode),
    isPlaying: await read($, isPlaying),
    editingId: await read($, editingId),
    openSteps: await read($, openSteps),
    shownDoneSteps: await read($, shownDoneSteps),
    expandedAgents: await read($, expandedAgents),
    tasks: robotsOf((await read($, queue)).prompts, await read($, tasks)),
    themes: (await read($, queue)).themes ?? {},
    notice: await read($, notice),
  }
}

/** Whether the person switched this chat's queue on, as the cdd server last answered: a chat's queue is off until
 * switched on, and off, the mod adds no note to a message, plays nothing and hands nothing to robots. */
export async function isQueueOn($: EngineInterface): Promise<boolean> {
  return (await read($, queue)).is_on === true
}

/** The on/off button: switches the chat's queue on, or off; off, the queue is paused too, so nothing is sent when it
 * is switched on again until the person plays it. */
export async function toggleQueueOn($: EngineInterface): Promise<void> {
  if (!(await isQueueOn($))) {
    await changeQueue($, 'switch_on')
    return
  }
  if (await changeQueue($, 'switch_off')) {
    await update($, isPlaying, () => false)
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

// The cdd server that answered last, asked first next time, kept in the chat's state so a reload asks it first too.
const answeringServer = atom({ plugin: 'prompt-queue', key: 'answeringServer' } as const, '')

/** Call tool on the first cdd server the chat holds that answers, the one that answered last first. */
async function callCddServer($: EngineInterface, tool: string, args: Record<string, unknown>): Promise<McpToolResult> {
  let failure: unknown = new QueueCallFailed('this chat holds no cdd server')
  const answered = await read($, answeringServer)
  for (const server of answered ? [answered, ...SERVERS.filter(other => other !== answered)] : SERVERS) {
    try {
      const result = await $.mcp.call(server, tool, args)
      await update($, answeringServer, () => server)
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
  const editedCard = (await read($, queue)).prompts.find(prompt => prompt.id === edited)
  if (isChanged && isEditing && editedCard) {
    await tellRobotOfChange($, editedCard, `its words are now: ${text.trim()}`)
  }

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

/** The `+` button runs /queue on the prompt box's draft, which places it into the plan; an edited prompt goes back in
 * its place instead. Alt+Enter is the plain add. The box empties once the draft is placed, and keeps it when the model
 * could not place it. */
export async function queueDraft($: EngineInterface): Promise<void> {
  const { text } = await $.prompt.read()
  if (text.trim() === '') {
    return
  }
  const edited = await read($, editingId)
  const isEditing = (await read($, queue)).prompts.some(prompt => prompt.id === edited)
  const robot = await openRobotOf($)
  const isPlaced = isEditing
    ? await queuePrompt($, text)
    : robot ? await queueForRobot($, text, robot) : (await runQueueCommand($, text)).isPlaced
  if (isPlaced) {
    await $.prompt.fill({ text: '', mode: 'replace' })
  }
}

/** In sub-agent mode, the robot whose queue is open, which + adds to; none while no robot is open or the mode is off. */
async function openRobotOf($: EngineInterface): Promise<string | undefined> {
  if (!(await read($, isSubAgentMode))) {
    return undefined
  }
  const open = (await read($, expandedAgents))[0]
  if (open === undefined) {
    return undefined
  }
  const robot = robotsOf((await read($, queue)).prompts, await read($, tasks))[open]
  return robot ? agentNameOf(robot, open) : undefined
}

/** + while a robot's queue is open: the draft becomes the last card of that robot's queue, where the person sees it. */
async function queueForRobot($: EngineInterface, text: string, robot: string): Promise<boolean> {
  if (!(await changeQueue($, 'add', { text: text.trim() }))) {
    return false
  }
  const added = (await read($, queue)).prompts.at(-1)
  return added ? changeQueue($, 'assign', { prompt: added.id, robot }) : false
}

/** Where the model put one piece of a draft: a task of the goal whose id it names, or a card of its own. */
type DraftPlace = { goal?: string; card?: string; text?: string }

/** What /queue did with what it was given: whether the work is on the queue, and what it says about it. */
type QueueCommandResult = { isPlaced: boolean; said: string }

/** The model reads this conversation and the queue and places each piece of the draft into the plan: a task of the goal
 * it is about, or a card of its own. It gives no card a robot; the agents button groups the work into robots. */
async function placeDraft($: EngineInterface, draft: string): Promise<QueueCommandResult> {
  const goals = (await read($, queue)).prompts
  const reply = await $.model.fork({ prompt: placingPrompt(draft, goals) })
  if (!reply.isAnswered) {
    await showFailure($, `The draft was not placed on the queue: ${reply.reason}`, 'Running /queue on a draft, asking the model where it belongs')
    return { isPlaced: false, said: `Placed nothing: ${reply.reason}` }
  }
  const places = parseJsonArray(reply.text) as DraftPlace[]
  for (const place of places) {
    await placeDraftPiece($, goals, place)
  }
  await update($, isExpanded, () => true)
  return { isPlaced: true, said: `Placed ${places.length} piece(s) of the draft on the queue.` }
}

async function placeDraftPiece($: EngineInterface, goals: QueuedPrompt[], place: DraftPlace): Promise<void> {
  if (place.goal && place.text && goals.some(goal => goal.id === place.goal)) {
    await changeQueue($, 'add_interruption', { prompt: place.goal, text: place.text })
    return
  }
  if (place.card) {
    await changeQueue($, 'add', { text: place.card })
  }
}

function placingPrompt(draft: string, goals: QueuedPrompt[]): string {
  return [
    'Do not answer or do any of the work. The person wants this draft placed into the plan on the prompt queue:',
    draft.trim(),
    'Decide where it belongs, reading this conversation. It may hold several pieces of work; place each one.',
    'A piece about a goal on the queue becomes a task of that goal: {"goal": "<id>", "text": "<the task, short>"}.',
    'A piece no goal covers becomes a card of its own, a short title of the goal: {"card": "<text>"}.',
    'The goals on the queue:',
    ...goals.map(goalLineOf),
    'Answer with only a JSON array of those objects.',
  ].join('\n')
}

export async function movePrompt($: EngineInterface, from: number, to: number): Promise<void> {
  const moving = (await read($, queue)).prompts[from]
  if (!moving || from === to) {
    return
  }
  if (await changeQueue($, 'move', { prompt: moving.id, to })) {
    await tellRobotOfChange($, moving, `its cards were reordered; its cards still to do, in order: ${await robotOrderOf($, moving.robot)}`)
  }
}

export async function removePrompt($: EngineInterface, id: string): Promise<void> {
  const removing = (await read($, queue)).prompts.find(prompt => prompt.id === id)
  if ((await changeQueue($, 'remove', { prompt: id })) && removing) {
    await tellRobotOfChange($, removing, 'the card was taken off the queue: stop its work, and keep what is done')
    await forgetRobotsNoCardNames($)
  }
}

/** A robot no card on the queue names any more is gone from the queue, so its task, its sub-agent, the card it was
 * handed and its open queue are forgotten, as leaving sub-agent mode forgets every robot; a robot still named keeps
 * its queue open where it now stands. */
async function forgetRobotsNoCardNames($: EngineInterface): Promise<void> {
  const prompts = (await read($, queue)).prompts
  const isNamed = (robot: string) => prompts.some(prompt => isSameRobot(prompt.robot, robot))
  const before = robotsOf(prompts, await read($, tasks)).map((robot, place) => agentNameOf(robot, place))
  const openNames = (await read($, expandedAgents)).map(place => before[place]).filter((name): name is string => name !== undefined)
  await update($, tasks, described => described.filter(task => isNamed(task.name)))
  await update($, robotAgents, agents => keptFor(agents, isNamed))
  await update($, sentCards, cards => keptFor(cards, isNamed))
  const after = robotsOf(prompts, await read($, tasks)).map((robot, place) => agentNameOf(robot, place))
  await update($, expandedAgents, () => openNames.map(name => after.indexOf(name)).filter(place => place >= 0))
}

/** The entries of a record kept by robot name whose robot is still named on the queue. */
function keptFor(byRobot: Record<string, string>, isNamed: (robot: string) => boolean): Record<string, string> {
  return Object.fromEntries(Object.entries(byRobot).filter(([robot]) => isNamed(robot)))
}

/** A robot works only the words this chat sends it, so a change the person makes to a card of a robot whose sub-agent
 * is running is sent on: this chat is asked to tell that sub-agent what changed. A robot with no sub-agent yet gets the
 * card as it then stands when it is handed out. */
async function tellRobotOfChange($: EngineInterface, card: QueuedPrompt, change: string): Promise<void> {
  const agentId = card.robot ? (await read($, robotAgents))[card.robot] : undefined
  if (!agentId) {
    return
  }
  const text = `The person changed ${card.robot}'s card [${card.id}]: ${change}. Tell ${card.robot} with SendMessage to ${agentId}, in those words, then carry on.`
  $.prompt.submit({ text, asUser: true }).catch(thrown =>
    showFailure($, `Not sent: ${reasonOf(thrown)}`, `Telling ${card.robot} that the person changed its card [${card.id}]`))
}

/** The ids of a robot's cards still to do, in queue order, as the robot is told them after a reorder. */
async function robotOrderOf($: EngineInterface, robot: string | undefined): Promise<string> {
  const cards = (await read($, queue)).prompts.filter(prompt => !prompt.is_done && prompt.robot && prompt.robot === robot)
  return cards.map(prompt => `[${prompt.id}]`).join(', ')
}

/** The pencil on a card: the prompt goes to the prompt box to be changed, and keeps its place in the queue, shaded,
 * until the next add puts the changed text back there. */
export async function editPrompt($: EngineInterface, prompt: QueuedPrompt): Promise<void> {
  await $.prompt.fill({ text: prompt.text, mode: 'replace' })
  await update($, editingId, () => prompt.id)
}

export async function clearQueue($: EngineInterface): Promise<void> {
  await changeQueue($, 'clear')
}

/** Flush: the cdd server keeps a timestamped copy of the whole queue file in the chat's queue archive, then takes the
 * finished cards off, as prompt-queue.flush does; the button asks for nothing more. */
export async function flushQueue($: EngineInterface): Promise<void> {
  if (await changeQueue($, 'flush')) {
    await forgetRobotsNoCardNames($)
  }
}

export async function toggleExpanded($: EngineInterface): Promise<void> {
  await update($, isExpanded, open => !open)
}

/** The sub-agents button: switching sub-agent mode on groups the work not done into robots; switching it off makes the
 * work the chat's own again, so every robot comes off the queue with the sub-agents they went by. */
export async function toggleSubAgentMode($: EngineInterface): Promise<void> {
  await update($, isSubAgentMode, on => !on)
  if (await read($, isSubAgentMode)) {
    await groupIntoTasks($)
    return
  }
  await takeRobotsOff($)
}

/** Every card given to a robot is given to none, and the robots, their sub-agents and their open queues are forgotten. */
async function takeRobotsOff($: EngineInterface): Promise<void> {
  for (const goal of (await read($, queue)).prompts.filter(prompt => prompt.robot)) {
    await changeQueue($, 'assign', { prompt: goal.id, robot: '' })
  }
  await update($, tasks, () => [])
  await update($, robotAgents, () => ({}))
  await update($, expandedAgents, () => [])
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
  if (!isAnswered || !(await read($, isPlaying)) || !(await isQueueOn($))) {
    return
  }
  if (await read($, isAwaitingDecision)) {
    await waitForDecision($)
    return
  }
  await sendNext($)
}

/** A robot's sub-agent started a turn: it is working, so no check on it is due. */
export async function startAgentTurn($: EngineInterface, agentId: string): Promise<void> {
  await update($, workingAgents, working => [...working.filter(id => id !== agentId), agentId])
  await update($, robotChecks, checks => ({ ...checks, [agentId]: (checks[agentId] ?? 0) + 1 }))
}

/** A robot's sub-agent ended its turn: nothing it started runs any more, so the queue checks on its card a minute later,
 * and every ten minutes after while the card stays not done, rather than trust a report that work is still running. */
export async function finishAgentTurn($: EngineInterface, agentId: string): Promise<void> {
  await update($, workingAgents, working => working.filter(id => id !== agentId))
  await scheduleRobotCheck($, agentId, ROBOT_FIRST_CHECK_MS)
}

async function scheduleRobotCheck($: EngineInterface, agentId: string, ms: number): Promise<void> {
  const check = ((await read($, robotChecks))[agentId] ?? 0) + 1
  await update($, robotChecks, checks => ({ ...checks, [agentId]: check }))
  $.clock.after(ms, () => void checkOnRobot($, agentId, check))
}

/** The check falls due: a robot still stopped with its card not done has this chat asked to look at it. While the main
 * chat is in a turn the check waits for the next one, so it never breaks into the agent's work. */
async function checkOnRobot($: EngineInterface, agentId: string, check: number): Promise<void> {
  if (check !== ((await read($, robotChecks))[agentId] ?? 0)) {
    return
  }
  const stopped = await stoppedRobotOf($, agentId)
  if (!stopped) {
    return
  }
  await scheduleRobotCheck($, agentId, ROBOT_CHECK_MS)
  if (await read($, isTurnRunning)) {
    return
  }
  $.prompt.submit({ text: checkOnRobotOf(stopped.robot, stopped.card, agentId, await $.session.id()), asUser: true }).catch(thrown =>
    showFailure($, `Not sent: ${reasonOf(thrown)}`, `Checking on ${stopped.robot}, whose sub-agent stopped with card [${stopped.card.id}] not done`))
}

/** The robot a stopped sub-agent works for and its first card not done; none when the sub-agent works again, is no
 * robot's, or its robot has finished every card. */
async function stoppedRobotOf($: EngineInterface, agentId: string): Promise<{ robot: string; card: QueuedPrompt } | undefined> {
  if (!(await read($, isSubAgentMode)) || !(await isQueueOn($)) || (await read($, workingAgents)).includes(agentId)) {
    return undefined
  }
  const robot = Object.entries(await read($, robotAgents)).find(([, id]) => id === agentId)?.[0]
  if (robot === undefined) {
    return undefined
  }
  await refreshQueue($)
  const card = (await read($, queue)).prompts.find(prompt => isSameRobot(prompt.robot, robot) && !prompt.is_done)
  return card ? { robot, card } : undefined
}

/** What this chat is asked about a robot that stopped with its card not done. */
function checkOnRobotOf(robot: string, card: QueuedPrompt, agentId: string, chat: string): string {
  return [
    `${robot}'s sub-agent ${agentId} has stopped, and its card [${card.id}] is not done. Nothing a sub-agent started runs once its turn ends, so do not take its word that work is still running.`,
    `Read its last report. If it says the card is finished, check the result and mark it done with prompt-queue.done(chat="${chat}", prompt="${card.id}").`,
    `If it waits on another robot's card that is not done, leave it and say so. Otherwise resume it with SendMessage to ${agentId}, telling it to finish card [${card.id}] in its own turn and report.`,
  ].join(' ')
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
  return (await read($, queue)).prompts.filter(prompt => prompt.id !== edited && prompt.is_waiting)
}

async function nextToDo($: EngineInterface): Promise<QueuedPrompt | undefined> {
  return (await promptsToDo($))[0]
}

/** What the agent reads beside each prompt while the queue plays: the queue, in order, and how to work through it; none
 * while paused or empty, so a paused queue never pulls the agent away from what the person asked. */
export async function queueContext($: EngineInterface, sentId = ''): Promise<string | undefined> {
  if (!(await read($, isPlaying)) || !(await isQueueOn($))) {
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

/** Whether the cdd server reads a message the person sent as only talk, which the chat answers and queues none of. A
 * server that cannot answer shows the failure, and the message is read as work, so the agent still decides where it
 * goes. */
async function isOnlyTalk($: EngineInterface, message: string): Promise<boolean> {
  try {
    return (await callQueue<{ is_only_talk: boolean }>($, 'is_only_talk', { message })).is_only_talk
  } catch (thrown) {
    await showFailure($, `Not read as talk or work: ${reasonOf(thrown)}`, 'Calling prompt-queue.is_only_talk on the cdd server')
    return false
  }
}

/** A prompt sent straight to the chat, as the queue holds it: its id, and what the agent is told about it. */
export type SentPrompt = { id: string; note: string }

/** A prompt the person sent straight to the chat goes to the chat as sent and puts nothing on the queue: the agent is
 * told about the queue beside it and decides whether it is work, and only then puts it there, as a step of the goal it
 * belongs to or a card of its own with a clean title. A message the cdd server reads as only talk
 * (prompt-queue.is_only_talk) carries no note, since the chat just answers it. */
export async function queueSentPrompt($: EngineInterface, text: string): Promise<SentPrompt | undefined> {
  if (text.trim() === '' || text.trim() === ASK_FOR_NEXT || SYSTEM_NOTICE.test(text)) {
    return undefined
  }
  // The queue as the server holds it now: the chat's start may have read it before the cdd server connected.
  await refreshQueue($)
  if (!(await isQueueOn($)) || (await isOnlyTalk($, text))) {
    return undefined
  }
  const editing = await read($, editingId)
  const goals = (await read($, queue)).prompts.filter(prompt => !prompt.is_done && prompt.id !== editing)
  const working = await interruptedPrompt($)
  const robots = (await read($, isSubAgentMode)) ? robotsOf(goals, await read($, tasks)) : []
  return { id: '', note: [sentNoteOf(await $.session.id(), working?.id, goals), ...robotsNoteOf(robots, goals)].join('\n') }
}

/** The goal a message the person sends is most likely about: the one last worked, if it is on the queue, while a turn
 * works that goal or its turn ended asking the person something. A message sent between turns is about none. */
async function interruptedPrompt($: EngineInterface): Promise<QueuedPrompt | undefined> {
  if (!(await read($, isTurnRunning)) && !(await read($, isAwaitingDecision))) {
    return undefined
  }
  const working = await read($, askedAbout)
  return (await read($, queue)).prompts.find(prompt => prompt.id === working)
}

/** What the agent is told about a message the person sent: it is on no card, and the agent puts it on the queue only
 * when it is work, where it belongs, titled cleanly, then reads the queue back to check. */
function sentNoteOf(chat: string, working: string | undefined, goals: QueuedPrompt[]): string {
  return [
    `The person sent this message in this chat, chat "${chat}"; it is on no card of the queue. Decide what it is before any other work:`,
    `1. Only talk (a question, an answer, a complaint or a comment): answer it, and put nothing on the queue.`,
    `2. Work for a goal on the queue${working ? `, such as the one being worked, [${working}]` : ''}: file it there with prompt-queue.add_interruption, as a short clean step.`,
    '3. New work no goal covers: queue it with prompt-queue.add as a card of its own, titled as a short statement of the goal in plain words, with the typing mistakes and any venting left out, and, when its work has clear parts, give it its steps with prompt-queue.set_steps as you add it.',
    `Pass chat "${chat}" to every prompt-queue call. A block the Claude app puts before the message, such as <artifact-view-context>, is a viewer's state, not the person's words: never put any of it in a title or a step.`,
    'Then call prompt-queue.show and check that what you placed stands once, where you meant it. The goals on the queue:',
    ...goals.map(goalLineOf),
  ].join('\n')
}

/** A goal as a note lists it: its id and the start of its text, enough to tell the goals apart. */
function goalLineOf(goal: QueuedPrompt): string {
  return `- [${goal.id}] ${goal.text.replace(/\s+/g, ' ').slice(0, GOAL_TITLE_COLUMNS)}${goal.is_done ? ' (done)' : ''}`
}

/** In sub-agent mode, what the agent reads beside a new message: each robot's queue, and that the agent decides whether
 * to do the message itself, make it a task of a robot's item, or give it to a robot as a new item. */
function robotsNoteOf(robots: SubAgentTask[], goals: QueuedPrompt[]): string[] {
  if (robots.length === 0) {
    return []
  }
  return [
    "Sub-agent mode is on. You decide where this message goes: do it yourself; make it a task of an item in a robot's queue with prompt-queue.add_interruption;",
    'or give it to a robot as a new item: prompt-queue.add, then prompt-queue.assign with the robot\'s name, so it stands in that robot\'s queue alone. Take it off this goal when it goes elsewhere,',
    "then call prompt-queue.show and check each card stands once, in the robot's queue you meant.",
    "When you add a card whose work has clear parts, give it its steps with prompt-queue.set_steps as you add it, so the queue shows the plan before anyone starts.",
    "Work that waits on a robot's result goes to that robot, after the card it waits on, so no robot waits on another or hands its result over; start a new robot only for work that can run at the same time.",
    "A robot works only the words this chat sends it, and says when it finished: send it new work with SendMessage to its robot name. The robots' queues:",
    ...robots.map((robot, place) => `${agentNameOf(robot, place)}: ${robotPromptsOf(goals, robot, place).map(goal => `[${goal.id}] ${goal.text.slice(0, GOAL_TITLE_COLUMNS)}`).join('; ')}`),
  ]
}

/** A robot's items as they stand on the queue, in queue order: the cards given to it, and any card given to no robot
 * that is queued for it by name, its text starting [for <robot name>], the name matched with no regard to case or outer
 * spaces. The robot a card was given to decides, so a card stands in one robot's queue and one sub-agent is handed it. */
export function robotPromptsOf(goals: QueuedPrompt[], robot: SubAgentTask, place: number): QueuedPrompt[] {
  const name = agentNameOf(robot, place)
  return goals.filter(goal => isSameRobot(goal.robot || robotNamedIn(goal.text), name))
}

/** The robot a card's text names by its opening [for <robot name>]; empty when it names none. */
function robotNamedIn(text: string): string {
  if (!text.startsWith(ROBOT_MARK_OPEN) || !text.includes(']')) {
    return ''
  }
  return text.slice(ROBOT_MARK_OPEN.length, text.indexOf(']'))
}

/** Whether two robot names are one robot: an agent types a robot's name by hand, so case and outer spaces do not make
 * another robot, as the cdd server's queue matches them. */
function isSameRobot(given: string | undefined, name: string): boolean {
  const robot = (given ?? '').trim().toLowerCase()
  return robot !== '' && robot === name.trim().toLowerCase()
}

/** The robots on the queue, in the order their first card stands, each by the first spelling the queue holds of it, so
 * bOLT and Bolt are one robot. Each card keeps the robot it was given on the
 * queue, so the robots' queues come back after a reload; what a robot does is what grouping said, while the plugin
 * still holds it. */
export function robotsOf(goals: QueuedPrompt[], described: SubAgentTask[]): SubAgentTask[] {
  const names = goals.flatMap(goal => (goal.robot ? [goal.robot] : [])).filter((name, place, given) => given.findIndex(first => isSameRobot(first, name)) === place)
  return names.map(name => ({
    name,
    description: described.find(task => task.name === name)?.description ?? '',
    prompts: goals.filter(goal => isSameRobot(goal.robot, name)).map(goal => goal.text),
  }))
}

/** One `update_plan` call: the agent's task list follows it and is copied whole onto the prompt being worked. */
export async function followPlan($: EngineInterface, call: PlanCall): Promise<void> {
  await update($, isPlanSeen, () => true)
  await update($, plan, steps => keptInterruptions(steps, nextPlan(steps, call)))
  await copyPlanOntoWorkingPrompt($)
}

/** A new task list keeps the person's interruptions it does not list, so a message sent mid-work is not lost. */
function keptInterruptions(before: PromptStep[], after: PromptStep[]): PromptStep[] {
  const listed = new Set(after.map(step => step.text))
  return [...after, ...before.filter(step => step.text.startsWith(INTERRUPTION_MARK) && !listed.has(step.text))]
}

/** The agent gave a queued prompt its steps: that is the prompt it took, so it becomes the one being worked, and the
 * task list's next changes follow onto it from those steps. */
export async function followTakenPrompt($: EngineInterface, call: { prompt?: unknown; steps?: unknown }): Promise<void> {
  if (typeof call.prompt !== 'string' || call.prompt === '') {
    return
  }
  const steps = Array.isArray(call.steps) ? (call.steps as PromptStep[]) : []
  await update($, askedAbout, () => call.prompt as string)
  await update($, plan, () => steps)
  await refreshQueue($)
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
/** What + says when the prompt box is empty, since a card's new task is the prompt box's draft. */
const EMPTY_TASK_NOTICE = 'Type the task in the prompt box and send it, or press + again, to add it to this card.'

/** The card whose + was pressed on an empty prompt box: the next message sent becomes its task. */
const stepAwaitedBy = atom({ plugin: 'prompt-queue', key: 'stepAwaitedBy' } as const, '')

/** + on a card: the prompt box's draft becomes the prompt's last step, not started, and the box empties; the steps open.
 * With the box empty, + waits for the task: the next message sent becomes it (takeAwaitedStep). */
export async function addStep($: EngineInterface, prompt: QueuedPrompt): Promise<void> {
  const { text } = await $.prompt.read()
  if (text.trim() === '') {
    await update($, notice, () => EMPTY_TASK_NOTICE)
    await update($, stepAwaitedBy, () => prompt.id)
    return
  }
  await appendStep($, prompt, text)
  await $.prompt.fill({ text: '', mode: 'replace' })
}

/** A message sent while + waits on a card becomes that card's task instead of a prompt; answers whether it did. */
export async function takeAwaitedStep($: EngineInterface, text: string): Promise<boolean> {
  const awaited = await read($, stepAwaitedBy)
  if (awaited === '' || text.trim() === '') {
    return false
  }
  await update($, stepAwaitedBy, () => '')
  const prompt = (await read($, queue)).prompts.find(held => held.id === awaited)
  if (prompt === undefined) {
    await update($, notice, said => (said === EMPTY_TASK_NOTICE ? '' : said))
    return false
  }
  await appendStep($, prompt, text)
  return true
}

/** The text becomes the prompt's last step, not started, and its steps open. A done card opens again, since it has work
 * to run. */
async function appendStep($: EngineInterface, prompt: QueuedPrompt, text: string): Promise<void> {
  await update($, notice, said => (said === EMPTY_TASK_NOTICE ? '' : said))
  await update($, stepAwaitedBy, () => '')
  await changeSteps($, prompt, [...(prompt.steps ?? []), { text: text.trim(), state: 'pending' }])
  if (prompt.is_done) {
    await changeQueue($, 'reopen', { prompt: prompt.id })
  }
  await update($, openSteps, open => (open.includes(prompt.id) ? open : [...open, prompt.id]))
}

/** ✕ on a step: it comes off its prompt. */
export async function removeStep($: EngineInterface, prompt: QueuedPrompt, index: number): Promise<void> {
  await changeStepsBy($, prompt, 'remove_step', { step: index + 1 })
}

/** ↑ or ↓ on a step: it moves one place among its prompt's steps. */
export async function moveStep($: EngineInterface, prompt: QueuedPrompt, from: number, to: number): Promise<void> {
  await changeStepsBy($, prompt, 'move_step', { step: from + 1, place: to + 1 })
}

/** Runs one prompt-queue operation on a prompt's steps; for the prompt being worked the task list's next changes start
 * from the steps the server answered. */
async function changeStepsBy($: EngineInterface, prompt: QueuedPrompt, operation: string, args: Record<string, unknown> = {}): Promise<void> {
  if (!(await changeQueue($, operation, { prompt: prompt.id, ...args }))) {
    return
  }
  const changed = (await read($, queue)).prompts.find(held => held.id === prompt.id)
  if (prompt.id === (await read($, askedAbout))) {
    await update($, plan, () => changed?.steps ?? [])
  }
  await tellRobotOfSteps($, changed ?? prompt)
}

/** Gives a prompt its changed steps; for the prompt being worked the task list's next changes start from them. */
async function changeSteps($: EngineInterface, prompt: QueuedPrompt, steps: PromptStep[]): Promise<void> {
  if (prompt.id === (await read($, askedAbout))) {
    await update($, plan, () => steps)
  }
  if (await changeQueue($, 'set_steps', { prompt: prompt.id, steps })) {
    await tellRobotOfSteps($, { ...prompt, steps })
  }
}

/** A robot is told the steps of its card the person changed, numbered as step_done counts them. */
async function tellRobotOfSteps($: EngineInterface, card: QueuedPrompt): Promise<void> {
  const steps = (card.steps ?? []).map((step, place) => `${place + 1}. ${step.text}${step.state === 'done' ? ' (done)' : ''}`).join('; ')
  await tellRobotOfChange($, card, `its steps are now: ${steps || 'none'}`)
}

/** Pressing a robot opens its queue under it and closes the one that was open, so one queue shows at a time, and shows
 * its sub-agent's task in the main view, as picking it from the Claude pane's background tasks does; pressing it again
 * closes its queue to the robot alone and goes back to the main conversation. A robot whose sub-agent has not started
 * changes no view. */
export async function toggleAgentQueue($: EngineInterface, place: number): Promise<void> {
  const isOpening = !(await read($, expandedAgents)).includes(place)
  await update($, expandedAgents, () => (isOpening ? [place] : []))
  const robot = robotsOf((await read($, queue)).prompts, await read($, tasks))[place]
  const agentId = robot ? (await read($, robotAgents))[agentNameOf(robot, place)] : undefined
  if (agentId === undefined) {
    return
  }
  const shown = await $.ui.view(isOpening ? { agentId } : {})
  if (shown.deny !== undefined) {
    $.ui.toast(`${agentNameOf(robot!, place)}'s task is not shown: ${shown.deny}`)
  }
}

export async function toggleSteps($: EngineInterface, id: string): Promise<void> {
  await update($, openSteps, open => (open.includes(id) ? open.filter(shown => shown !== id) : [...open, id]))
}

/** The folded line of a card's finished steps: they show, or fold into the line again. */
export async function toggleDoneSteps($: EngineInterface, id: string): Promise<void> {
  await update($, shownDoneSteps, shown => (shown.includes(id) ? shown.filter(card => card !== id) : [...shown, id]))
}

/** Split on a card: the cdd server puts each interruption the goal holds and has not done on a card of its own, right
 * after the goal, as prompt-queue.split does for the agent. */
export async function splitGoal($: EngineInterface, prompt: QueuedPrompt): Promise<void> {
  await changeQueue($, 'split', { prompt: prompt.id })
}

/** Whether a goal holds an interruption not done yet, which split would put on a card of its own. */
export function hasInterruptionsToDo(prompt: QueuedPrompt): boolean {
  return (prompt.steps ?? []).some(step => step.text.startsWith(INTERRUPTION_MARK) && step.state !== 'done')
}

/** What a finished turn sends: the next prompt, or every task to its own sub-agent. */
export async function sendNext($: EngineInterface): Promise<void> {
  if (await read($, isSubAgentMode)) {
    await sendTasksToSubAgents($)
    return
  }
  await sendNextPrompt($)
}

/** The model groups the work not done and given to no robot yet into robots that can run side by side, and each card
 * is given its robot on the queue; robots already on the queue keep their names and cards. The person's interruptions
 * are left out, as this chat decides where each one goes. */
export async function groupIntoTasks($: EngineInterface): Promise<void> {
  const queued = new PromptQueue((await read($, queue)).prompts.filter(prompt => !prompt.is_done && !prompt.robot && !prompt.text.startsWith(INTERRUPTION_MARK)))
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
  await assignRobots($, parseJsonArray(reply.text) as SubAgentTask[])
  await update($, notice, () => '')
}

/** Each grouped task becomes a robot with a name no robot on the queue has, and each of its cards is given to it;
 * every robot's queue then closes, so the robots show as a plain list until one is pressed. */
async function assignRobots($: EngineInterface, grouped: SubAgentTask[]): Promise<void> {
  const goals = (await read($, queue)).prompts
  const names = freeRobotNames(goals, grouped.length)
  const named = grouped.map((task, place) => ({ ...task, name: names[place]! }))
  for (const robot of named) {
    for (const goal of goals.filter(goal => !goal.is_done && !goal.robot && robot.prompts.includes(goal.text))) {
      await changeQueue($, 'assign', { prompt: goal.id, robot: robot.name })
    }
  }
  await update($, tasks, described => [...described.filter(task => !named.some(robot => robot.name === task.name)), ...named])
  await update($, expandedAgents, () => [])
}

/** As many fun names as asked for, none of them a robot already on the queue. */
function freeRobotNames(goals: QueuedPrompt[], count: number): string[] {
  const taken = new Set(goals.flatMap(goal => (goal.robot ? [goal.robot] : [])))
  const free = AGENT_NAMES.filter(name => !taken.has(name))
  return Array.from({ length: count }, (_, place) => free[place] ?? `Robot ${taken.size + place + 1}`)
}

/** Fun names a sub-agent goes by, one for each place in turn, until the person names it. */
const AGENT_NAMES = ['Sparky', 'Bolt', 'Gizmo', 'Rivet', 'Pixel', 'Widget', 'Cog', 'Zap']

/** The name a sub-agent goes by: what the person called it, else the fun name for its place. */
export function agentNameOf(task: SubAgentTask, place: number): string {
  return task.name ?? AGENT_NAMES[place % AGENT_NAMES.length]!
}

/**
 * Sub-agent mode, playing: this chat is the orchestrator. Each robot whose last card is done, or that has had none, is
 * handed its next open card: this chat is asked to send the robot the card's words exactly, and to mark the card done
 * when the robot reports it finished. A robot whose next open card is the one it was last handed is still working it
 * and is passed over; one whose earlier card was opened again is handed that card. With nothing to hand out, this chat
 * is asked nothing. Work given to no robot is grouped first.
 */
export async function sendTasksToSubAgents($: EngineInterface): Promise<void> {
  await groupIntoTasks($)
  const held = (await read($, queue)).prompts
  const sent = await read($, sentCards)
  const handed: { robot: string; card: QueuedPrompt }[] = []
  for (const [place, task] of robotsOf(held.filter(prompt => !prompt.is_done), await read($, tasks)).entries()) {
    const robot = agentNameOf(task, place)
    const card = held.find(prompt => isSameRobot(prompt.robot, robot) && !prompt.is_done)
    if (card && card.id !== sent[robot]) {
      handed.push({ robot, card })
    }
  }
  if (handed.length === 0) {
    return
  }
  await update($, sentCards, cards => ({ ...cards, ...Object.fromEntries(handed.map(({ robot, card }) => [robot, card.id])) }))
  $.prompt.submit({ text: handOutOf(handed, await read($, robotAgents), await $.session.id()), asUser: true })
    .catch(thrown => showFailure($, `Not sent: ${reasonOf(thrown)}`, 'Playing the queue in sub-agent mode, asking this chat to hand out the robots\' cards'))
}

/** What this chat is asked when robots are due their next card: who gets which words, and how to hand them over. A
 * robot whose sub-agent is known is sent its words by that sub-agent's id; one not started yet is started with the
 * Agent tool, its description starting with the robot's name, so the queue learns which sub-agent is that robot. */
function handOutOf(handed: { robot: string; card: QueuedPrompt }[], agents: Record<string, string>, chat: string): string {
  return [
    "Hand out the robots' next cards. Send each robot its card's words exactly as written below, followed by one line: " +
      `"Before you start, break card [<card id>] into a discrete task list of your own plan, and put it on the card with prompt-queue.set_steps(chat=\\"${chat}\\", prompt=\\"<card id>\\", steps=[...]); ` +
      'keep it as your own task list too, and as you finish each task tick it with prompt-queue.step_done(chat, prompt, step=N), so the queue shows your progress."',
    'When a card already has steps, work them, adding or changing steps with prompt-queue.set_steps as the robot learns more.',
    'Tell each robot too: fix every failing test you meet, including one that failed before your change, and never report a failure as left because it was already there.',
    'When a robot tells you it finished, mark its card done with prompt-queue.done; its next card follows.',
    ...handed.map(({ robot, card }) => {
      const how = agents[robot]
        ? `SendMessage to ${agents[robot]}`
        : `start it with the Agent tool in the background, its description starting "${robot}: " and its prompt starting "Card [${card.id}]: "`
      return `- ${robot} (${how}), card [${card.id}]: ${card.text}`
    }),
  ].join('\n')
}

// How a sub-agent's prompt names the card it was started for, as the hand-out asks: Card [id].
const CARD_OF_PROMPT = /\bcard \[([^\]\s]+)\]/i
// The name a description starts with, before its colon, such as Robot 20 in "Robot 20: fix the review items".
const NAMED_DESCRIPTION = /^\s*([^:\n]{1,40}):\s*/

/** This chat starts a sub-agent for a robot: the card its prompt names, else the robot its description starts with.
 * The task then goes by that robot's name on the queue, whatever name this chat wrote, and the robot goes with the
 * sub-agent's id, so the robot's cards and the Claude pane's background task always name the same work. A sub-agent
 * for no robot starts as it was asked. */
export async function startRobotAgent($: EngineInterface, spawn: AgentSpawnInput, next: (spawn: AgentSpawnInput) => Promise<AgentSpawnResult>): Promise<AgentSpawnResult> {
  const robot = (await isQueueOn($)) ? await robotOfSpawn($, spawn) : undefined
  if (robot === undefined) {
    return next(spawn)
  }
  const started = await next({ ...spawn, description: `${robot}: ${spawn.description.replace(NAMED_DESCRIPTION, '')}` })
  const agentId = 'agentId' in started ? started.agentId : undefined
  if (agentId !== undefined) {
    await update($, robotAgents, agents => ({ ...agents, [robot]: agentId }))
    await noteCardHanded($, robot, spawn.prompt)
  }
  return started
}

/** This chat sent a robot's sub-agent a message naming a card: that card is handed out, so play does not hand it again. */
export async function followRobotMessage($: EngineInterface, call: Record<string, unknown>): Promise<void> {
  const to = typeof call.to === 'string' ? call.to : ''
  const robot = Object.entries(await read($, robotAgents)).find(([, id]) => id === to)?.[0]
  if (robot !== undefined && typeof call.message === 'string') {
    await noteCardHanded($, robot, call.message)
  }
}

/** The card words this chat gave a robot name, when it is a card on the queue, as the card that robot was handed. */
async function noteCardHanded($: EngineInterface, robot: string, words: string): Promise<void> {
  const card = CARD_OF_PROMPT.exec(words)?.[1]
  if (card !== undefined && (await read($, queue)).prompts.some(prompt => prompt.id === card)) {
    await update($, sentCards, cards => ({ ...cards, [robot]: card }))
  }
}

/** The robot on the queue a sub-agent is started for: the robot of the card its prompt names, else the robot whose
 * name its description starts with. */
async function robotOfSpawn($: EngineInterface, spawn: AgentSpawnInput): Promise<string | undefined> {
  const goals = (await read($, queue)).prompts
  const card = CARD_OF_PROMPT.exec(spawn.prompt)?.[1]
  const cardRobot = goals.find(goal => goal.id === card)?.robot
  if (cardRobot) {
    return cardRobot
  }
  const named = NAMED_DESCRIPTION.exec(spawn.description)?.[1]?.trim() ?? ''
  return robotsOf(goals, await read($, tasks)).map((task, place) => agentNameOf(task, place)).find(name => isSameRobot(named, name))
}

/**
 * `/queue [list or draft]`: a pasted list queues each of its items in order; a draft is placed into the plan, as a
 * task of a goal or a card of its own, as the `+` button does; with nothing given, the model reads this conversation
 * and proposes the ordered prompts to queue. Answers what it queued, and why it queued nothing when it did not.
 */
export async function queueFromCommand($: EngineInterface, args: string): Promise<string> {
  return (await runQueueCommand($, args)).said
}

async function runQueueCommand($: EngineInterface, args: string): Promise<QueueCommandResult> {
  const listed = listedItems(args)
  if (listed.length > 0) {
    await queueAll($, listed)
    return { isPlaced: true, said: `Queued ${listed.length} prompt(s).` }
  }
  if (args.trim() !== '') {
    return placeDraft($, args)
  }
  return { isPlaced: true, said: await planFromConversation($) }
}

async function planFromConversation($: EngineInterface): Promise<string> {
  const reply = await $.model.fork({ prompt: PLANNING_INSTRUCTIONS })
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

const PLANNING_INSTRUCTIONS =
  'Do not answer or do any of the work. From this conversation so far, list the next prompts the person ' +
  'should send, in the order they should run, each one a self-contained instruction a new turn can act on. ' +
  'Answer with only a JSON array of strings.'

const GROUPING_INSTRUCTIONS =
  'You are given a JSON array of prompts a person queued for a coding agent. Group them into tasks that ' +
  'independent sub-agents can run at the same time: prompts that depend on each other or touch the same ' +
  "work go in one task, kept in their order. A prompt that needs another prompt's result, such as reporting on a " +
  "test run or building on a change, goes in that prompt's task, so no sub-agent waits on another or hands its " +
  'result over; make as many tasks as can truly run at once, and no more. Answer with only a JSON array of ' +
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

/** The queue's pointer in a stack of cards: the place of the first card that waits, as the cdd server says each card
 * does (neither done nor asking a decision), past the last card when none waits. Play takes the card it points at. */
export function pointerOf(prompts: QueuedPrompt[]): number {
  const next = prompts.findIndex(prompt => prompt.is_waiting)
  return next === -1 ? prompts.length : next
}

/** ▲ on the pointer: the nearest done card above it opens again, its steps not started, so play runs it again. */
export async function movePointerUp($: EngineInterface, prompts: QueuedPrompt[]): Promise<void> {
  const above = prompts.slice(0, pointerOf(prompts)).filter(prompt => prompt.is_done).at(-1)
  if (!above) {
    return
  }
  await changeQueue($, 'reopen', { prompt: above.id })
  await update($, askedAbout, working => (working === above.id ? '' : working))
}

/** ▼ on the pointer: the card it points at is marked done, so play moves past it. */
export async function movePointerDown($: EngineInterface, prompts: QueuedPrompt[]): Promise<void> {
  const pointed = prompts[pointerOf(prompts)]
  if (pointed) {
    await changeQueue($, 'done', { prompt: pointed.id })
  }
}

/** ▲ on a card's step pointer: the done step above it is worked again, and every step after it is not started. */
export async function moveStepPointerUp($: EngineInterface, prompt: QueuedPrompt): Promise<void> {
  await changeStepsBy($, prompt, 'step_back')
}

/** ▼ on a card's step pointer: its step is done and the next step is the one worked. */
export async function moveStepPointerDown($: EngineInterface, prompt: QueuedPrompt): Promise<void> {
  await changeStepsBy($, prompt, 'step_on')
}

/** The answer of a prompt-queue call the agent or a sub-agent made: the queue as the server now holds it, drawn at once,
 * so the cards, the pointer and the working mark keep up with the agent instead of waiting for the mod's next read. */
export async function followQueueAnswer($: EngineInterface, ran: unknown): Promise<void> {
  const text = (ran as { result?: { content?: { text?: string }[] } } | undefined)?.result?.content?.[0]?.text ?? ''
  const answered = parseQueueAnswer(text)
  if (!answered) {
    return
  }
  const held = await read($, queue)
  if (held.chat !== '' && answered.chat !== held.chat) {
    return
  }
  await update($, queue, () => answered)
}

function parseQueueAnswer(text: string): QueueJson | undefined {
  try {
    const parsed = JSON.parse(text) as Partial<QueueJson>
    return typeof parsed.chat === 'string' && Array.isArray(parsed.prompts) ? (parsed as QueueJson) : undefined
  } catch (thrown) {
    if (thrown instanceof SyntaxError) {
      return undefined
    }
    throw thrown
  }
}

/** ↵ on a step: that step of its prompt goes to the chat at once, the prompt being worked. */
export async function sendStepNow($: EngineInterface, prompt: QueuedPrompt, index: number): Promise<void> {
  const step = (prompt.steps ?? [])[index]
  if (!step) {
    return
  }
  await workOn($, prompt.id)
  $.prompt.submit({ text: `Take step ${index + 1} of prompt [${prompt.id}] on the queue now: ${step.text}`, asUser: true }).catch(thrown =>
    showFailure($, `Not sent: ${reasonOf(thrown)}`, `Pressing send now on the step "${step.text}"`))
}

/** ✎ on a step: with the prompt box empty, the step's text goes to the box to change; with a draft there, the draft
 * becomes the step's text and the box empties. */
export async function editStep($: EngineInterface, prompt: QueuedPrompt, index: number): Promise<void> {
  const steps = prompt.steps ?? []
  const step = steps[index]
  if (!step) {
    return
  }
  const { text } = await $.prompt.read()
  if (text.trim() === '') {
    await $.prompt.fill({ text: step.text, mode: 'replace' })
    return
  }
  await changeSteps($, prompt, steps.map((held, place) => (place === index ? { ...held, text: text.trim() } : held)))
  await $.prompt.fill({ text: '', mode: 'replace' })
}
