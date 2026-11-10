import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { ChatFolderJson } from '../../types'
import { isChatBusy, turnsSoFar } from '../board-chat/chat-turns'
import { reasonOf } from '../shared/failure'
import { dismissFailure, showFailure, type ChatBarClient } from './chat-bar-client'

// Where this chat works against where the active session's work is: the ticket's own worktree, else the repository's
// main checkout, where activating it checked its branch out. A switch made in the chat bar moves the chat there with
// Claude Code's own /cd; one made elsewhere shows in the band until the person moves it.
const chatFolder = atom({ plugin: 'cdd-board', key: 'chatFolder' } as const, { current: '', expected: '' } as ChatFolderJson)

// Windows names one folder with either slash and any case, so a folder is compared in one spelling.
const spelled = (folder: string): string => folder.split('\\').join('/').replace(/\/+$/, '').toLowerCase()
const sameFolder = (one: string, other: string): boolean => spelled(one) === spelled(other)

// Atom chatFolder, declared in pane/types/index.d.ts and kept in this file.
export async function currentChatFolder($: EngineInterface): Promise<ChatFolderJson & { isElsewhere: boolean }> {
  const folder = await read($, chatFolder)
  return { ...folder, isElsewhere: Boolean(folder.current && folder.expected && !sameFolder(folder.current, folder.expected)) }
}

// The folder holding a .git folder git names, in git's own spelling.
const spelledAsGiven = (gitFolder: string): string => gitFolder.split('\\').join('/').replace(/\/\.git$/, '')

// The repository's main checkout, which every worktree shares: the folder holding its .git.
async function mainCheckoutOf($: EngineInterface): Promise<string> {
  const { exitCode, stdout } = await $.process.run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'])
  return exitCode === 0 ? spelledAsGiven(stdout.trim()) : ''
}

// The folder the active session's work is in: its ticket's worktree, else the main checkout.
async function workFolderOf($: EngineInterface, chatBar: ChatBarClient): Promise<string> {
  return chatBar.worktree || (await mainCheckoutOf($))
}

// Reads where the chat is and where the active session's work is, so the band can say when they differ.
export async function checkChatFolder($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  const [current, expected] = await Promise.all([$.session.cwd(), workFolderOf($, chatBar)])
  await update($, chatFolder, () => ({ current, expected }))
}

// The desktop app moves a chat when the agent's turn ends. A chat still not there this long after the turn that was
// asked to move it has ended was refused, so the person hears so then instead of waiting on a fixed timeout.
const MOVE_AFTER_TURN_MILLISECONDS = 3_000
const MOVE_CHECK_MILLISECONDS = 500

// Where the move was asked of: /cd moves at once; the agent moves the chat when a turn started after the ask ends.
type MoveAsked = { byAgent: boolean; turnsBefore: number }

// Moves this chat to the main checkout before a worktree it may be working in is deleted, and waits until it is there:
// a chat still in the worktree holds its folder open, so the delete fails halfway. Answers why the chat is not in the
// main checkout, or '' once it is.
export async function moveToMainCheckout($: EngineInterface): Promise<string> {
  const [current, main] = await Promise.all([$.session.cwd(), mainCheckoutOf($)])
  if (!main) return `git found no main checkout from ${current}`
  if (sameFolder(current, main)) return ''
  const asked = await moveChatTo($, main)
  if (!asked) return `this chat did not move out of ${current}`
  return (await arrivedIn($, main, asked)) ? '' : `the app did not move this chat out of ${current}, so its worktree is held open`
}

// True once the chat is in folder; false once the move had its chance: the asked turn ended and the app still had not.
async function arrivedIn($: EngineInterface, folder: string, asked: MoveAsked): Promise<boolean> {
  let sinceTurnEnded = 0
  while (sinceTurnEnded < MOVE_AFTER_TURN_MILLISECONDS) {
    if (sameFolder(await $.session.cwd(), folder)) return true
    await $.clock.sleep(MOVE_CHECK_MILLISECONDS)
    // The app moves the chat once it is idle, so a turn that starts after the asked one (a second move request, a
    // queued prompt) starts the count again instead of being counted against the move.
    sinceTurnEnded = askedTurnEnded(asked) ? sinceTurnEnded + MOVE_CHECK_MILLISECONDS : 0
  }
  return false
}

// The app sometimes moves the chat later than the grace period, such as while it reconnects the folder's MCP servers.
// The failure shows at once, and is taken back if the chat arrives after all, so a move that worked never reads as one
// that failed.
const LATE_MOVE_MILLISECONDS = 60_000

async function reportLateMove($: EngineInterface, folder: string): Promise<void> {
  await showFailure($, `The app did not move this chat to ${folder}`)
  for (let waited = 0; waited < LATE_MOVE_MILLISECONDS; waited += MOVE_CHECK_MILLISECONDS) {
    if (sameFolder(await $.session.cwd(), folder)) return dismissFailure($)
    await $.clock.sleep(MOVE_CHECK_MILLISECONDS)
  }
}

function askedTurnEnded(asked: MoveAsked): boolean {
  return !asked.byAgent || (turnsSoFar() > asked.turnsBefore && !isChatBusy())
}

// Claude Code's /cd moves the chat where the session offers it. The desktop app offers no /cd: there the chat's folder
// changes through the app's change_directory tool, which only the agent can call, so the agent is asked to.
async function moveChatTo($: EngineInterface, folder: string): Promise<MoveAsked | null> {
  const turnsBefore = turnsSoFar()
  try {
    const hasCd = (await $.command.list()).some(command => command.name === 'cd')
    if (hasCd) await $.command.run({ command: 'cd', args: folder })
    else await askAgentToMove($, folder)
    return { byAgent: !hasCd, turnsBefore }
  } catch (failure) {
    await showFailure($, `This chat did not move to ${folder}: ${reasonOf(failure)}`)
    return null
  }
}

// The desktop app rewrites a Windows path to backslashes before change_directory runs, and auto mode refuses a call
// whose input changed after it was reviewed; asking in the spelling the app uses leaves nothing to rewrite.
const DRIVE_PATH = /^[A-Za-z]:\//
const inWindowsSpelling = (folder: string): string => (DRIVE_PATH.test(folder) ? folder.split('/').join('\\') : folder)

async function askAgentToMove($: EngineInterface, folder: string): Promise<void> {
  const answer = await $.prompt.submit({ text: `Move this chat to ${inWindowsSpelling(folder)}: call the change_directory tool with that path, and do nothing else.`, asUser: true })
  if (answer.drop !== undefined) throw new Error(answer.drop || 'the chat did not take the request')
}

// Moves this chat to the folder the active session's work is in, as /cd does when the person types it. The desktop app
// moves the chat only after the agent's turn ends, so the band is read again once the chat is there, not before.
export async function followSession($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  await checkChatFolder($, chatBar)
  const { expected, isElsewhere } = await currentChatFolder($)
  if (!isElsewhere) return
  const asked = await moveChatTo($, expected)
  if (!asked) return
  $.ui.toast(`Moving this chat to ${expected}${chatBar.sessionName ? `, for ${chatBar.sessionName}` : ''}`)
  if (!(await arrivedIn($, expected, asked))) await reportLateMove($, expected)
  await checkChatFolder($, chatBar)
}
