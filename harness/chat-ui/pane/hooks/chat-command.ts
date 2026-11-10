import type { EngineInterface } from 'claude-code'

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

// Puts slash commands in the prompt box the moment a button is pressed, as the handoff button does, and the person
// presses Enter to send them. Running them straight away waits until the chat is idle, so a press showed nothing for a
// long time. A prompt holds one slash command, so the first goes in the box and the person is told the rest.
export async function promptCommands($: EngineInterface, commands: string[]): Promise<void> {
  const [first, ...rest] = commands
  if (!first) return
  const unfilled = await filledPrompt($, first).catch(reasonOf)
  if (unfilled) return $.ui.toast(`${first} could not go in the prompt box: ${unfilled}`)
  if (rest.length) $.ui.toast(`After ${first}, send ${rest.join(', then ')}`)
}
