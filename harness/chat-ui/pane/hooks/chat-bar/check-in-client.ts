import type { ChatCommandData } from '@cdd/harness/chat/chat'
import type { EngineInterface } from 'claude-code'

import { commandOf, filledPrompt, REFUSED_WITHIN_MILLISECONDS } from '../shared/chat-command'
import { showFailure, shownAsFailure } from '../error-display/failure-client'
import { reasonOf } from '../shared/reason'
import { chatTool, post } from '../board-chat/board'
import { CddToolFailed, replyOf } from '../shared/cdd-tool'
import { currentChatName } from '../board-chat/chat-name'
import { awaitTurn, chatWorked, finish, forgetTurn, isChatBusy, turnsSoFar } from '../board-chat/chat-turns'
import { after } from '../shared/clock'
import { refreshChatBar } from './chat-bar-client'
import { openFileInViewer } from './fidelity-files-client'

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

// A refresh reads the board and the format chips again, with no toast: a page such as the Files app turned a practice
// or a format on or off for the session, which the bar shows only after it reads them.
async function refreshed($: EngineInterface, chat: string, command: ChatCommandData): Promise<void> {
  const reason = await refreshChatBar($)
    .then(() => '', reasonOf)
  if (reason) await showFailure($, `The chat bar did not read the board again: ${reason}`, `A refresh ${command.text} sent to this chat`)
  await post($, { chat, operation: 'confirm', body: { message: command.message, is_shown: !reason, reason } })
}

// A page the chat opened, such as the Files app, failed: its failure shows on the chat bar as the bar's own do, where
// the person can have the chat fix it.
async function failed($: EngineInterface, chat: string, command: ChatCommandData): Promise<void> {
  const { failure, context } = failureSentIn(command)
  await showFailure($, failure, context)
  await post($, { chat, operation: 'confirm', body: { message: command.message, is_shown: true, reason: '' } })
}

// The failure and its context a page sent, as the text of its failure command.
function failureSentIn(command: ChatCommandData): { failure: string; context: string } {
  return JSON.parse(command.text) as { failure: string; context: string }
}

// How many check-ins in a row may fail before the bar shows it: a cdd server restarting, as a repin restarts it, drops
// the call in flight, and the check-in a second later answers again. Ten failed in a row is a cdd that is not coming back.
const FAILED_CHECK_INS_SHOWN = 10
let failedCheckIns = 0

// The check-in every second, or, between an idle chat's check-ins, the read of its selection: a failure shows once it
// keeps happening, with the reason the last one gave and how long it has gone on.
export async function keepInTouch($: EngineInterface, chat: string, isCheckIn: boolean): Promise<void> {
  try {
    if (!isCheckIn) return
    await checkIn($, chat)
    failedCheckIns = 0
  } catch (failure) {
    failedCheckIns += 1
    if (failedCheckIns !== FAILED_CHECK_INS_SHOWN) return
    await shownAsFailure($, `This chat has not reached cdd for ${FAILED_CHECK_INS_SHOWN} check-ins`, 'The check-in every second, calling chat.check_in')(namedFailure(failure))
  }
}

// A failed cdd tool shows the server's own text under the tool's name, such as "chat.check_in failed: LaneUnreachable:
// ...", so the person reads why the server failed rather than what the bar made of its answer.
function namedFailure(failure: unknown): unknown {
  return failure instanceof CddToolFailed ? `${failure.tool} failed: ${failure.message}` : failure
}

// Checks in with cdd every second: whether a turn is running, what to call the chat, and the folder it works in, which
// lets the board find a ticket's chat. The dots then draw the selection cdd holds for the chat, which a page the chat
// opened, such as the Files app, may have changed.
export async function checkIn($: EngineInterface, chat: string): Promise<void> {
  const commands = await waitingCommands($, chat)
  if (commands.length) chatWorked()
  for (const command of commands) await run($, chat, command)
}

// The commands waiting for this chat, which chat.check_in answers once it has recorded the chat's state. An answer that
// is not the commands' JSON is the server's failure text, a CddToolFailed.
async function waitingCommands($: EngineInterface, chat: string): Promise<ChatCommandData[]> {
  const answer = await post($, { chat, operation: 'check-in', body: { is_busy: isChatBusy(), name: currentChatName(), folder: await $.session.root() } })
  return replyOf<ChatCommandData[]>(chatTool('check-in'), answer)
}
