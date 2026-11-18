import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { FailureData } from '@cdd/tools/error_display/failure'

import type { FailureJson, QueueFailureJson } from '../../types'
import { commandOf, filledPrompt } from '../shared/chat-command'
import { debugCommandOf } from '../shared/debug-command'
import { reasonOf } from '../shared/reason'

// Every failure in the mod is shown the same way, above the chat bar's line: what failed with the reason it gave, the
// context it failed in, Fix, which sends both to this chat to find the cause and fix it, and ✕ to dismiss it. It stays
// until the person fixes or dismisses it, since a toast passes before anyone reads it. The shape is tools/error_display's
// Failure; the mod builds it itself, since a failure must show while the cdd server is what is broken.
const shownFailure = atom({ plugin: 'cdd-board', key: 'failure' } as const, null as FailureJson)
// The prompt queue's failures show on this line too. The queue keeps its latest failure itself, since only a value's
// owner writes it, and Fix and ✕ on it hide it here by keeping its id.
const queueFailure = atom({ plugin: 'prompt-queue', key: 'failure' } as const, null as QueueFailureJson)
const handledQueueFailure = atom({ plugin: 'cdd-board', key: 'handledQueueFailure' } as const, 0)

type ShownFailureData = FailureData & { is_fixing?: boolean; queue_failure_id?: number }

export class FailureClient {
  constructor(private readonly json: ShownFailureData) {}

  get failure(): string {
    return this.json.failure
  }

  get context(): string {
    return this.json.context
  }

  // Whether Fix was pressed and its prompt is on its way into the chat: the line shows Claude working instead of Fix.
  get isFixing(): boolean {
    return Boolean(this.json.is_fixing)
  }

  // The id of the prompt queue's failure this is, which Fix and ✕ hide; undefined for the board's own.
  get queueFailureId(): number | undefined {
    return this.json.queue_failure_id
  }

  // What Fix sends to the chat: the debug command with the failure and its context, which captures what went wrong,
  // fixes it in a sub-agent, and pushes the fix to main, or opens a pull request where the person cannot push there.
  get fixPrompt(): string {
    return debugCommandOf('', `The CDD chat bar above the prompt shows this failure. Failure: ${this.failure} Context: ${this.context}`)
  }
}

// The board's own failure first; otherwise the prompt queue's latest, unless Fix or ✕ already handled it.
export async function currentFailure($: EngineInterface): Promise<FailureClient | null> {
  const json = await read($, shownFailure)
  if (json) return new FailureClient(json as FailureData)
  const queued = await read($, queueFailure)
  if (!queued || queued.id === (await read($, handledQueueFailure))) return null
  return new FailureClient({ failure: queued.failure, context: queued.context, queue_failure_id: queued.id })
}

// Shows a failure above the line: what failed and the context it failed in, such as the button pressed and the tool it
// called. A failure something threw is shown through shownAsFailure, which adds the reason it gave.
export async function showFailure($: EngineInterface, failure: string, context: string): Promise<void> {
  await update($, shownFailure, () => ({ failure, context }))
}

// A catch handler that shows what it caught, with the reason it gave:
// `.catch(shownAsFailure($, 'The board did not load', 'Reading the board'))`.
export function shownAsFailure($: EngineInterface, failure: string, context: string): (thrown: unknown) => Promise<void> {
  return thrown => showFailure($, `${failure}: ${reasonOf(thrown)}`, context)
}

// A slash command runs as if the person typed it, as the board's commands do: the engine refuses a submitted prompt that
// starts with a slash. Any other text arrives as the person's own message.
function sentToChat($: EngineInterface, text: string): Promise<unknown> {
  return text.startsWith('/') ? $.command.run(commandOf(text)) : $.prompt.submit({ text, asUser: true })
}

export async function dismissFailure($: EngineInterface, failure: FailureClient): Promise<void> {
  const queueFailureId = failure.queueFailureId
  if (queueFailureId === undefined) {
    await update($, shownFailure, () => null)
    return
  }
  await update($, handledQueueFailure, () => queueFailureId)
}

// Fix sends the failure and its context to this chat's agent and clears it from the line.
// Until the prompt is in the chat the line shows Claude working in place of Fix, so a second press cannot send it twice;
// a prompt the chat did not take is a failure of its own, shown in place of the one it was fixing.
export async function fixFailure($: EngineInterface, failure: FailureClient): Promise<void> {
  if (failure.isFixing) return
  if (failure.queueFailureId !== undefined) return fixQueueFailure($, failure)
  await update($, shownFailure, json => (json ? { ...json, is_fixing: true } : json))
  try {
    await sentToChat($, failure.fixPrompt)
  } catch (thrown) {
    return shownAsFailure($, 'The fix did not reach the chat', `Pressing Fix on: ${failure.failure}`)(thrown)
  }
  await dismissFailure($, failure)
}

// Fix on the prompt queue's failure hides it first, since the queue's value cannot show the fix on its way; a prompt
// the chat did not take shows as the board's own failure.
async function fixQueueFailure($: EngineInterface, failure: FailureClient): Promise<void> {
  await dismissFailure($, failure)
  await sentToChat($, failure.fixPrompt).catch(shownAsFailure($, 'The fix did not reach the chat', `Pressing Fix on: ${failure.failure}`))
}

// Puts a slash command in the prompt box the moment a button is pressed, as the handoff button does, and the person
// presses Enter to send it. Running it straight away waits until the chat is idle, so a press showed nothing for a
// long time.
export async function promptCommand($: EngineInterface, command: string): Promise<void> {
  const unfilled = await promptOf($, command).then(prompt => filledPrompt($, prompt)).catch(reasonOf)
  if (unfilled) await showFailure($, `${command} could not go in the prompt box: ${unfilled}`, `Pressing the button that puts ${command} in the prompt box`)
}

// What goes in the prompt box for command: the command itself while the chat has loaded its skill. A chat whose folder
// had no CDD install when it last read its skills has not, and the prompt box marks the slash command "not a command"
// and sends it as plain text; it then goes in as a plain request the agent runs through the tool its skill names, and a
// toast says why.
async function promptOf($: EngineInterface, command: string): Promise<string> {
  const name = commandOf(command).command
  if ((await $.command.list()).some(each => each.name === name)) return command
  $.ui.toast(`This chat has not loaded the CDD skill ${name}: CDD was not installed in this folder when the chat read its skills. The request goes in as plain text, which the agent runs through the tool the skill names; install CDD here and its skills load.`)
  return `Run the CDD skill ${name}, which this chat has not loaded, through the MCP tool or script its SKILL.md names: ${command.slice(1)}`
}
