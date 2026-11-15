import type { ChatCommandData } from '@cdd/harness/chat/chat'
import type { EngineInterface } from 'claude-code'

import { refreshChatBar } from '../chat-bar/chat-bar-client'
import { openFileInViewer } from '../chat-bar/fidelity-files-client'
import { selectedFidelitySlugs, selectFidelities } from '../chat-bar/fidelity-progress-client'
import { commandOf, filledPrompt, REFUSED_WITHIN_MILLISECONDS } from '../shared/chat-command'
import { reasonOf, showFailure } from '../error-display/failure-client'
import { after, post } from './board'
import { currentChatName } from './chat-name'
import { awaitTurn, chatWorked, finish, forgetTurn, isChatBusy, turnsSoFar } from './chat-turns'

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

// Why the chat did not show the command, or nothing once it did. A file to open is shown in the chat bar's file viewer,
// never in the chat: a Story UI editor this chat opened sends a story's acceptance test so.
function shown($: EngineInterface, chat: string, command: ChatCommandData): Promise<string> {
  if (command.kind === 'open_file') return openFileInViewer($, command.text).then(() => '', reasonOf)
  if (command.kind === 'fill') return filledPrompt($, command.text).catch(reasonOf)
  // A kind this bar does not know is refused, never submitted: an older bar submitted a refresh's text as the
  // person's own message.
  if (command.kind !== 'command' && command.kind !== 'submit') return Promise.resolve(`this chat bar does not know the command kind ${command.kind}: run /reload-plugins`)
  return command.text.startsWith('/') ? ranOrFilled($, chat, command) : submitted($, command.text)
}

// The board shows each message as shown or failed, so a message the chat could not take is never silent. A fill waits
// for the person to send it, so only a command or a submit has work for the chat to finish.
async function run($: EngineInterface, chat: string, command: ChatCommandData): Promise<void> {
  if (command.kind === 'refresh') return refreshed($, chat, command)
  if (command.kind === 'select') return selected($, chat, command)
  if (command.kind === 'failure') return failed($, chat, command)
  const hasTurn = command.kind === 'command' || command.kind === 'submit'
  $.ui.toast(`Board message arrived: ${command.text}`)
  if (hasTurn) awaitTurn(command.message)
  const reason = await shown($, chat, command)
  if (reason) await showFailure($, `Board message failed: ${reason}`, `A ${command.kind} the board sent to this chat: ${command.text}`)
  else $.ui.toast(`Board sent: ${command.text}`)
  if (reason) forgetTurn(command.message)
  await post($, { chat, operation: 'confirm', body: { message: command.message, is_shown: !reason, reason } })
}

// A refresh reads the board again, with no toast: a page such as the Files app turned a practice on or off for the
// session, which the bar shows only after it reads the board.
async function refreshed($: EngineInterface, chat: string, command: ChatCommandData): Promise<void> {
  const reason = await refreshChatBar($).then(() => '', reasonOf)
  if (reason) await showFailure($, `The chat bar did not read the board again: ${reason}`, `A refresh ${command.text} sent to this chat`)
  await post($, { chat, operation: 'confirm', body: { message: command.message, is_shown: !reason, reason } })
}

// A select puts the fidelities a page named in place of the bar's selection, with no toast: a practice pressed in the
// Files app selects or clears its dots here.
async function selected($: EngineInterface, chat: string, command: ChatCommandData): Promise<void> {
  await selectFidelities($, command.text.split(',').filter(Boolean))
  await post($, { chat, operation: 'confirm', body: { message: command.message, is_shown: true, reason: '' } })
}

// A page the chat opened, such as the Files app, failed: its failure shows on the chat bar as the bar's own do, where
// the person can have the chat fix it.
async function failed($: EngineInterface, chat: string, command: ChatCommandData): Promise<void> {
  const { failure, context } = JSON.parse(command.text) as { failure: string; context: string }
  await showFailure($, failure, context)
  await post($, { chat, operation: 'confirm', body: { message: command.message, is_shown: true, reason: '' } })
}

// Checks in through the board, which runs chat.check_in on the cdd server every chat shares. The folder the chat works in
// lets the board find a ticket's chat: the one working in the ticket's worktree. The fidelities selected on the chat bar
// go with it, so a page the chat opened, such as the Files app, shows the same ones.
export async function checkIn($: EngineInterface, chat: string): Promise<void> {
  const body = { is_busy: isChatBusy(), name: currentChatName(), folder: await $.session.root(), selected_fidelities: await selectedFidelitySlugs($) }
  const answer = await post($, { chat, operation: 'check-in', body })
  if (!answer.ok) return
  const commands = JSON.parse(answer.text) as ChatCommandData[]
  if (commands.length) chatWorked()
  for (const command of commands) await run($, chat, command)
}
