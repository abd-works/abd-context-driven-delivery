import type { EngineInterface } from 'claude-code'

import { after } from './board-chat/board'
import { reasonOf } from './failure'

// The engine queues a plugin's prompt or slash command until the chat is idle, the same queue a person's Ctrl+Enter
// uses, and either resolves only once it has run. It refuses one it will not take straight away, so one not refused by
// now waits in that queue or is running.
export const REFUSED_WITHIN_MILLISECONDS = 3_000

// A slash command as $.command.run takes it: the name without its slash, and the rest of the words as its arguments.
export function commandOf(text: string): { command: string; args: string } {
  const [command = '', ...words] = text.slice(1).split(' ')
  return { command, args: words.join(' ') }
}

// Adds to the prompt box, so a draft the person is typing stays. Nothing once it did, else why not.
export async function filledPrompt($: EngineInterface, text: string): Promise<string> {
  const answer = await $.prompt.fill({ text, mode: 'append' })
  return answer.isFilled ? '' : `the prompt box did not take it (${answer.refusal ?? 'refused by a hook'})`
}

// Sends a slash command to this chat as the board's Run does: it runs as if the person typed it, its line in the
// transcript. The engine refuses a plugin's command in some states, such as after the person stopped the session and
// has typed nothing since; the command then waits in the prompt box for the person to send, so it is never lost.
export async function sendToChat($: EngineInterface, text: string): Promise<void> {
  const refusal = await Promise.race([$.command.run(commandOf(text)).then(() => '', reasonOf), after($, REFUSED_WITHIN_MILLISECONDS, '')])
  if (!refusal) return
  const unfilled = await filledPrompt($, text).catch(reasonOf)
  $.ui.toast(unfilled ? `The chat would not run ${text}: ${refusal}; ${unfilled}` : `The chat would not run ${text} (${refusal}), so it is in the prompt box: press Enter to send it`)
}
