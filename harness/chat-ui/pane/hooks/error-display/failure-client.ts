import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { FailureData } from '@cdd/tools/error_display/failure'

import type { FailureJson } from '../../types'
import { commandOf } from '../shared/chat-command'
import { debugCommandOf } from '../shared/debug-command'

// Every failure in the mod is shown the same way, above the chat bar's line: what failed with the reason it gave, the
// context it failed in, Fix, which sends both to this chat to find the cause and fix it, and ✕ to dismiss it. It stays
// until the person fixes or dismisses it, since a toast passes before anyone reads it. The shape is tools/error_display's
// Failure; the mod builds it itself, since a failure must show while the cdd server is what is broken.
const shownFailure = atom({ plugin: 'cdd-board', key: 'failure' } as const, null as FailureJson)

export class FailureClient {
  constructor(private readonly json: FailureData) {}

  get failure(): string {
    return this.json.failure
  }

  get context(): string {
    return this.json.context
  }

  // Whether Fix was pressed and its prompt is on its way into the chat: the line shows Claude working instead of Fix.
  get isFixing(): boolean {
    return Boolean((this.json as FailureData & { is_fixing?: boolean }).is_fixing)
  }

  // What Fix sends to the chat: the debug command with the failure and its context, which captures what went wrong,
  // fixes it in a sub-agent, and pushes the fix to main, or opens a pull request where the person cannot push there.
  get fixPrompt(): string {
    return debugCommandOf('', `The CDD chat bar above the prompt shows this failure. Failure: ${this.failure} Context: ${this.context}`)
  }
}

// The words a failure carries: the server's own text for a failed cdd tool, a thrown error's message otherwise.
export function reasonOf(failure: unknown): string {
  return failure instanceof Error ? failure.message : String(failure)
}

export async function currentFailure($: EngineInterface): Promise<FailureClient | null> {
  const json = await read($, shownFailure)
  return json ? new FailureClient(json as FailureData) : null
}

// Shows a failure above the line: what failed, with the reason the thrown failure gave when there is one, and the
// context it failed in, such as the button pressed and the tool it called.
export async function showFailure($: EngineInterface, failure: string, context: string, thrown?: unknown): Promise<void> {
  const said = thrown === undefined ? failure : `${failure}: ${reasonOf(thrown)}`
  await update($, shownFailure, () => ({ failure: said, context }))
}

// A catch handler that shows what it caught: `.catch(shownAsFailure($, 'The board did not load', 'Reading the board'))`.
export function shownAsFailure($: EngineInterface, failure: string, context: string): (thrown: unknown) => Promise<void> {
  return thrown => showFailure($, failure, context, thrown)
}

// A slash command runs as if the person typed it, as the board's commands do: the engine refuses a submitted prompt that
// starts with a slash. Any other text arrives as the person's own message.
function sentToChat($: EngineInterface, text: string): Promise<unknown> {
  return text.startsWith('/') ? $.command.run(commandOf(text)) : $.prompt.submit({ text, asUser: true })
}

export async function dismissFailure($: EngineInterface): Promise<void> {
  await update($, shownFailure, () => null)
}

// Fix sends the failure and its context to this chat's agent and clears it from the line.
// Until the prompt is in the chat the line shows Claude working in place of Fix, so a second press cannot send it twice;
// a prompt the chat did not take is a failure of its own, shown in place of the one it was fixing.
export async function fixFailure($: EngineInterface, failure: FailureClient): Promise<void> {
  if (failure.isFixing) return
  await update($, shownFailure, json => (json ? { ...json, is_fixing: true } : json))
  try {
    await sentToChat($, failure.fixPrompt)
  } catch (thrown) {
    return showFailure($, 'The fix did not reach the chat', `Pressing Fix on: ${failure.failure}`, thrown)
  }
  await dismissFailure($)
}
