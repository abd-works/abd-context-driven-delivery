import type { ChatCommandData } from '@cdd/harness/chat/chat'
import type { EngineInterface } from 'claude-code'

import { commandOf, filledPrompt, REFUSED_WITHIN_MILLISECONDS } from '../shared/chat-command'
import { reasonOf } from '../shared/failure'
import { after, post } from './board'
import { currentChatName } from './chat-name'
import { awaitTurn, finish, forgetTurn, isChatBusy, turnsSoFar } from './chat-turns'

// Connects this chat to cdd's chat tools, which the board sends commands through. The rules live in the cdd server.

// A slash command runs as if the person typed it, its line in the transcript; the engine refuses a submitted prompt
// that starts with a slash.
function ranCommand($: EngineInterface, chat: string, command: ChatCommandData): Promise<string> {
  const turnsBefore = turnsSoFar()
  const running = $.command.run(commandOf(command.text)).then(() => '', reasonOf)
  // A command that printed its line and started no turn, such as /board, is done once it returns.
  void running.then(reason => {
    if (!reason && turnsSoFar() === turnsBefore && !isChatBusy()) void finish($, chat, command.message)
  })
  return Promise.race([running, after($, REFUSED_WITHIN_MILLISECONDS, '')])
}

// Any other text arrives as the person's own message, the same as typing it.
function submitted($: EngineInterface, text: string): Promise<string> {
  const submitting = $.prompt.submit({ text, asUser: true }).then(answer => (answer.drop === undefined ? '' : `the chat dropped it: ${answer.drop || 'no reason given'}`), reasonOf)
  return Promise.race([submitting, after($, REFUSED_WITHIN_MILLISECONDS, '')])
}

// The engine refuses a plugin's command in some states, such as after the person stopped the session and has typed
// nothing since. The command then waits in the prompt box for the person to send, so it is never lost; once they send
// it, its turn finishes it like any other.
async function ranOrFilled($: EngineInterface, chat: string, command: ChatCommandData): Promise<string> {
  const refusal = await ranCommand($, chat, command)
  if (!refusal) return ''
  const unfilled = await filledPrompt($, command.text).catch(reasonOf)
  if (unfilled) return `${refusal}; ${unfilled}`
  $.ui.toast(`The chat would not run ${command.text} (${refusal}), so it is in the prompt box: press Enter to send it`)
  return ''
}

// Why the chat did not show the command, or nothing once it did.
function shown($: EngineInterface, chat: string, command: ChatCommandData): Promise<string> {
  if (command.kind === 'fill') return filledPrompt($, command.text).catch(reasonOf)
  return command.text.startsWith('/') ? ranOrFilled($, chat, command) : submitted($, command.text)
}

// The board shows each message as shown or failed, so a message the chat could not take is never silent. A fill waits
// for the person to send it, so only a command or a submit has work for the chat to finish.
async function run($: EngineInterface, chat: string, command: ChatCommandData): Promise<void> {
  const hasTurn = command.kind === 'command' || command.kind === 'submit'
  $.ui.toast(`Board message arrived: ${command.text}`)
  if (hasTurn) awaitTurn(command.message)
  const reason = await shown($, chat, command)
  $.ui.toast(reason ? `Board message failed: ${reason}: ${command.text}` : `Board sent: ${command.text}`)
  if (reason) forgetTurn(command.message)
  await post($, { chat, operation: 'confirm', body: { message: command.message, is_shown: !reason, reason } })
}

// Checks in through the board, which runs chat.check_in on the cdd server every chat shares. The folder the chat works in
// lets the board find a ticket's chat: the one working in the ticket's worktree.
export async function checkIn($: EngineInterface, chat: string): Promise<void> {
  const answer = await post($, { chat, operation: 'check-in', body: { is_busy: isChatBusy(), name: currentChatName(), folder: await $.session.root() } })
  if (!answer.ok) return
  for (const command of JSON.parse(answer.text) as ChatCommandData[]) await run($, chat, command)
}
